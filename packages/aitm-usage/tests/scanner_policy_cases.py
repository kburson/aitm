"""Run scanner policy on in-memory transcript bytes and explicit custody."""

from contextlib import nullcontext
from importlib import import_module
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from aitm_usage.monitor_registry import _ServiceEvidence
from aitm_usage.types import Registration

scanner = import_module("aitm_usage.sources.scan")


class ScannerPolicy:
    checkout = Path("/fixture/checkout")
    root = Path("/fixture/transcripts")
    path = root / "source.jsonl"
    identity = ((1, 2), (1, 3))

    def __init__(self, monkeypatch, project_id, cutoff):
        self.monkeypatch = monkeypatch
        self.cutoff = cutoff
        self.evidence = _ServiceEvidence(b"scanner-policy-test-fixture")
        self.registration = Registration(
            project_id, Path("/fixture/project"), (self.root,), (self.checkout,), cutoff
        )

    def scan(self, contents):
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
        candidate = scanner.CandidateSource(
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
        batch = scanner.scan(candidate, None, self.cutoff)
        if batch.cursor is not None:
            verify.assert_called_once()
        return batch
