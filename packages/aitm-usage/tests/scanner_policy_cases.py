"""Run scanner policy on in-memory transcript bytes and explicit custody."""

import json
from contextlib import nullcontext
from dataclasses import dataclass
from importlib import import_module
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

from aitm_usage.ledger import Ledger, LedgerIdentity
from aitm_usage.monitor_registry import _ServiceEvidence
from aitm_usage.types import (
    Eligibility,
    LedgerBatch,
    LedgerView,
    Registration,
    SourceCheckpoint,
)

scanner = import_module("aitm_usage.sources.scan")


class ScannerPolicy:
    checkout = Path("/fixture/checkout")
    root = Path("/fixture/transcripts")
    path = root / "source.jsonl"
    identity = ((1, 2), (1, 3))

    def __init__(self, monkeypatch, project_id, cutoff, *, evidence=None):
        self.monkeypatch = monkeypatch
        self.cutoff = cutoff
        self.evidence = (
            _ServiceEvidence(b"scanner-policy-test-fixture")
            if evidence is None
            else evidence
        )
        self.registration = Registration(
            project_id, Path("/fixture/project"), (self.root,), (self.checkout,), cutoff
        )

    def candidate(self, contents):
        origin = scanner._origin(BytesIO(contents), len(contents), self.evidence)
        assert origin is not None
        locator = scanner._locator_reference(self.evidence, self.path)
        stream_ref = (
            self.evidence.pseudonymize(
                f"{origin.provider.value}-stream", origin.session_ref.value
            )
            if origin.provider is not None and origin.session_ref is not None
            else locator
        )
        return scanner.CandidateSource(
            origin.provider,
            origin.session_ref,
            stream_ref,
            locator,
            scanner._incarnation_reference(self.evidence, self.identity[-1]),
            self.path,
            self.identity,
            self.registration,
            self.evidence,
            _native_surface=origin.native_surface,
        )

    def scan(self, contents, checkpoint=None, *, candidate=None):
        if candidate is None:
            candidate = self.candidate(contents)
        snapshot = SimpleNamespace(stat=SimpleNamespace(st_size=len(contents)))
        verify = Mock()

        def open_snapshot(path, *, identity_prefix):
            assert (path, identity_prefix) == (self.path, self.identity)
            return nullcontext((BytesIO(contents), snapshot))

        def checkout_anchor(path, source):
            assert source is candidate
            if path == self.checkout:
                return (scanner.checkout_anchor_reference(self.evidence, path), (1, 4))
            return None

        self.monkeypatch.setattr(
            scanner, "_within_source_roots", lambda source: source is candidate
        )
        self.monkeypatch.setattr(scanner, "_open_snapshot", open_snapshot)
        self.monkeypatch.setattr(scanner, "_checkout_anchor", checkout_anchor)
        self.monkeypatch.setattr(scanner, "_verify_snapshot", verify)
        batch = scanner.scan(candidate, checkpoint, self.cutoff)
        if batch.cursor is not None:
            verify.assert_called_once()
        return batch


@dataclass(frozen=True, slots=True)
class _ReplayEvidence(_ServiceEvidence):
    project_id: UUID
    history: list[LedgerView]
    root = Path("/fixture/project")

    @property
    def identity(self) -> LedgerIdentity:
        return LedgerIdentity(self.project_id, self.key_id)

    def as_of(self, sequence=None):
        return self.history[-1 if sequence is None else sequence]

    def apply(self, batch):
        prior = self.as_of()
        previous = prior.checkpoints[0] if prior.checkpoints else None
        assert batch.prior_checkpoint == previous
        assert batch.checkpoint is not None
        self.history.append(
            LedgerView(
                self.project_id,
                prior.sequence + 1,
                (*prior.revisions, *batch.revisions),
                (batch.checkpoint,),
            )
        )


class TranscriptReplay:
    """Use the same scanner and adapter policy with disk or in-memory inputs."""

    def __init__(self, request, monkeypatch, project_id, cutoff, *, durable):
        self._project_id = project_id
        self._cutoff = cutoff
        self._contents = b""
        self._policy = None
        if durable:
            (
                self.ledger,
                self._registration,
                self._path,
                self.checkout,
                self.outside,
            ) = request.getfixturevalue("project")
        else:
            self.ledger = _ReplayEvidence(
                b"native-replay-evidence",
                project_id,
                [LedgerView(project_id, 0, (), ())],
            )
            self._policy = ScannerPolicy(
                monkeypatch, project_id, cutoff, evidence=self.ledger
            )
            self.checkout = self._policy.checkout
            self.outside = Path("/fixture/outside")

    def write(self, rows, *, append=False):
        contents = b"".join((json.dumps(row) + "\n").encode() for row in rows)
        if self._policy is None:
            with self._path.open("ab" if append else "wb") as stream:
                stream.write(contents)
        else:
            self._contents = self._contents + contents if append else contents

    def candidate(self):
        if self._policy is None:
            (candidate,) = scanner.discover(self._registration)
            return candidate
        return self._policy.candidate(self._contents)

    def scan(self, candidate, prior=None):
        if self._policy is None:
            return scanner.scan(candidate, prior, self._cutoff)
        return self._policy.scan(self._contents, prior, candidate=candidate)

    def read(self, reader, candidate, state, prior=None):
        batch = self.scan(candidate, prior)
        return batch, reader(batch, state, Eligibility.ELIGIBLE)

    def commit(self, batch, result, *, revisions=None, prior=None):
        checkpoint = SourceCheckpoint(batch.cursor, result.provider_checkpoint)
        self.ledger.apply(
            LedgerBatch(
                revisions=result.revisions if revisions is None else revisions,
                checkpoint=checkpoint,
                prior_checkpoint=prior,
            )
        )
        return checkpoint

    def reopen(self):
        if self._policy is None:
            return Ledger.open(self.ledger.root, self._project_id)
        return self.ledger
