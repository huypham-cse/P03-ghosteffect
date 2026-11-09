"""Minimal host action boundary for Algorithm 1, separate from the GUI agent.

Write-ahead dispatch, durable one-read cache and calibrated Algorithm 1 recovery.
Without a matching measured certificate recovery is ASK. Synthetic fixtures
can be enabled only explicitly for code tests; they never become real labels.
"""
import hashlib
import json
from pathlib import Path
import secrets
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'artifact' / 'scripts'))
from ledger import Ledger
from calibration import load_store, canonical_sha
from recovery import Recovery

ALPHABET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'


def boot_epoch():
    # The primary host runtime is Linux. Do not reuse monotonic timestamps
    # across host reboot; wall time subtraction is not an equivalent clock.
    path=Path('/proc/sys/kernel/random/boot_id')
    return path.read_text().strip() if path.is_file() else None


def new_nonce():
    return 'gx:' + ''.join(secrets.choice(ALPHABET) for _ in range(6))


class HostController:
    def __init__(self, db_path, adb, journal):
        self.ledger = Ledger(str(db_path))
        self.adb, self.journal = adb, journal
        self.lock = threading.Lock()
        self.boot_epoch=boot_epoch()
        self.ledger.db.executescript('''
            CREATE TABLE IF NOT EXISTS recovery_sessions(
                effect_id TEXT, attempt INTEGER, certificate TEXT, domain TEXT,
                context TEXT, result TEXT, PRIMARY KEY(effect_id,attempt));
            CREATE TABLE IF NOT EXISTS probe_reads(
                effect_id TEXT, attempt INTEGER, family TEXT, view TEXT,
                status TEXT, value INTEGER, PRIMARY KEY(effect_id,attempt,family,view));
            CREATE TABLE IF NOT EXISTS effect_runtime(
                effect_id TEXT PRIMARY KEY, metadata TEXT);
        ''')

    def prepare(self, effect_id, workflow, step, package, description, history_xml,
                nonce_field='none', visible_opt_in=False, semantic_snapshot=None, app_version=None):
        if nonce_field not in ('none', 'private', 'visible'):
            raise ValueError('unknown nonce field policy')
        if nonce_field == 'visible' and not visible_opt_in:
            raise ValueError('counterparty-visible nonce requires per-app opt-in')
        # Reusing the same ID after a crash MUST retain its original nonce.
        old = self.ledger.db.execute('SELECT nonce FROM effects WHERE id=?', (effect_id,)).fetchone()
        nonce = old[0] if old else (new_nonce() if nonce_field != 'none' else '')
        if semantic_snapshot is not None:
            if semantic_snapshot.get('verdict')!='SNAPSHOT':
                raise ValueError('verified pre-tap history-item snapshot required')
            history_digest=canonical_sha(semantic_snapshot['snapshot'])
        else:
            history_digest = hashlib.sha256(history_xml).hexdigest()
        self.ledger.plan(effect_id, workflow, step, package, description, nonce, history_digest)
        metadata=dict(app_version=app_version,nonce_field=nonce_field,visible_opt_in=visible_opt_in,
                      semantic_snapshot=semantic_snapshot,boot_epoch=self.boot_epoch)
        encoded=json.dumps(metadata,sort_keys=True,allow_nan=False)
        previous=self.ledger.db.execute('SELECT metadata FROM effect_runtime WHERE effect_id=?',(effect_id,)).fetchone()
        if previous and previous[0]!=encoded:
            raise ValueError('prepared app/history/nonce policy changed for the same effect')
        self.ledger.db.execute('INSERT OR IGNORE INTO effect_runtime VALUES(?,?)',(effect_id,encoded))
        self.journal.emit('PREPARED', effect_id=effect_id, history_sha256=history_digest,
                          nonce_policy=nonce_field)
        # The app-specific driver must type/verify this field BEFORE dispatch.
        return nonce

    def dispatch(self, effect_id, package, x, y, context_guard=None):
        with self.lock:
            outstanding = self.ledger.candidates()
            if any(eid != effect_id for eid in outstanding):
                raise RuntimeError('resolve earlier effects before continuing the agent')
            if not self.adb.foreground().startswith(package + '/'):
                raise RuntimeError('foreground changed before commit dispatch')
            row = self.ledger.db.execute('SELECT app FROM effects WHERE id=?', (effect_id,)).fetchone()
            if row is None or row[0] != package:
                raise ValueError('effect/package identity mismatch')
            meta_row=self.ledger.db.execute('SELECT metadata FROM effect_runtime WHERE effect_id=?',(effect_id,)).fetchone()
            metadata=json.loads(meta_row[0]) if meta_row else {}
            # Production preparation has a pinned app version. Package alone
            # cannot distinguish a changed activity/account/conversation.
            guarded=metadata.get('app_version') is not None
            if guarded and (not callable(context_guard) or context_guard() is not True):
                raise RuntimeError('verified activity/account/window guard required before commit')
            self.ledger.issue(effect_id)  # returns only after SQLite COMMIT
            self.journal.emit('DURABLE_ISSUED', effect_id=effect_id)
            try:
                if guarded and context_guard() is not True:
                    raise RuntimeError('activity/account/window changed after durable issue')
                self.adb.tap(x, y)
                self.journal.emit('DISPATCH_RETURN', effect_id=effect_id,
                                  scope='adb accepted input; not an app/backend acknowledgement')
            except BaseException:
                # Dispatch may already have reached Android. ISSUED stays ambiguous.
                self.journal.emit('DISPATCH_UNCERTAIN', effect_id=effect_id)
                raise

    def recover(self, effect_id, certificate_path=None, domain=None, context=None,
                observer=None, allow_synthetic=False, now=time.monotonic, sleep=time.sleep):
        if effect_id not in self.ledger.candidates():
            raise ValueError('effect is not an unresolved candidate')
        if self.ledger.state(effect_id) == 'COMPENSATING':
            self.journal.emit('ASK_REQUIRED', effect_id=effect_id, reason='ambiguous_compensation')
            return dict(decision='ASK', reason='ambiguous_compensation')
        if certificate_path is None or observer is None:
            self.ledger.settle(effect_id, 'ASKED')
            self.journal.emit('ASK_REQUIRED', effect_id=effect_id, reason='no_validated_runtime_certificate')
            return dict(decision='ASK', reason='no_validated_runtime_certificate')
        attempt = self.ledger.db.execute('SELECT attempt FROM effects WHERE id=?',(effect_id,)).fetchone()[0]
        # A completed resolution cannot be retried with a different certificate,
        # new view samples, or a changed context until a new durable attempt.
        session = self.ledger.db.execute('SELECT certificate,domain,context,result FROM recovery_sessions WHERE effect_id=? AND attempt=?',
                                         (effect_id,attempt)).fetchone()
        if session and session[3]:
            prior = json.loads(session[3])
            if prior['decision'] != 'PENDING':
                return prior
        if self.ledger.state(effect_id) == 'ASKED':
            return dict(decision='ASK',reason='already_escalated')
        try:
            store = load_store(certificate_path,allow_synthetic=allow_synthetic)
            metadata_row=self.ledger.db.execute('SELECT metadata FROM effect_runtime WHERE effect_id=?',(effect_id,)).fetchone()
            metadata=json.loads(metadata_row[0]) if metadata_row else {}
            context=dict(context or {})
            snapshot=metadata.get('semantic_snapshot') or {}
            if snapshot.get('snapshot',{}).get('matches',0)>0:
                # Caller cannot turn VLM back on by forgetting a look-alike
                # already recorded durably before the commit tap.
                context['lookalike']=True
            if not allow_synthetic:
                if self.boot_epoch is None or context.get('clock_epoch')!=self.boot_epoch:
                    raise ValueError('current Linux boot identity required for monotonic recovery')
                if metadata.get('boot_epoch')!=self.boot_epoch:
                    raise ValueError('host reboot invalidated the saved recovery clock')
                if metadata.get('app_version')!=domain.get('app_version'):
                    raise ValueError('prepared app version does not match calibration')
                item=next((s for s in store['strata'] if s['domain']==domain),None)
                if item and 'digest' in item['families'] and not metadata.get('semantic_snapshot'):
                    raise ValueError('XML hash is not the paper history-item digest')
                if item and 'nonce' in item['families'] and metadata.get('nonce_field','none')=='none':
                    raise ValueError('nonce family unavailable for this prepared effect')
            encoded_domain = json.dumps(domain,sort_keys=True,allow_nan=False)
            encoded_context = json.dumps(context,sort_keys=True,allow_nan=False)
            if session and session[:3] != (store['content_sha256'],encoded_domain,encoded_context):
                raise ValueError('certificate/domain/clock changed during unresolved recovery')
            if not session:
                self.ledger.db.execute('INSERT INTO recovery_sessions VALUES(?,?,?,?,?,NULL)',
                                       (effect_id,attempt,store['content_sha256'],encoded_domain,encoded_context))
            cached = CachedObserver(self,observer,effect_id,attempt)
            result = Recovery(store,cached,now,sleep).resolve(domain,context)
        except (ValueError,KeyError,TypeError,OSError,RuntimeError) as exc:
            result = dict(decision='ASK',reason='invalid_certificate_or_observation',error_type=type(exc).__name__)
        target = {'ASK':'ASKED','PENDING':'PENDING','COMMITTED':'COMMITTED','RETRY':'ABSENT'}[result['decision']]
        # Both durable records commit together. If killed before this transaction,
        # probe STARTED markers survive and prevent obtaining extra noisy votes.
        with self.ledger._transaction():
            current = self.ledger.state(effect_id)
            if current != target:
                if target not in self.ledger.TRANSITIONS[current]:
                    raise ValueError('invalid recovery settlement')
                self.ledger.db.execute('UPDATE effects SET state=?,t_updated=? WHERE id=?',(target,time.time(),effect_id))
            self.ledger.db.execute('UPDATE recovery_sessions SET result=? WHERE effect_id=? AND attempt=?',
                                   (json.dumps(result,allow_nan=False),effect_id,attempt))
        self.journal.emit('RECOVERY_RESULT',effect_id=effect_id,attempt=attempt,
                          decision=result['decision'],reason=result['reason'])
        # RETRY is permission for dispatch(), which performs a fresh foreground
        # check and durable issue. No tap is injected inside this decision method.
        return result

    def close(self):
        self.ledger.close()


class CachedObserver:
    def __init__(self, controller, observer, effect_id, attempt):
        self.controller,self.observer,self.effect_id,self.attempt = controller,observer,effect_id,attempt

    def verify_context(self):
        return self.observer.verify_context()

    def read(self,family,view):
        db = self.controller.ledger.db
        key = (self.effect_id,self.attempt,family,view)
        # STARTED is durable BEFORE acquiring a noisy view. Crash after starting
        # but before persisting its answer yields BOT, not a second read.
        with self.controller.ledger._transaction():
            row = db.execute('SELECT status,value FROM probe_reads WHERE effect_id=? AND attempt=? AND family=? AND view=?',key).fetchone()
            if row:
                return row[1] if row[0]=='DONE' else None
            db.execute("INSERT INTO probe_reads VALUES(?,?,?,?,'STARTED',NULL)",key)
        value = self.observer.read(family,view)
        if value is not None and (type(value) is not int or value not in (0,1)):
            raise ValueError('invalid binary/BOT observation')
        db.execute("UPDATE probe_reads SET status='DONE',value=? WHERE effect_id=? AND attempt=? AND family=? AND view=?",(value,*key))
        return value

    def monitor(self):
        return self.observer.monitor()  # Monitor is intentionally repeated/fallible per §5

