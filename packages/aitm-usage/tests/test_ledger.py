import importlib
import json
import os
import select
import shutil
import sqlite3
import stat
import subprocess
import sys
from contextlib import closing, contextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from importlib.util import find_spec
from pathlib import Path
from uuid import UUID

import pytest

PROJECT = UUID("586c8e13-1c17-42a4-84cf-d2802fa312df")
OTHER_PROJECT = UUID("31b124f7-10b8-421d-9c76-74555f86435d")
NOW = datetime(2026, 11, 9, 14, 0, tzinfo=UTC)
CANARY = "/private/transcripts/raw-provider-handle-canary"
ROOT_PREFIX = "Library/Application Support/aitm-usage"
REAL_HOME = Path.home()


@pytest.fixture(autouse=True)
def isolated_control_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir(mode=0o700)
    monkeypatch.setenv("HOME", str(home))
    if find_spec("aitm_usage") is not None:
        from aitm_usage import ledger as ledger_module

        monkeypatch.setattr(
            ledger_module, "_control_root", lambda: control_directory(), raising=False
        )


def control_directory():
    return Path.home() / "Library" / "Application Support" / "aitm-usage-control"


@pytest.fixture
def modules():
    if find_spec("aitm_usage") is None:
        pytest.skip("The standalone aitm_usage package is absent")
    return importlib.import_module("aitm_usage.ledger"), importlib.import_module(
        "aitm_usage.types"
    )


@pytest.fixture
def state(tmp_path, modules):
    root = tmp_path / "project"
    ledger_module, types = modules
    return ledger_module.Ledger.initialize(root, PROJECT), types


def sample_batch(ledger, types):
    session = ledger.pseudonymize("session", CANARY)
    stream = ledger.pseudonymize("logical-stream", CANARY)
    epoch = ledger.pseudonymize("counter-epoch", CANARY)
    request = ledger.pseudonymize("request", CANARY)
    boundary = types.SourceBoundary(
        types.Provider.CODEX,
        stream,
        session,
        1,
        types.BoundaryKind.REQUEST,
        request,
        epoch,
    )
    tokens = types.TokenCounts(input_tokens=11, cached_input_tokens=2, output_tokens=5)
    observation = types.UsageObservation(
        boundary,
        NOW,
        "0.99.0",
        1,
        tokens,
        types.Availability.PARTIAL,
        request_ref=request,
    )
    revision = types.Revision(request, 1, observation)
    cursor = types.SourceCursor(
        stream,
        ledger.pseudonymize("file-locator", CANARY),
        ledger.pseudonymize("file-incarnation", CANARY),
        307,
        ledger.pseudonymize("validation-anchor", CANARY),
    )
    prefix = types.RequestPrefix(
        request, ledger.pseudonymize("message", CANARY), 1, tokens
    )
    provider = types.ProviderCheckpoint(
        types.Provider.CODEX,
        epoch_ref=epoch,
        ordinal=1,
        baseline=tokens,
        request_prefix=(prefix,),
        client_version=types.ClientVersion.CODEX_0_167_0_ALPHA_3_2,
        format_version=1,
    )
    return types.LedgerBatch((revision,), types.SourceCheckpoint(cursor, provider))


@contextmanager
def tamper(path):
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)
        yield conn


def test_atomic_cursor_and_revisions(tmp_path, monkeypatch):
    assert find_spec("aitm_usage") is not None, (
        "The standalone durable ledger is absent"
    )
    from aitm_usage import types
    from aitm_usage.ledger import ConflictError, Ledger

    ledger = Ledger.initialize(tmp_path / "project", PROJECT)
    batch = sample_batch(ledger, types)

    def fail_checkpoint(conn, sequence, proposed, *args, **kwargs):
        assert conn.execute(
            "SELECT revision FROM revisions WHERE sequence = ?", (sequence,)
        ).fetchall() == [(1,)]
        raise sqlite3.IntegrityError("checkpoint fault")

    from aitm_usage import ledger as ledger_module

    with monkeypatch.context() as inject:
        inject.setattr(ledger_module, "_append_checkpoint", fail_checkpoint)
        with pytest.raises(sqlite3.IntegrityError, match="checkpoint fault"):
            ledger.apply(batch)
    reopened = type(ledger).open(ledger.root, PROJECT)
    assert reopened.as_of().sequence == 0
    assert reopened.as_of().revisions == ()
    assert reopened.as_of().checkpoints == ()

    assert reopened.apply(batch) == 1
    assert reopened.apply(batch) == 1
    assert reopened.as_of(1).revisions == batch.revisions
    assert reopened.as_of(1).checkpoints == (batch.checkpoint,)
    assert reopened.as_of(0).revisions == ()
    assert reopened.as_of(0).checkpoints == ()

    revision = batch.revisions[0]
    final = replace(revision.record, availability=types.Availability.COMPLETE)
    changed = replace(batch, revisions=(replace(revision, record=final),))
    with pytest.raises(ConflictError):
        reopened.apply(changed)
    assert reopened.as_of().revisions == (revision,)
    assert reopened.as_of().checkpoints == (batch.checkpoint,)

    next_revision = replace(revision, revision=2, record=final)
    assert reopened.apply(types.LedgerBatch((next_revision,))) == 2
    assert reopened.as_of(1).current == (revision,)
    assert reopened.as_of(2).current == (next_revision,)
    assert reopened.as_of(2).revisions == (revision, next_revision)


def test_cursor_replay_never_rewinds_current_provider_state(state):
    from aitm_usage.ledger import ConflictError

    ledger, types = state
    first = sample_batch(ledger, types)
    assert ledger.apply(first) == 1
    second = types.SourceCheckpoint(
        replace(first.checkpoint.cursor, offset=412),
        replace(first.checkpoint.provider, ordinal=2, request_prefix=()),
    )
    assert (
        ledger.apply(
            types.LedgerBatch(checkpoint=second, prior_checkpoint=first.checkpoint)
        )
        == 2
    )
    with pytest.raises(ConflictError):
        ledger.apply(first)
    assert ledger.as_of().checkpoints == (second,)
    assert ledger.as_of(1).checkpoints == (first.checkpoint,)


def test_writer_refusal_read_snapshot_and_release_on_process_exit(state):
    from aitm_usage.ledger import WriterActive

    ledger, types = state
    batch = sample_batch(ledger, types)
    ledger.apply(batch)
    lock_before = ledger.lock_path.stat()
    with subprocess.Popen(
        [
            sys.executable,
            "-c",
            """import sys
from pathlib import Path
from uuid import UUID
from aitm_usage import ledger as ledger_module
from aitm_usage.ledger import Ledger
ledger_module._control_root = lambda: Path(sys.argv[3])
ledger = Ledger.open(Path(sys.argv[1]), UUID(sys.argv[2]))
with ledger.writer():
    print("writer ready", flush=True)
    sys.stdin.read()
""",
            str(ledger.root),
            str(PROJECT),
            str(control_directory()),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    ) as process:
        try:
            assert select.select([process.stdout], [], [], 10)[0], (
                "writer did not start"
            )
            assert process.stdout.readline().strip() == "writer ready"
            with pytest.raises(WriterActive, match="writer-active"):
                ledger.apply(types.LedgerBatch())
            read_ledger = type(ledger).open(ledger.root, PROJECT)
            assert read_ledger.as_of(1).revisions == batch.revisions
            with (
                read_ledger.reader() as src,
                closing(sqlite3.connect(":memory:")) as dest,
            ):
                assert src.execute("PRAGMA busy_timeout").fetchone() == (1000,)
                assert src.execute("PRAGMA journal_mode").fetchone() == ("wal",)
                with pytest.raises(sqlite3.OperationalError, match="readonly"):
                    src.execute("DELETE FROM revisions")
                src.backup(dest)
                assert dest.execute("SELECT count(*) FROM revisions").fetchone() == (1,)
        finally:
            process.kill()
            process.wait(timeout=10)
    with ledger.writer() as writer:
        assert writer.apply(types.LedgerBatch()) == 1
    assert ledger.lock_path.stat().st_ino == lock_before.st_ino


def test_open_refuses_missing_state_without_creating_it(tmp_path, modules):
    ledger_module, _ = modules
    root = tmp_path / "missing"
    with pytest.raises(ledger_module.LedgerError):
        ledger_module.Ledger.open(root, PROJECT)
    assert not root.exists()


def test_key_is_project_bound_and_pseudonyms_survive_restart(state, tmp_path):
    ledger, _ = state
    reopened = type(ledger).open(ledger.root, PROJECT)
    other = type(ledger).initialize(tmp_path / "other", OTHER_PROJECT)
    ref = ledger.pseudonymize("session", CANARY)
    assert reopened.pseudonymize("session", CANARY) == ref
    assert ledger.pseudonymize("request", CANARY) != ref
    assert other.pseudonymize("session", CANARY) != ref
    assert ledger.identity.key_id == reopened.identity.key_id
    assert ledger.identity.key_id != other.identity.key_id


def durable_data(ledger):
    return {
        path.relative_to(ledger.root): path.read_bytes()
        for path in ledger.root.rglob("*")
        if path.is_file() and not path.name.endswith("-shm")
    }


@pytest.mark.parametrize("damage", ["schema", "project", "key"])
def test_invalid_identity_refuses_before_durable_writes(state, tmp_path, damage):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    batch = sample_batch(ledger, types)
    assert ledger.apply(batch) == 1
    if damage == "schema":
        with tamper(ledger.database_path) as conn:
            conn.execute("PRAGMA user_version = 99")
    elif damage == "project":
        with pytest.raises(LedgerError):
            type(ledger).open(ledger.root, OTHER_PROJECT)
        with tamper(ledger.database_path) as conn:
            conn.execute("UPDATE identity SET project_id = ?", (str(OTHER_PROJECT),))
    else:
        replacement = type(ledger).initialize(tmp_path / "replacement", PROJECT)
        ledger.key_path.write_bytes(replacement.key_path.read_bytes())

    before = durable_data(ledger)
    with pytest.raises(LedgerError):
        type(ledger).open(ledger.root, PROJECT)
    with pytest.raises(LedgerError):
        type(ledger).initialize(ledger.root, PROJECT)
    with pytest.raises(LedgerError):
        ledger.apply(batch)
    assert durable_data(ledger) == before


def test_schema_tag_alone_does_not_allow_a_missing_table(state):
    from aitm_usage.ledger import LedgerError

    ledger, _ = state
    with tamper(ledger.database_path) as conn:
        conn.execute("ALTER TABLE checkpoints RENAME TO invalid_checkpoints")
    before = durable_data(ledger)
    with pytest.raises(LedgerError):
        type(ledger).open(ledger.root, PROJECT)
    assert durable_data(ledger) == before


def test_held_writer_checks_key_identity_before_each_batch(state, tmp_path):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    replacement = type(ledger).initialize(tmp_path / "replacement", PROJECT)
    with ledger.writer() as writer:
        ledger.key_path.write_bytes(replacement.key_path.read_bytes())
        before = durable_data(ledger)
        with pytest.raises(LedgerError):
            writer.apply(types.LedgerBatch())
        assert durable_data(ledger) == before


@pytest.mark.parametrize(
    "relative_path", ["project", "store", "database", "lock", "key", "wal", "shm"]
)
def test_private_paths_have_exact_modes_and_reject_looser_modes(state, relative_path):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    paths = {
        "project": ledger.root,
        "store": ledger.database_path.parent,
        "database": ledger.database_path,
        "lock": ledger.lock_path,
        "key": ledger.key_path,
        "wal": Path(str(ledger.database_path) + "-wal"),
        "shm": Path(str(ledger.database_path) + "-shm"),
    }
    path = paths[relative_path]
    assert stat.S_IMODE(path.stat().st_mode) == (0o700 if path.is_dir() else 0o600)
    path.chmod(0o755 if path.is_dir() else 0o644)
    with pytest.raises(LedgerError):
        type(ledger).open(ledger.root, PROJECT)
    with pytest.raises(LedgerError):
        ledger.apply(types.LedgerBatch())


@pytest.mark.parametrize("file", ["lock", "key", "database", "wal", "shm"])
def test_symlink_state_files_are_refused_without_touching_target(state, tmp_path, file):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    paths = {
        "lock": ledger.lock_path,
        "key": ledger.key_path,
        "database": ledger.database_path,
        "wal": Path(str(ledger.database_path) + "-wal"),
        "shm": Path(str(ledger.database_path) + "-shm"),
    }
    original = paths[file]
    target = tmp_path / "outside"
    original.rename(target)
    before = target.read_bytes()
    original.symlink_to(target)
    with pytest.raises(LedgerError):
        type(ledger).open(ledger.root, PROJECT)
    with pytest.raises(LedgerError):
        ledger.apply(types.LedgerBatch())
    assert target.read_bytes() == before


def test_symlink_state_root_and_hardlinked_private_key_are_refused(state, tmp_path):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    linked_root = tmp_path / "linked"
    linked_root.symlink_to(ledger.root, target_is_directory=True)
    with pytest.raises(LedgerError):
        type(ledger).open(linked_root, PROJECT)
    os.link(ledger.key_path, tmp_path / "copied-key")
    with pytest.raises(LedgerError):
        ledger.apply(types.LedgerBatch())


def test_closed_batch_rejects_raw_fields_before_write(state):
    ledger, types = state
    batch = sample_batch(ledger, types)
    record = batch.revisions[0]
    invalid = [
        replace(batch, revisions=(replace(record, record={"prompt": CANARY}),)),
        replace(
            batch,
            revisions=(
                replace(record, record=replace(record.record, request_ref=CANARY)),
            ),
        ),
        replace(
            batch,
            checkpoint=replace(
                batch.checkpoint,
                provider=replace(
                    batch.checkpoint.provider,
                    request_prefix=({"tool_arguments": CANARY},),
                ),
            ),
        ),
        replace(
            batch,
            checkpoint=replace(
                batch.checkpoint,
                cursor=replace(batch.checkpoint.cursor, anchor_ref=CANARY),
            ),
        ),
    ]
    for malformed in invalid:
        with pytest.raises((ValueError, TypeError)):
            ledger.apply(malformed)
        assert ledger.as_of().sequence == 0
    assert ledger.apply(batch) == 1
    assert ledger.as_of().checkpoints[0].provider.request_prefix
    for path in ledger.root.rglob("*"):
        if path.is_file() and path != ledger.key_path:
            assert CANARY.encode() not in path.read_bytes(), path.name


def test_marker_wire_allowlist_rejects_extra_or_raw_source_fields(state):
    ledger, types = state
    marker = types.ScopeMarker(
        UUID("e6b3d931-55f4-4edd-8ee0-f642dfd2404a"),
        types.Provider.CODEX,
        ledger.pseudonymize("session", CANARY),
        1,
        types.BoundaryKind.TURN,
        ledger.pseudonymize("turn", CANARY),
        NOW,
        types.ItemKey(types.ItemKind.ISSUE, 83),
        types.WorkPhase.PLANNING,
        ledger.pseudonymize("participant", CANARY),
        project_id=PROJECT,
        role=types.ReviewRole.XPR,
    )
    ledger.validate_marker(marker)
    data = types.encode_marker(marker)
    assert types.decode_marker(data) == marker
    assert CANARY.encode() not in data
    payload = json.loads(data)
    payload["tool_arguments"] = CANARY
    with pytest.raises(ValueError):
        types.decode_marker(json.dumps(payload).encode())
    with pytest.raises((ValueError, TypeError)):
        types.encode_marker(replace(marker, session_ref=CANARY))
    from aitm_usage.ledger import LedgerError

    other_project = replace(marker, project_id=OTHER_PROJECT)
    revision = types.Revision(
        ledger.pseudonymize("marker", str(marker.marker_id)), 1, other_project
    )
    with pytest.raises(LedgerError):
        ledger.apply(types.LedgerBatch((revision,)))
    assert ledger.as_of().sequence == 0


def test_installed_console_entry_uses_package_and_project_prefix(tmp_path):
    executable = Path(sys.executable).with_name("aitm-usage")
    assert executable.is_file(), "The standalone aitm-usage console script is absent"
    result = subprocess.run(
        [str(executable), "--project", str(tmp_path / "test-project"), "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.startswith("aitm-usage ")
    cli = importlib.import_module("aitm_usage.cli")
    assert cli.default_project_root(PROJECT) == Path.home() / ROOT_PREFIX / str(PROJECT)


def test_stale_expected_checkpoint_cannot_append_new_revision(state):
    from aitm_usage.ledger import ConflictError

    ledger, types = state
    batch = sample_batch(ledger, types)
    assert ledger.apply(batch) == 1
    novel = replace(batch.revisions[0], revision=2)
    before = durable_data(ledger)
    with pytest.raises(ConflictError):
        ledger.apply(replace(batch, revisions=(novel,)))
    assert ledger.as_of().revisions == batch.revisions
    assert durable_data(ledger) == before
    assert ledger.apply(batch) == 1
    assert (
        ledger.apply(
            replace(batch, revisions=(novel,), prior_checkpoint=batch.checkpoint)
        )
        == 2
    )


def test_schema_with_same_columns_without_constraints_is_refused(state):
    from aitm_usage.ledger import Ledger, LedgerError

    ledger, types = state
    with tamper(ledger.database_path) as conn:
        conn.execute("ALTER TABLE revisions RENAME TO revisions_original")
        conn.execute("CREATE TABLE revisions AS SELECT * FROM revisions_original")
        conn.execute("DROP TABLE revisions_original")
    before = durable_data(ledger)
    with pytest.raises(LedgerError):
        Ledger.open(ledger.root, PROJECT)
    with pytest.raises(LedgerError):
        ledger.apply(types.LedgerBatch())
    assert durable_data(ledger) == before


def drift_path(ledger, kind, *, clone_ancestor=False):
    if kind == "lock":
        ledger.lock_path.rename(ledger.root / "old.lock")
        ledger.lock_path.touch(mode=0o600)
    elif kind == "root":
        previous = ledger.root.with_name("previous-root")
        ledger.root.rename(previous)
        shutil.copytree(previous, ledger.root)
    else:
        parent = ledger.root.parent
        previous = parent.with_name("previous-ancestor")
        parent.rename(previous)
        parent.mkdir(mode=0o700)
        original = previous / ledger.root.name
        if clone_ancestor:
            shutil.copytree(original, ledger.root)
        else:
            original.rename(ledger.root)


def try_writer_in_other_process(root):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """import sys
from pathlib import Path
from uuid import UUID
from aitm_usage import ledger as ledger_module
from aitm_usage.ledger import Ledger, WriterActive
ledger_module._control_root = lambda: Path(sys.argv[3])
ledger = Ledger.open(Path(sys.argv[1]), UUID(sys.argv[2]))
try:
    with ledger.writer():
        print("second writer admitted")
except WriterActive:
    print("writer-active")
""",
            str(root),
            str(PROJECT),
            str(control_directory()),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout.strip()


@pytest.mark.parametrize("kind", ["lock", "root", "ancestor"])
def test_uuid_guard_refuses_second_process_after_state_path_drift(
    tmp_path, modules, kind
):
    ledger_module, _ = modules
    ledger = ledger_module.Ledger.initialize(tmp_path / "parent" / "project", PROJECT)
    with ledger.writer():
        drift_path(ledger, kind, clone_ancestor=True)
        assert try_writer_in_other_process(ledger.root) == "writer-active"


@pytest.mark.parametrize("kind", ["lock", "root", "ancestor"])
def test_held_writer_refuses_changed_state_paths_before_write(tmp_path, modules, kind):
    ledger_module, types = modules
    ledger = ledger_module.Ledger.initialize(tmp_path / "parent" / "project", PROJECT)
    batch = sample_batch(ledger, types)
    with ledger.writer() as writer:
        drift_path(ledger, kind)
        before = durable_data(ledger)
        with pytest.raises(ledger_module.LedgerError):
            writer.apply(batch)
        assert durable_data(ledger) == before


def test_existing_state_refuses_missing_control_guard(state):
    from aitm_usage.ledger import LedgerError, project_guard

    ledger, _ = state
    with project_guard(ledger.root, PROJECT) as guard:
        path = guard.path
        assert not path.is_relative_to(ledger.root)
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        assert path.stat().st_uid == os.geteuid()
    path.unlink()
    with pytest.raises(LedgerError):
        type(ledger).open(ledger.root, PROJECT)
    with pytest.raises(LedgerError):
        type(ledger).initialize(ledger.root, PROJECT)
    assert not path.exists()


@pytest.mark.parametrize("destination", ["project", "guard"])
def test_inherited_macos_grant_refused_before_private_creation(
    tmp_path, modules, destination
):
    ledger_module, _ = modules
    parent = tmp_path / "grant" if destination == "project" else Path.home() / "Library"
    parent.mkdir(mode=0o700)
    subprocess.run(
        [
            "chmod",
            "+a",
            "everyone allow read,search,file_inherit,directory_inherit",
            parent,
        ],
        check=True,
        capture_output=True,
    )
    root = (parent if destination == "project" else tmp_path) / "project"
    with pytest.raises(ledger_module.LedgerError):
        ledger_module.Ledger.initialize(root, PROJECT)
    assert not root.exists()
    assert list(parent.iterdir()) == []


def test_real_mac_default_ancestry_allows_standard_deny_delete():
    from aitm_usage.ledger import validate_private_path

    base = REAL_HOME / "Library" / "Application Support"
    validate_private_path(
        base / "aitm-usage-u01-ancestry-probe", directory=True, allow_missing=True
    )


def test_private_path_rejects_mismatched_owner(state, monkeypatch):
    from aitm_usage.ledger import LedgerError, validate_private_path

    ledger, _ = state
    actual = ledger.key_path.stat().st_uid
    monkeypatch.setattr(os, "geteuid", lambda: actual + 1)
    with pytest.raises(LedgerError):
        validate_private_path(ledger.key_path)


@pytest.mark.parametrize("label", ["model", "client_version", "checkpoint_version"])
def test_raw_credential_shaped_metadata_is_normalized_before_durable_write(
    state, label
):
    ledger, types = state
    batch = sample_batch(ledger, types)
    canary = "sk-PRIVATE-CANARY" if label == "model" else "0.99.0-sk-PRIVATE-CANARY"
    if label == "checkpoint_version":
        checkpoint = batch.checkpoint
        batch = replace(
            batch,
            checkpoint=replace(
                checkpoint, provider=replace(checkpoint.provider, client_version=canary)
            ),
        )
    else:
        revision = batch.revisions[0]
        batch = replace(
            batch,
            revisions=(
                replace(revision, record=replace(revision.record, **{label: canary})),
            ),
        )
    assert ledger.apply(batch) == 1
    view = type(ledger).open(ledger.root, PROJECT).as_of()
    result = (
        view.checkpoints[0].provider.client_version
        if label == "checkpoint_version"
        else getattr(view.revisions[0].record, label)
    )
    assert result == "unknown"
    assert all(
        canary.encode() not in payload for payload in durable_data(ledger).values()
    )


@pytest.mark.parametrize("kind", ["foreign-project", "foreign-key", "fabricated"])
def test_authenticated_refusal_for_nested_pseudonyms(state, tmp_path, kind):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    batch = sample_batch(ledger, types)
    genuine = batch.checkpoint.cursor.anchor_ref
    if kind == "fabricated":
        prefix, digest, *proof = genuine.value.split(":")
        changed = ("0" if digest[0] != "0" else "1") + digest[1:]
        invalid = types.SourceRef(":".join((prefix, changed, *proof)))
    else:
        other_id = OTHER_PROJECT if kind == "foreign-project" else PROJECT
        other = type(ledger).initialize(tmp_path / "other", other_id)
        invalid = other.pseudonymize("validation-anchor", CANARY)
    batch = replace(
        batch,
        checkpoint=replace(
            batch.checkpoint,
            cursor=replace(batch.checkpoint.cursor, anchor_ref=invalid),
        ),
    )
    before = durable_data(ledger)
    with pytest.raises(LedgerError):
        ledger.apply(batch)
    assert durable_data(ledger) == before
    assert ledger.as_of().sequence == 0


def test_genuine_pseudonyms_and_project_identity_survive_reopen(state):
    ledger, types = state
    assert ledger.as_of(0).project_id == PROJECT
    batch = sample_batch(ledger, types)
    assert ledger.apply(batch) == 1
    reopened = type(ledger).open(ledger.root, PROJECT)
    assert reopened.as_of(1).project_id == PROJECT
    assert reopened.as_of(1).checkpoints == (batch.checkpoint,)
    reopened.validate_source_ref(batch.checkpoint.cursor.anchor_ref)


def quota_sample(ledger, types):
    return types.QuotaEvidence(
        provider=types.Provider.CODEX,
        account_ref=ledger.pseudonymize("codex-account", CANARY),
        bucket=types.QuotaBucket.SEVEN_DAY,
        observed_at=NOW,
        reset_at=NOW + timedelta(days=1),
        window_seconds=7 * 24 * 60 * 60,
        percent_milli=6050,
        precision=2,
        source=types.QuotaSource.CODEX_INLINE,
    )


def test_quota_envelope_roundtrips_only_account_window_evidence(state):
    ledger, types = state
    quota = quota_sample(ledger, types)
    result = types.AdapterResult(quota=(quota,))
    assert result.quota == (quota,)
    ledger.validate_quota(quota)
    encoded = types._encode(quota, types.QuotaEvidence)
    assert CANARY not in encoded
    assert types._decode(encoded, types.QuotaEvidence) == quota
    extra = json.loads(encoded)
    extra["task_burn"] = 17
    with pytest.raises(ValueError):
        types._decode(json.dumps(extra), types.QuotaEvidence)
    extra.pop("task_burn")
    extra["observed_at"] = NOW.astimezone(timezone(timedelta(hours=3))).isoformat()
    with pytest.raises(ValueError):
        types._decode(json.dumps(extra), types.QuotaEvidence)
    extra["observed_at"] = NOW.isoformat()
    extra["account_ref"] = CANARY
    with pytest.raises(ValueError):
        types._decode(json.dumps(extra), types.QuotaEvidence)


@pytest.mark.parametrize(
    "change",
    [
        {"percent_milli": 100_001},
        {"percent_milli": -1},
        {"precision": 4},
        {"precision": 1},
        {"observed_at": NOW.replace(tzinfo=None)},
        {"reset_at": NOW.astimezone(timezone(timedelta(hours=3)))},
        {"window_seconds": 0},
        {"bucket": "private-bucket-canary"},
        {"source": "tool_arguments"},
    ],
)
def test_quota_rejects_out_of_contract_scalar_values(state, change):
    ledger, types = state
    quota = quota_sample(ledger, types)
    with pytest.raises(ValueError):
        replace(quota, **change)


def test_quota_rejects_foreign_account_reference(state, tmp_path):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    quota = quota_sample(ledger, types)
    other = type(ledger).initialize(tmp_path / "other", OTHER_PROJECT)
    foreign = replace(quota, account_ref=other.pseudonymize("codex-account", CANARY))
    with pytest.raises(LedgerError):
        ledger.validate_quota(foreign)


def test_extended_grant_on_private_key_refused_before_read(state):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    subprocess.run(
        ["chmod", "+a", "everyone allow read", ledger.key_path],
        check=True,
        capture_output=True,
    )
    before = durable_data(ledger)
    with pytest.raises(LedgerError):
        type(ledger).open(ledger.root, PROJECT)
    with pytest.raises(LedgerError):
        ledger.apply(types.LedgerBatch())
    assert durable_data(ledger) == before


def test_control_location_cannot_be_inside_project_state(tmp_path, modules):
    ledger_module, _ = modules
    root = control_directory().parent
    with pytest.raises(ledger_module.LedgerError):
        ledger_module.Ledger.initialize(root, PROJECT)
    assert not root.exists()


def test_distinct_project_can_write_while_first_uuid_guard_held(state, tmp_path):
    ledger, types = state
    with ledger.writer():
        other = type(ledger).initialize(tmp_path / "other", OTHER_PROJECT)
        assert other.apply(sample_batch(other, types)) == 1


def test_control_location_rejects_case_alias_of_project_state(modules):
    ledger_module, _ = modules
    root = control_directory().with_name("AITM-USAGE-CONTROL")
    with pytest.raises(ledger_module.LedgerError):
        ledger_module.Ledger.initialize(root, PROJECT)
    assert not root.exists()


def test_source_proof_also_requires_exact_wire_shape(state):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    genuine = ledger.pseudonymize("request", CANARY)
    _, digest, tag = genuine.value.split(":")
    invalid = object.__new__(types.SourceRef)
    object.__setattr__(invalid, "value", f"private-shape-canary:{digest}:{tag}")
    with pytest.raises(LedgerError):
        ledger.validate_source_ref(invalid)


def data_volume_alias(path):
    return Path("/System/Volumes/Data") / path.relative_to("/")


@pytest.mark.parametrize("existing", [False, True], ids=["missing", "existing"])
@pytest.mark.parametrize(
    "relation", ["equal", "control-inside-state", "state-inside-control"]
)
def test_apfs_firmlink_overlap_refused_before_private_creation(
    modules, existing, relation
):
    ledger_module, _ = modules
    control = control_directory()
    physical_project = {
        "equal": control,
        "control-inside-state": control.parent,
        "state-inside-control": control / "project",
    }[relation]
    project = data_volume_alias(physical_project)
    assert Path.home().samefile(data_volume_alias(Path.home()))
    assert project.resolve() != physical_project.resolve()
    if existing:
        for path in sorted(
            {control, physical_project}, key=lambda item: len(item.parts)
        ):
            path.mkdir(mode=0o700, parents=True, exist_ok=True)
        assert project.samefile(physical_project)

    with pytest.raises(
        ledger_module.LedgerError, match="Writer guard must be outside project state"
    ):
        ledger_module.Ledger.initialize(project, PROJECT)

    assert project.exists() == control.exists() == existing
    assert not list(Path.home().rglob("*.lock"))
    assert not list(Path.home().rglob("pseudonym.key"))
    assert not list(Path.home().rglob("usage.sqlite3"))


def test_distinct_apfs_alias_cannot_admit_a_second_writer(tmp_path, modules):
    ledger_module, _ = modules
    root = tmp_path / "project"
    ledger = ledger_module.Ledger.initialize(root, PROJECT)
    alias = data_volume_alias(root)
    assert alias.samefile(root)
    assert ledger_module.Ledger.open(alias, PROJECT).identity == ledger.identity
    with ledger.writer():
        assert try_writer_in_other_process(alias) == "writer-active"
