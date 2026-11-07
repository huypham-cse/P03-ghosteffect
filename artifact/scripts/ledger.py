#!/usr/bin/env python3
"""GhostEffect write-ahead effect ledger (stdlib sqlite3).

States: PLANNED -> ISSUED -> {COMMITTED, ABSENT, ASKED, PENDING_MONITOR}; ABSENT -> ISSUED on retry
(attempt+1, same nonce); COMMITTED -> COMPENSATING -> COMPENSATED.  Invariant (write-ahead):
the ISSUED row is committed (WAL, synchronous=FULL) *before* the commit tap is injected, by a
process that is not the agent.  This module is the ledger used by bench_ledger.py, which measures
append latency on the build host and checks the invariant under SIGKILL of the writer process.
"""
import os
import sqlite3
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS effects(
  id TEXT PRIMARY KEY, workflow TEXT, step INTEGER, app TEXT, descr TEXT,
  nonce TEXT, attempt INTEGER, state TEXT, digest TEXT, t_issued REAL, t_updated REAL);
CREATE INDEX IF NOT EXISTS effects_state ON effects(state);
"""


class Ledger:
    def __init__(self, path, fullfsync=False):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=30)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        if fullfsync:  # macOS: F_FULLFSYNC (power-loss durability); off by default
            self.db.execute('PRAGMA fullfsync=ON')
        self.db.executescript(SCHEMA)

    def plan(self, eid, workflow, step, app, descr, nonce, digest=''):
        now = time.time()
        self.db.execute('INSERT OR REPLACE INTO effects VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                        (eid, workflow, step, app, descr, nonce, 0, 'PLANNED', digest, None, now))

    def issue(self, eid):
        """Durably mark ISSUED; returns only after the WAL commit (call before the commit tap)."""
        now = time.time()
        self.db.execute('BEGIN IMMEDIATE')
        self.db.execute("UPDATE effects SET state='ISSUED', attempt=attempt+1, t_issued=?, t_updated=? "
                        "WHERE id=?", (now, now, eid))
        self.db.execute('COMMIT')

    def settle(self, eid, state):
        self.db.execute('UPDATE effects SET state=?, t_updated=? WHERE id=?', (state, time.time(), eid))

    def candidates(self):
        """Ghost-effect candidates after a restart: every ISSUED record."""
        return [r[0] for r in self.db.execute("SELECT id FROM effects WHERE state='ISSUED' ORDER BY t_issued")]

    def state(self, eid):
        r = self.db.execute('SELECT state FROM effects WHERE id=?', (eid,)).fetchone()
        return r[0] if r else None

    def close(self):
        self.db.close()


def db_bytes(path):
    return sum(os.path.getsize(p) for p in (path, path + '-wal', path + '-shm') if os.path.exists(p))
