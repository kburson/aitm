"""Storage-edge doubles for the real delivery receipt and claim validators."""

from contextlib import contextmanager, nullcontext
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock

from journal_disposition_cases import _Rows
from test_monitor_journal import _ClaudeJournalRows

from aitm_usage import ledger as ledger_module
from aitm_usage import monitor_journal, monitor_writer
from aitm_usage.ledger import DELIVERY_SCHEMA_VERSION, Ledger
from aitm_usage.monitor_journal import _DELIVERY_ACK_ROWS, _DELIVERY_SCHEMA_VERSION
from aitm_usage.monitor_registry import _project


class DeliveryJournalRows(_ClaudeJournalRows):
    def __init__(self, evidence):
        super().__init__(evidence)
        self.acks = {}
        self.delivery_enabled = False

    def _current_version(self, connection):
        if self.delivery_enabled:
            assert connection is self
            return _DELIVERY_SCHEMA_VERSION
        return super()._current_version(connection)

    @contextmanager
    def transaction(self, *, write=False):
        acks = self.acks.copy()
        try:
            with super().transaction(write=write):
                yield self
        except Exception:
            self.acks = acks
            raise
        if not write:
            assert self.acks == acks

    def execute(self, sql, parameters=()):
        if sql.startswith(
            "SELECT s.sequence,s.payload,c.sequence FROM paired_settlements s"
        ):
            return _Rows()
        if sql.startswith(
            "SELECT c.project,c.payload,c.digest,c.sequence FROM claims c"
        ):
            (key,) = parameters
            if key not in self.claims:
                return _Rows()
            project, digest, payload, sequence = self.claims[key]
            return _Rows(
                [(project, payload, digest, sequence)]
                if sequence in self.commits
                else []
            )
        if sql == "SELECT 1 FROM commits WHERE sequence=?":
            (sequence,) = parameters
            return _Rows([(1,)] if sequence in self.commits else [])
        if sql.startswith("SELECT c.key,c.sequence,d.sequence,d.payload FROM claims c"):
            (project,) = parameters
            return _Rows(
                (key, sequence, None, None)
                for key, (owner, _, _, sequence) in self.claims.items()
                if owner == project
            )
        if sql == "SELECT DISTINCT destination_key FROM delivery_acks WHERE project=?":
            (project,) = parameters
            return _Rows(
                sorted({(row[1],) for row in self.acks.values() if row[0] == project})
            )
        if (
            sql
            == _DELIVERY_ACK_ROWS + " WHERE (a.project,a.claim_key,a.revision)=(?,?,?)"
        ):
            saved = self.acks.get(parameters)
            return SimpleNamespace(
                fetchall=lambda: [saved] if saved is not None else []
            )
        if sql.startswith("INSERT INTO delivery_acks ("):
            project, _, key, revision, claim, ack, _, _ = parameters
            assert {claim, ack} <= self.commits
            identity = project, key, revision
            assert identity not in self.acks
            self.acks[identity] = (*parameters, ack, claim)
            return _Rows()
        return super().execute(sql, parameters)


def delivery_journal_rows(monkeypatch, registry):
    with registry.writer() as writer:
        rows = DeliveryJournalRows(writer.source_evidence())

    def open_rows(writer):
        assert (
            writer.root == registry.root and writer.source_evidence() == rows.evidence
        )
        return rows

    monkeypatch.setattr(monitor_journal, "JournalStore", open_rows)
    return rows


class DestinationRows:
    def __init__(self):
        self.commits = set()
        self.revisions = {}
        self.receipts = {}

    def execute(self, sql, parameters=()):
        if sql == "SELECT COALESCE(MAX(sequence), 0) FROM commits":
            return _Rows([(max(self.commits, default=0),)])
        if sql.startswith(
            ("SELECT payload FROM revisions", "SELECT c.payload FROM checkpoints")
        ):
            return _Rows()
        if sql.startswith("SELECT key, revision, payload FROM monitor_revisions"):
            (cutoff,) = parameters
            return _Rows(
                (key, revision, payload)
                for (key, revision), (sequence, payload) in self.revisions.items()
                if sequence <= cutoff
            )
        if sql.startswith(
            "SELECT m.sequence,m.payload,c.sequence,r.sequence,r.payload,r.seal"
        ):
            record = self.revisions.get(parameters)
            if record is None:
                return _Rows()
            sequence, payload = record
            receipt = self.receipts.get(parameters, (None, None, None))
            committed = sequence if sequence in self.commits else None
            return _Rows([(sequence, payload, committed, *receipt)])
        if sql == "SELECT 1 FROM monitor_delivery_receipts WHERE (key,revision)=(?,?)":
            return _Rows([(1,)] if parameters in self.receipts else [])
        if sql == "SELECT 1 FROM monitor_revisions WHERE key=? AND revision>? LIMIT 1":
            key, revision = parameters
            return _Rows(
                [(1,)]
                if any(k == key and n > revision for k, n in self.revisions)
                else []
            )
        if sql == "INSERT INTO commits(sequence) VALUES (?)":
            (sequence,) = parameters
            assert sequence not in self.commits
            self.commits.add(sequence)
            return _Rows()
        if sql.startswith("INSERT INTO monitor_revisions("):
            key, revision, sequence, payload = parameters
            assert sequence in self.commits and (key, revision) not in self.revisions
            self.revisions[key, revision] = sequence, payload
            return _Rows()
        if sql.startswith("INSERT INTO monitor_delivery_receipts("):
            key, revision, sequence, payload, seal = parameters
            assert self.revisions[key, revision][0] == sequence
            self.receipts[key, revision] = sequence, payload, seal
            return _Rows()
        assert sql == "PRAGMA foreign_key_check", sql
        return _Rows()


def delivery_destination(monkeypatch, journal, ledger):
    rows = DestinationRows()
    registered = _project(journal._writer.view(), ledger.identity.project_id)
    writer = replace(
        ledger,
        identity=replace(ledger.identity, schema_version=DELIVERY_SCHEMA_VERSION),
        _writer=rows,
        _write_paths=SimpleNamespace(files=((1, 11),), check=Mock()),
    )

    def read_key(root, project_id, expected):
        assert (root, project_id, expected) == (
            ledger.root,
            ledger.identity.project_id,
            (1, 11),
        )
        return ledger._key

    def location(path, *, private):
        assert path == str(ledger.root) and private
        return registered.state

    def transaction(actual):
        assert actual is writer
        return nullcontext(rows)

    monkeypatch.setattr(ledger_module, "_read_key", read_key)
    monkeypatch.setattr(monitor_writer, "_directory", location)
    monkeypatch.setattr(Ledger, "reader", transaction)
    monkeypatch.setattr(Ledger, "_write_transaction", transaction)
    return writer, rows
