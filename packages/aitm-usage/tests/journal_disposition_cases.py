"""Observe disposition transactions while storing only typed row data in memory."""

from contextlib import contextmanager

from aitm_usage import monitor_journal


class _Rows(list):
    def fetchone(self):
        return self[0] if self else None


class DispositionRows:
    def __init__(self, evidence):
        self.evidence = evidence
        self.commits = set()
        self.rows = {}
        self.writes = []

    @contextmanager
    def transaction(self, *, write=False):
        commits, rows = self.commits.copy(), self.rows.copy()
        try:
            yield self
        except Exception:
            self.commits, self.rows = commits, rows
            raise
        if not write:
            assert (self.commits, self.rows) == (commits, rows)

    def _current_version(self, connection):
        assert connection is self
        return 4

    def execute(self, sql, parameters=()):
        if sql == "SELECT coalesce(max(sequence), 0) FROM commits":
            return _Rows([(max(self.commits, default=0),)])
        if sql == "INSERT OR IGNORE INTO commits VALUES (?)":
            (sequence,) = parameters
            self.writes.append(sql)
            self.commits.add(sequence)
            return _Rows()
        if sql == "INSERT INTO route_dispositions VALUES (?, ?, ?, ?)":
            command, hold, sequence, payload = parameters
            self.writes.append(sql)
            assert command not in self.rows
            assert sequence in self.commits
            self.rows[command] = (command, hold, sequence, sequence, payload)
            return _Rows()
        if sql == "SELECT 1 FROM route_dispositions WHERE hold = ?":
            (hold,) = parameters
            return _Rows(
                [(1,)] if any(row[1] == hold for row in self.rows.values()) else []
            )
        if sql == monitor_journal._DISPOSITION_ROWS + " WHERE d.command = ?":
            (command,) = parameters
            return _Rows([self.rows[command]] if command in self.rows else [])
        if sql.startswith(monitor_journal._DISPOSITION_ROWS + " WHERE d.sequence <= ?"):
            (limit,) = parameters
            return _Rows(row for row in self.rows.values() if row[2] <= limit)
        if sql.startswith(
            (
                "SELECT key,project,payload,digest,sequence FROM claims",
                "SELECT key, contender, evidence, sequence FROM disputes",
                "SELECT d.key,c.project,c.payload,c.digest,d.sequence,d.payload FROM content_disputes",
            )
        ):
            return _Rows()
        raise AssertionError(f"Unexpected disposition query {sql!r}")
