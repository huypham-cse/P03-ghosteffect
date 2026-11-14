"""GhostEffect at the M3A action boundary for the guarded arm of the agent study.

agent_episode.py --guard ghosteffect calls this module and nothing else changes: same prompt, model,
task, fault and grading as the baseline arm.
 - Before a classified commit tap (classifier.py lexicon on the element the action targets) the effect
   is planned and durably ISSUED in a host SQLite ledger (controller.py), then the native tap runs.
   A second commit tap while the effect is still ISSUED (K-9's "Send and Delete" dialog) is the same
   effect and is not issued again.
 - After the agent is killed and K-9 force-stopped and relaunched, a fresh HostController reopens the
   ledger from disk and recover() resolves every unresolved effect. There is no runtime certificate
   for K-9 (no evidence family can certify it, Table realsim), so recovery asks.
 - A simulated user answers from the backend and errs when the freeze says so. Delivered: COMMITTED,
   the step is done and the agent is not restarted. Not delivered: ABSENT, retry is permitted and the
   agent restarts as in the baseline. No candidate (the classifier missed the tap): the agent restarts
   unguarded, and that miss stays in the data.
"""
import json
from xml.sax.saxutils import quoteattr

from classifier import classify, commit_slot_id
from controller import HostController

PACKAGE = 'com.fsck.k9'
COMMIT_KINDS = ('click', 'long_press', 'keyboard_enter')


def capture(elements, action):
    """(classifier action, XML) for the element the action targets: the M3A index, else the pixel."""
    def box(e):
        b = e.bbox_pixels
        return (int(b.x_min), int(b.y_min), int(b.x_max), int(b.y_max)) if b else None
    index = getattr(action, 'index', None)
    if action.action_type == 'keyboard_enter':
        return dict(action_type='keyboard_enter'), '<hierarchy/>'
    if index is not None:
        if not 0 <= int(index) < len(elements) or box(elements[int(index)]) is None:
            return dict(action_type=action.action_type), '<hierarchy/>'
        targets = [elements[int(index)]]
        left, top, right, bottom = box(targets[0])
        x, y = (left + right) // 2, (top + bottom) // 2
    else:
        x, y = getattr(action, 'x', None), getattr(action, 'y', None)
        targets = [e for e in elements if box(e) and x is not None and y is not None
                   and box(e)[0] <= x < box(e)[2] and box(e)[1] <= y < box(e)[3]]
    nodes = ''.join('<node bounds="[%d,%d][%d,%d]" text=%s content-desc=%s resource-id=%s/>' % (
        *box(e), quoteattr(e.text or ''), quoteattr(e.content_description or ''), quoteattr(e.resource_name or ''))
        for e in targets)
    return dict(action_type=action.action_type, x=x, y=y), '<hierarchy>%s</hierarchy>' % nodes


class Guard:
    def __init__(self, out, episode_id, goal_sha256, journal):
        self.db, self.journal = out / 'ledger.db', journal
        self.effect = commit_slot_id(episode_id, goal_sha256, 'send')
        self.episode_id = episode_id
        self.controller = HostController(self.db, None, journal)
        self.taps = []

    def before(self, action, elements, phase):
        """Called before every native action; issues the effect before a commit tap. Returns the record."""
        if action.action_type not in COMMIT_KINDS:
            return None
        verdict_action, xml = capture(elements, action)
        verdict = classify(verdict_action, xml)
        record = dict(phase=phase, action=verdict_action, commit_candidate=verdict['commit_candidate'],
                      reason=verdict['reason'], matched=verdict.get('matched_terms', []))
        if verdict['commit_candidate']:
            ledger = self.controller.ledger
            state = ledger.state(self.effect)
            if state is None:
                self.controller.prepare(self.effect, self.episode_id, 1, PACKAGE, 'send the task mail', xml.encode())
                state = 'PLANNED'
            if state in ('PLANNED', 'ABSENT'):
                ledger.issue(self.effect)   # returns after the SQLite commit, before the tap
                self.journal.emit('DURABLE_ISSUED', effect_id=self.effect, phase=phase)
                record['ledger'] = 'issued'
            elif state == 'ISSUED':
                record['ledger'] = 'same_effect'
            else:
                raise RuntimeError('commit tap on a %s effect' % state)
        self.taps.append(record)
        return record

    def restart(self, ask):
        """After the kill and relaunch: reopen the ledger, recover, ask. Returns the decision record."""
        self.controller.close()
        self.controller = HostController(self.db, None, self.journal)   # the host reopens the ledger from disk
        candidates = self.controller.ledger.candidates()
        if self.effect not in candidates:
            record = dict(decision='NO_CANDIDATE', state=self.controller.ledger.state(self.effect))
        else:
            result = self.controller.recover(self.effect)
            delivered = ask()
            self.controller.ledger.settle(self.effect, 'COMMITTED' if delivered else 'ABSENT')
            record = dict(decision=result['decision'], reason=result['reason'],
                          answer='delivered' if delivered else 'not_delivered',
                          state=self.controller.ledger.state(self.effect))
        self.journal.emit('GUARD_RESTART', **record)
        return record

    def close(self):
        self.controller.close()


def simulated_user(delivered_truth, user_error):
    """Answer to 'did the recipient get it?': the backend truth, flipped when the freeze drew an error."""
    if user_error not in (0, 1):
        raise ValueError('user_error must be 0 or 1')
    return bool(delivered_truth) != bool(user_error)


RULES_WAIT_S = 10.0   # the fixed wait of the paper's same-evidence rules (planner_sim.T_RULES_WAIT)


class Rules(Guard):
    """Same-evidence rule cascade (paper RQ3 'rules'; planner_sim.resolve_rules) on the same ledger and boundary.

    K-9 with a Sent folder: hop 1 is K-9's own Outbox listing, the end-to-end family is K-9's Sent list. The reads are
    exact (K-9's database), an upper bound on a perception-based reader. K-9 is not G2, so hop 1 gives no vote. After the
    fixed 10 s wait: the mail in the Sent list means done; absent means every family reads absent, so retry; no
    reading means ask (the simulated user as in the guarded arm).
    """

    def restart(self, ask, read_folders, sleep):
        self.controller.close()
        self.controller = HostController(self.db, None, self.journal)
        ledger = self.controller.ledger
        if self.effect not in ledger.candidates():
            record = dict(decision='NO_CANDIDATE', state=ledger.state(self.effect))
        else:
            hop1 = read_folders()
            sleep(RULES_WAIT_S)
            folders = read_folders()
            record = dict(hop1_folders=hop1, folders=folders)
            if folders is None:
                result = self.controller.recover(self.effect)
                delivered = ask()
                ledger.settle(self.effect, 'COMMITTED' if delivered else 'ABSENT')
                record.update(decision=result['decision'], reason='no_reading',
                              answer='delivered' if delivered else 'not_delivered')
            elif 'Sent' in folders:
                ledger.settle(self.effect, 'COMMITTED')
                record.update(decision='COMMITTED', reason='sent_list_shows_it')
            else:
                ledger.settle(self.effect, 'ABSENT')
                record.update(decision='RETRY', reason='every_family_reads_absent')
            record['state'] = ledger.state(self.effect)
        self.journal.emit('RULES_RESTART', **record)
        return record


if __name__ == '__main__':
    print(json.dumps(dict(module=__doc__.splitlines()[0])))
