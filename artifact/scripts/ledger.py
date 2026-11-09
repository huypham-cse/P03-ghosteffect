#!/usr/bin/env python3
"""GhostEffect write-ahead effect ledger (stdlib sqlite3).

States: PLANNED -> ISSUED -> {COMMITTED, ABSENT, ASKED, PENDING}; ABSENT -> ISSUED on retry
(attempt+1, same nonce); COMMITTED -> COMPENSATING -> COMPENSATED.  Invariant (write-ahead):
the ISSUED row is committed (WAL, synchronous=FULL) *before* the commit tap is injected, by a
process that is not the agent.  This module is the ledger used by bench_ledger.py, which measures
append latency on the build host and checks the invariant under SIGKILL of the writer process.
"""
import os
import sqlite3
import time
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS effects(
  id TEXT PRIMARY KEY, workflow TEXT, step INTEGER, app TEXT, descr TEXT,
  nonce TEXT, attempt INTEGER, state TEXT, digest TEXT, t_issued REAL, t_updated REAL);
CREATE INDEX IF NOT EXISTS effects_state ON effects(state);
"""


class Ledger:
    # PENDING_MONITOR is accepted when reading a legacy database, but new writes
    # use the paper's PENDING spelling. Settling never authorizes a dispatch.
    TRANSITIONS = {
        'PLANNED': set(),
        'ISSUED': {'COMMITTED', 'ABSENT', 'ASKED', 'PENDING'},
        'PENDING': {'COMMITTED', 'ABSENT', 'ASKED'},
        'ASKED': {'COMMITTED', 'ABSENT', 'PENDING'},
        'ABSENT': set(),
        'COMMITTED': {'COMPENSATING'},
        # An ambiguous compensation is ASKED on its own new effect record;
        # the original committed effect must never regain an ABSENT->ISSUED path.
        'COMPENSATING': {'COMPENSATED'},
        'COMPENSATED': set(),
    }

    def __init__(self, path, fullfsync=False):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=30)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        if fullfsync:  # macOS: F_FULLFSYNC (power-loss durability); off by default
            self.db.execute('PRAGMA fullfsync=ON')
        self.db.executescript(SCHEMA)

    @staticmethod
    def _canonical(state):
        return 'PENDING' if state == 'PENDING_MONITOR' else state

    @staticmethod
    def _check_id(eid):
        if not isinstance(eid, str) or not eid.strip():
            raise ValueError('effect id must be a nonempty string')

    @contextmanager
    def _transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise

    def plan(self, eid, workflow, step, app, descr, nonce, digest=''):
        """Insert once; replaying identical metadata cannot erase a settled effect."""
        self._check_id(eid)
        now = time.time()
        metadata = (workflow, step, app, descr, nonce, digest)
        with self._transaction():
            old = self.db.execute('SELECT workflow, step, app, descr, nonce, digest FROM effects WHERE id=?',
                                  (eid,)).fetchone()
            if old is not None:
                if old != metadata:
                    raise ValueError('effect id already exists with different metadata')
                return
            self.db.execute('INSERT INTO effects VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                            (eid, workflow, step, app, descr, nonce, 0, 'PLANNED', digest, None, now))

    def issue(self, eid):
        """Authorize one attempt, only from PLANNED or certified/user-resolved ABSENT.

        Return after the durable commit, before the caller dispatches its tap.
        An outstanding ISSUED/PENDING/ASKED effect cannot be issued again. The
        original t0 is retained across retries; t_updated records this attempt.
        """
        self._check_id(eid)
        now = time.time()
        with self._transaction():
            row = self.db.execute('SELECT state FROM effects WHERE id=?', (eid,)).fetchone()
            if row is None:
                raise KeyError(eid)
            if self._canonical(row[0]) not in ('PLANNED', 'ABSENT'):
                raise ValueError('cannot issue an outstanding or settled effect: ' + row[0])
            self.db.execute("UPDATE effects SET state='ISSUED', attempt=attempt+1, "
                            't_issued=COALESCE(t_issued, ?), t_updated=? WHERE id=?', (now, now, eid))

    def settle(self, eid, state):
        self._check_id(eid)
        state = self._canonical(state)
        if state not in self.TRANSITIONS or state in ('PLANNED', 'ISSUED'):
            raise ValueError('settle requires a known resolution state; dispatch uses issue()')
        with self._transaction():
            row = self.db.execute('SELECT state FROM effects WHERE id=?', (eid,)).fetchone()
            if row is None:
                raise KeyError(eid)
            current = self._canonical(row[0])
            if current == state:
                return
            if state not in self.TRANSITIONS.get(current, set()):
                raise ValueError('illegal ledger transition: ' + current + ' -> ' + state)
            self.db.execute('UPDATE effects SET state=?, t_updated=? WHERE id=?', (state, time.time(), eid))

    def candidates(self):
        """Unresolved records to reconcile after restart, never a retry permission."""
        return [r[0] for r in self.db.execute(
            "SELECT id FROM effects WHERE state IN ('ISSUED','PENDING','PENDING_MONITOR','ASKED','COMPENSATING') "
            'ORDER BY t_issued, id')]

    def state(self, eid):
        r = self.db.execute('SELECT state FROM effects WHERE id=?', (eid,)).fetchone()
        return self._canonical(r[0]) if r else None

    def close(self):
        self.db.close()


def db_bytes(path):
    return sum(os.path.getsize(p) for p in (path, path + '-wal', path + '-shm') if os.path.exists(p))
