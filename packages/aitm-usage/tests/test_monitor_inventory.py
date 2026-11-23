"""Admission inventory behavior on the existing native selected-read paths."""

import json
import os
import stat
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from shutil import copyfile
from time import time_ns
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from qualification_policy_cases import qualification_policy
from scanner_policy_cases import NativeTranscriptFiles
from test_codex import CUTOFF
from test_grok import FIXTURES, GROK_BINARY, SESSION
from test_monitor_adapters import _desktop
from test_monitor_journal import COPY, LIVE, A, NativeJournalFixture

from aitm_usage.ledger import LedgerError
from aitm_usage.monitor_journal import RoutingJournal
from aitm_usage.monitor_registry import (
    BoundaryUnavailable,
    CaptureChange,
    Registry,
    SourceApprovalRequest,
)
from aitm_usage.monitor_scope import ScopeState
from aitm_usage.sources.adapter import ProviderAdapter
from aitm_usage.sources.grok import GrokAdapter, GrokOrigin
from aitm_usage.sources.scan import _InventoryUnavailable, _OriginCache

source_scan = import_module("aitm_usage.sources.scan")

pytestmark = pytest.mark.usefixtures("legacy_monitor_qualification")


@pytest.fixture
def siblings(tmp_path, monkeypatch):
    native = NativeJournalFixture(tmp_path, monkeypatch, independent_copy=True)
    selected = native.locator(LIVE)
    parked = native.paths[LIVE].with_name("parked.jsonl")
    copyfile(native.paths[COPY], parked)
    monkeypatch.setattr(source_scan, "time_ns", lambda: time_ns() + 3_000_000_000)
    return native, selected, parked


@pytest.fixture
def inventory_policy(monkeypatch):
    authority = qualification_policy(monkeypatch, LIVE, CUTOFF)
    writer = authority.writer
    writer.lease.identities = ((1, 90),)
    files = NativeTranscriptFiles(monkeypatch)
    root = authority.locator._source._registration
    assert files.root == root.path
    files.write(files.root / "active.jsonl", _desktop(files.checkout))
    parked = files.root / "parked.jsonl"
    parked_rows = _desktop(files.checkout)
    parked_rows[0]["payload"]["id"] = str(UUID(int=2026))
    files.write(parked, parked_rows)
    stamp = 10_000_000_000
    case = SimpleNamespace(
        writer=writer,
        foreign=authority.foreign,
        root=root,
        parked=parked,
        stamp=stamp,
        now=stamp + source_scan._INVENTORY_TIMESTAMP_GRANULARITY_NS + 1,
        opened=[],
    )
    normal_snapshot = files._snapshot

    def snapshot(path):
        value = normal_snapshot(path)
        value.directory_ctimes = (stamp,)
        value.stat.st_mtime_ns = stamp
        value.stat.st_ctime_ns = stamp
        value.stat.st_nlink = 1
        value.stat.st_mode = stat.S_IFREG | 0o600
        return value

    def catalog(path, identity):
        assert path == files.root and identity == authority.approved.directory.identity
        return {
            path: source_scan._DirectoryCatalog(
                (identity,),
                (identity, stamp, stamp),
                {name: snapshot(name) for name in files.contents},
            )
        }

    def open_snapshot(path, **kwargs):
        case.opened.append(path)
        return files._open_snapshot(path, **kwargs)

    monkeypatch.setattr(files, "_snapshot", snapshot)
    monkeypatch.setattr(source_scan, "_probe", snapshot)
    monkeypatch.setattr(source_scan, "_open_snapshot", open_snapshot)
    monkeypatch.setattr(source_scan, "_complete_catalog", catalog)
    monkeypatch.setattr(source_scan, "_revalidate_catalog", Mock())
    monkeypatch.setattr(source_scan, "time_ns", lambda: case.now)
    return case


def test_current_catalog_matches_legacy_locator_fields_and_skips_parked_open(
    siblings, monkeypatch
):
    native, selected, parked = siblings
    original = source_scan._open_snapshot
    opened = []

    @contextmanager
    def opens(path, **kwargs):
        opened.append(path)
        with original(path, **kwargs) as result:
            yield result

    monkeypatch.setattr(source_scan, "_open_snapshot", opens)
    catalog_calls = []
    catalog = source_scan._complete_catalog

    def enumerate_root(root, identity):
        catalog_calls.append(root)
        return catalog(root, identity)

    monkeypatch.setattr(source_scan, "_complete_catalog", enumerate_root)
    cache = _OriginCache()
    change = CaptureChange(A, LIVE, True)
    with native.registry.writer() as writer:
        legacy = tuple(ProviderAdapter().discover(native.roots[LIVE]))
        with writer._inventory_cycle(cache) as inventory:
            current = tuple(
                ProviderAdapter()._inventory_discover(native.roots[LIVE], inventory)
            )
            assert len(current) == len(legacy) == 2
            for observed, expected in zip(current, legacy, strict=True):
                assert observed.stream_ref == expected.stream_ref
                for field in (
                    "_registration",
                    "_path",
                    "_identity",
                    "_native_surface",
                    "_ledger",
                ):
                    assert getattr(observed._source, field) == getattr(
                        expected._source, field
                    )
            first = writer._native_delta(
                writer.view(), change, selected, None, inventory=inventory
            )
        assert parked in opened
        assert catalog_calls == [native.paths[LIVE].parent]
        opened.clear()
        with writer._inventory_cycle(cache) as inventory:
            replay = writer._native_delta(
                writer.view(), change, selected, None, inventory=inventory
            )
        assert replay == first
        assert native.paths[LIVE] in opened
        assert parked not in opened

        # A rewrite changes the file fingerprint even when its path stays the same.
        parked.write_bytes(parked.read_bytes() + b"\n")
        opened.clear()
        with writer._inventory_cycle(cache) as inventory:
            replay = writer._native_delta(
                writer.view(), change, selected, None, inventory=inventory
            )
        assert replay == first
        assert parked in opened


def _run_inventory_audit(kind, tmp_path):
    result = subprocess.run(
        [sys.executable, __file__, kind, str(tmp_path)],  # noqa: S603
        capture_output=True,
        check=False,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_native_inventory_audits_actual_selected_route(tmp_path):
    traces = _run_inventory_audit("native", tmp_path)
    assert traces["baseline-parked"] == 1
    assert traces["unchanged-parked"] == 0
    assert traces["changed-parked"] == 1
    assert traces["selected-opens"] > 0


def _native_audit(tmp_path):
    from conftest import install_legacy_monitor_qualification

    with pytest.MonkeyPatch.context() as patch:
        install_legacy_monitor_qualification(patch, lambda: tmp_path)
        native = NativeJournalFixture(tmp_path, patch, independent_copy=True)
        selected = native.locator(LIVE)
        parked = native.paths[LIVE].with_name("parked.jsonl")
        copyfile(native.paths[COPY], parked)
        patch.setattr(source_scan, "time_ns", lambda: time_ns() + 3_000_000_000)
        seen = []
        observing = False

        def audit(event, arguments):
            if observing and event == "open":
                path, _, flags = arguments
                if (
                    isinstance(path, (str, bytes))
                    and not flags & os.O_DIRECTORY
                    and os.fsdecode(path).endswith(".jsonl")
                ):
                    seen.append(Path(os.fsdecode(path)).name)

        sys.addaudithook(audit)
        cache = _OriginCache()
        counts = {}
        with native.registry.writer() as writer:
            for state in ("baseline", "unchanged", "changed"):
                if state == "changed":
                    parked.write_bytes(parked.read_bytes() + b"\n")
                seen.clear()
                with writer._inventory_cycle(cache) as inventory:
                    observing = True
                    try:
                        writer._native_delta(
                            writer.view(),
                            CaptureChange(A, LIVE, True),
                            selected,
                            None,
                            inventory=inventory,
                        )
                    finally:
                        observing = False
                counts[f"{state}-parked"] = seen.count(parked.name)
                if state == "unchanged":
                    counts["selected-opens"] = seen.count(native.paths[LIVE].name)
        print(json.dumps(counts))


def _grok_audit(tmp_path):
    from conftest import install_legacy_monitor_qualification

    with pytest.MonkeyPatch.context() as patch:
        install_legacy_monitor_qualification(patch, lambda: tmp_path)
        native = NativeJournalFixture(tmp_path, patch, independent_copy=True)
        root = tmp_path / "grok"
        parked_id = "10000000-0000-4000-8000-000000000116"
        for session in (SESSION, parked_id):
            directory = root / session
            directory.mkdir(parents=True)
            (directory / "updates.jsonl").write_bytes(
                (FIXTURES / "updates.jsonl")
                .read_bytes()
                .replace(SESSION.encode(), session.encode())
            )
            (directory / "usage.json").write_bytes(
                (FIXTURES / "usage.json")
                .read_bytes()
                .replace(SESSION.encode(), session.encode())
            )
        witness_file = root / "origin-revision"
        witness_file.write_bytes(b"verified-origin-generation-1")
        selected, parked = (
            root / session / "updates.jsonl" for session in (SESSION, parked_id)
        )
        patch.setattr(source_scan, "time_ns", lambda: time_ns() + 3_000_000_000)
        source_id = UUID(int=6)
        configuration = replace(
            native.roots[LIVE], path=root, cutoff=datetime(2026, 1, 1, tzinfo=UTC)
        )
        seen = []
        observing = False

        def audit(event, arguments):
            if observing and event == "open":
                path, _, flags = arguments
                if isinstance(path, (bytes, str)) and not flags & os.O_DIRECTORY:
                    opened = os.fsdecode(path)
                    if opened.endswith("updates.jsonl"):
                        seen.append(opened)

        def verify_origin(path):
            session = path.parent.name
            with path.open("rb") as stream:
                if session.encode() not in stream.readline():
                    return None
            return GrokOrigin(
                session_id=session,
                system="Darwin",
                architecture="arm64",
                version="1.0.77",
                build="50ca579fa996",
                executable_digest=GROK_BINARY,
                format_version=1,
                lineage_id=session,
                incarnation=native.evidence.pseudonymize("grok-incarnation", session),
                checkout=None,
            )

        def witness_for(source_root):
            return source_root.evidence.pseudonymize(
                "grok-inventory-witness", sha256(witness_file.read_bytes()).hexdigest()
            )

        reader = GrokAdapter(verify_origin, inventory_witness=witness_for)
        locator = next(
            item
            for item in reader.discover(configuration)
            if item._source.path == selected
        )
        sys.addaudithook(audit)
        cache = _OriginCache()
        counts = {}
        with native.registry.writer() as writer:
            writer.approve_source(
                SourceApprovalRequest(
                    source_id,
                    "grok",
                    "grok-build-macos",
                    "Darwin",
                    "arm64",
                    "1.0.77",
                    1,
                    str(root),
                )
            )
            state = ScopeState(writer, grok_reader=reader)
            before = writer.view()
            for phase in ("baseline", "unchanged", "changed", "sideband"):
                if phase == "changed":
                    parked.write_bytes(parked.read_bytes() + b"\n")
                if phase == "sideband":
                    witness_file.write_bytes(b"verified-origin-generation-2")
                seen.clear()
                with writer._inventory_cycle(cache) as inventory:
                    observing = True
                    try:
                        batch = state.read_source(
                            source_id, locator, inventory=inventory
                        )
                    finally:
                        observing = False
                assert batch.observations and writer.view() == before
                assert batch._locator.stream_ref == locator.stream_ref
                assert (
                    batch._locator._source.snapshot.identity
                    == locator._source.snapshot.identity
                )
                assert batch._locator._source.path == locator._source.path
                assert batch._locator._source.origin == locator._source.origin
                assert batch._locator._source.root == locator._source.root
                counts[f"{phase}-parked"] = seen.count(str(parked))
                if phase == "unchanged":
                    counts["selected-verifier-opens"] = seen.count(str(selected))
                    counts["selected-native-opens"] = seen.count("updates.jsonl")

            opaque = ScopeState(writer, grok_reader=GrokAdapter(verify_origin))
            assert opaque.read_source(source_id, locator).observations
            with (
                writer._inventory_cycle(cache) as inventory,
                pytest.raises(LedgerError),
            ):
                opaque.read_source(source_id, locator, inventory=inventory)
        print(json.dumps(counts))


def test_grok_inventory_audits_active_route_and_sideband_renewal(tmp_path):
    traces = _run_inventory_audit("grok", tmp_path)
    assert traces["baseline-parked"] == 1
    assert traces["unchanged-parked"] == 0
    assert traces["changed-parked"] == 1
    assert traces["sideband-parked"] == 1
    assert traces["selected-verifier-opens"] == 1
    assert traces["selected-native-opens"] == 1


@pytest.mark.parametrize(
    "fault", ["duplicate", "hardlink", "symlink", "limit", "denied"]
)
def test_incomplete_or_ambiguous_catalog_refuses_selected_stream(
    siblings, monkeypatch, fault
):
    native, selected, parked = siblings
    active = native.paths[LIVE]
    if fault == "duplicate":
        copyfile(active, parked)
    elif fault == "hardlink":
        parked.unlink()
        os.link(active, parked)
    elif fault == "symlink":
        parked.unlink()
        parked.symlink_to(active)
    elif fault == "limit":
        monkeypatch.setattr(source_scan, "_INVENTORY_MAX_ENTRIES", 1)
    else:
        original = os.scandir
        root_inode = active.parent.stat().st_ino

        def denied(path):
            if isinstance(path, int) and os.fstat(path).st_ino == root_inode:
                raise PermissionError("injected inventory enumeration failure")
            return original(path)

        monkeypatch.setattr(source_scan.os, "scandir", denied)
    with (
        native.registry.writer() as writer,
        writer._inventory_cycle(_OriginCache()) as inventory,
    ):
        with pytest.raises(BoundaryUnavailable):
            writer._native_delta(
                writer.view(),
                CaptureChange(A, LIVE, True),
                selected,
                None,
                inventory=inventory,
            )


def test_metadata_inventory_rejects_changed_sibling_before_return_and_same_cycle_retry(
    siblings, monkeypatch
):
    native, selected, parked = siblings
    original = source_scan._revalidate_catalog
    cache = _OriginCache()

    def changed(catalog):
        monkeypatch.setattr(source_scan, "_revalidate_catalog", original)
        parked.write_bytes(parked.read_bytes() + b"\n")
        original(catalog)

    monkeypatch.setattr(source_scan, "_revalidate_catalog", changed)
    with (
        native.registry.writer() as writer,
        writer._inventory_cycle(cache) as inventory,
    ):
        for _ in range(2):
            with pytest.raises(BoundaryUnavailable):
                writer._current_candidate(
                    writer.view(), LIVE, selected, inventory=inventory
                )
        assert not cache._entries


def test_cache_renews_through_same_authority_and_rejects_closed_or_foreign_writer(
    inventory_policy, monkeypatch
):
    case = inventory_policy
    writer = case.writer
    adapter = ProviderAdapter()
    cache = _OriginCache()
    with writer._inventory_cycle(cache) as old:
        baseline = tuple(adapter._inventory_discover(case.root, old))
        assert len(baseline) == 2
        assert len(cache._entries) == 2
    assert case.parked in case.opened
    case.opened.clear()
    with pytest.raises(_InventoryUnavailable, match="expired"):
        old._require_writer(writer)

    reopened = Registry(writer.root, Mock(identities=writer.lease.identities))
    monkeypatch.setattr(reopened, "view", writer.view)
    monkeypatch.setattr(reopened, "source_evidence", writer.source_evidence)
    with reopened._inventory_cycle(cache) as current:
        with pytest.raises(_InventoryUnavailable, match="another writer"):
            old._require_writer(reopened)
        assert tuple(adapter._inventory_discover(case.root, current)) == baseline
    assert case.opened == []

    foreign = case.foreign
    empty = replace(writer.view(), sources=(), source_key_id=None)
    monkeypatch.setattr(foreign, "view", lambda: empty)
    with pytest.raises(BoundaryUnavailable, match="established"):
        with foreign._inventory_cycle(cache):
            pytest.fail("keyless inventory opened")
    assert foreign.view().source_key_id is None
    empty = replace(empty, source_key_id=foreign.source_evidence().key_id)
    with pytest.raises(_InventoryUnavailable, match="another inventory"):
        with foreign._inventory_cycle(cache):
            pytest.fail("foreign inventory opened")


def test_existing_journal_entry_uses_only_explicit_inventory_cycle(
    siblings, monkeypatch
):
    native, selected, parked = siblings
    opened = []
    original = source_scan._open_snapshot

    @contextmanager
    def tracked(path, **kwargs):
        opened.append(path)
        with original(path, **kwargs) as observed:
            yield observed

    monkeypatch.setattr(source_scan, "_open_snapshot", tracked)
    cache = _OriginCache()
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        with writer._inventory_cycle(cache):
            baseline = journal.prepare(LIVE, selected)
        assert baseline.candidates and parked in opened
        opened.clear()
        with writer._inventory_cycle(cache):
            current = journal.prepare(LIVE, selected)
            assert current.progress == baseline.progress
            with pytest.raises(BoundaryUnavailable, match="already active"):
                with writer._inventory_cycle(_OriginCache()):
                    pytest.fail("nested cycle entered")
        assert native.paths[LIVE] in opened and parked not in opened
        opened.clear()
        assert journal.prepare(LIVE, selected).progress == baseline.progress
        assert parked in opened


@pytest.mark.parametrize("age", [-1, 1_000_000])
def test_previously_cached_origin_reauthenticates_if_clock_is_racy_or_future(
    inventory_policy, age
):
    case = inventory_policy
    writer = case.writer
    cache = _OriginCache()
    adapter = ProviderAdapter()
    with writer._inventory_cycle(cache) as inventory:
        baseline = tuple(adapter._inventory_discover(case.root, inventory))
    assert case.parked in case.opened
    assert cache._entries
    case.now = case.stamp + age
    for _ in range(2):
        case.opened.clear()
        with writer._inventory_cycle(cache) as inventory:
            assert tuple(adapter._inventory_discover(case.root, inventory)) == baseline
        assert case.parked in case.opened


def test_replaced_approved_root_never_reuses_a_warm_origin(siblings):
    native, selected, parked = siblings
    root = parked.parent
    retired = root.with_name("retired-source-root")
    cache = _OriginCache()
    with native.registry.writer() as writer:
        with writer._inventory_cycle(cache) as inventory:
            writer._current_candidate(
                writer.view(), LIVE, selected, inventory=inventory
            )
        root.rename(retired)
        root.mkdir()
        for original in retired.iterdir():
            copyfile(original, root / original.name)
        with writer._inventory_cycle(cache) as inventory:
            with pytest.raises(LedgerError, match="identity changed"):
                writer._current_candidate(
                    writer.view(), LIVE, selected, inventory=inventory
                )


@pytest.mark.parametrize(
    "when", ["during-walk", "root-revalidation", "nested-revalidation"]
)
def test_superseded_directory_witness_holds_catalog_without_staging(
    siblings, monkeypatch, when
):
    native, selected, parked = siblings
    root = parked.parent
    nested = root / "nested"
    nested.mkdir()
    parked.rename(nested / parked.name)
    changed = root if when == "root-revalidation" else nested
    marker = changed / "membership-change"
    before = source_scan._directory_witness(changed.stat())

    if when == "during-walk":
        original = source_scan.os.scandir
        inode = changed.stat().st_ino

        @contextmanager
        def change_after_scan(directory):
            with original(directory) as entries:
                yield entries
            if isinstance(directory, int) and os.fstat(directory).st_ino == inode:
                monkeypatch.setattr(source_scan.os, "scandir", original)
                marker.touch()

        monkeypatch.setattr(source_scan.os, "scandir", change_after_scan)
    else:
        original_revalidate = source_scan._revalidate_catalog

        def change_before_revalidation(catalog):
            monkeypatch.setattr(source_scan, "_revalidate_catalog", original_revalidate)
            marker.touch()
            original_revalidate(catalog)

        monkeypatch.setattr(
            source_scan, "_revalidate_catalog", change_before_revalidation
        )

    cache = _OriginCache()
    with native.registry.writer() as writer:
        with writer._inventory_cycle(cache) as inventory:
            for _ in range(2):
                with pytest.raises(BoundaryUnavailable, match="Complete metadata"):
                    writer._current_candidate(
                        writer.view(), LIVE, selected, inventory=inventory
                    )
            assert marker.exists()
            assert source_scan._directory_witness(changed.stat()) != before
            assert not cache._entries
        with writer._inventory_cycle(cache) as refreshed:
            _, current = writer._current_candidate(
                writer.view(), LIVE, selected, inventory=refreshed
            )
            assert current.stream_ref == selected.stream_ref


def test_inventory_rechecks_root_identity_even_without_existing_registry_match(
    siblings,
):
    native, _, parked = siblings
    directory = parked.parent
    moved = directory.with_name("moved-approved")
    cache = _OriginCache()
    with native.registry.writer() as writer:
        with writer._inventory_cycle(cache) as inventory:
            directory.rename(moved)
            directory.mkdir()
            with pytest.raises(_InventoryUnavailable, match="Complete metadata"):
                tuple(
                    ProviderAdapter()._inventory_discover(native.roots[LIVE], inventory)
                )
            directory.rmdir()
            moved.rename(directory)
            with pytest.raises(_InventoryUnavailable, match="Complete metadata"):
                tuple(
                    ProviderAdapter()._inventory_discover(native.roots[LIVE], inventory)
                )
            assert not cache._entries
        with writer._inventory_cycle(cache) as inventory:
            assert (
                len(
                    tuple(
                        ProviderAdapter()._inventory_discover(
                            native.roots[LIVE], inventory
                        )
                    )
                )
                == 2
            )


def test_midcycle_key_identity_change_refuses_existing_writer_cache(
    inventory_policy, monkeypatch
):
    case = inventory_policy
    writer = case.writer
    adapter = ProviderAdapter()
    with writer._inventory_cycle(_OriginCache()) as current:
        assert tuple(adapter._inventory_discover(case.root, current))
        before = writer.view()
        assert before.source_key_id is not None
        successor = sha256(before.source_key_id.encode()).hexdigest()
        monkeypatch.setattr(
            writer, "view", lambda: replace(before, source_key_id=successor)
        )
        case.opened.clear()
        with pytest.raises(BoundaryUnavailable, match="authority changed"):
            tuple(adapter._inventory_discover(case.root, current))
        assert case.opened == []


if __name__ == "__main__":
    {"native": _native_audit, "grok": _grok_audit}[sys.argv[1]](Path(sys.argv[2]))
