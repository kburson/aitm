import errno
import importlib
import json
import os
import select
import shutil
import sqlite3
import stat
import subprocess
import sys
from contextlib import closing, contextmanager, nullcontext
from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from hashlib import sha256
from importlib.util import find_spec
from io import BytesIO
from itertools import count
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest

PROJECT = UUID("586c8e13-1c17-42a4-84cf-d2802fa312df")
OTHER_PROJECT = UUID("31b124f7-10b8-421d-9c76-74555f86435d")
NOW = datetime(2026, 11, 9, 14, 0, tzinfo=UTC)
CANARY = "/private/transcripts/raw-provider-handle-canary"
ROOT_PREFIX = "Library/Application Support/aitm-usage"


def _uses_path_metadata(request):
    name = request.node.originalname
    if name == "test_symlink_state_files_are_refused_without_touching_target":
        return request.node.callspec.id != "database"
    if name == "test_held_writer_refuses_changed_state_paths_before_write":
        return request.node.callspec.id != "ancestor"
    if name == "test_uuid_guard_refuses_second_process_after_state_path_drift":
        return request.node.callspec.id != "lock"
    return "ledger_path_metadata" in request.fixturenames


@pytest.fixture(autouse=True)
def isolated_control_home(request, monkeypatch):
    if "memory_state" in request.fixturenames or _uses_path_metadata(request):
        return
    tmp_path = request.getfixturevalue("tmp_path")
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


def _memory_ledger(ledger_module, project_id, key):
    return ledger_module.Ledger(
        Path("/fixture/project"),
        ledger_module.LedgerIdentity(project_id, sha256(key).hexdigest()),
        key,
    )


@pytest.fixture
def memory_state(modules, monkeypatch):
    ledger_module, types = modules
    ledger = _memory_ledger(ledger_module, PROJECT, b"a" * 32)
    writer = Mock(side_effect=AssertionError("invalid input reached the ledger writer"))
    monkeypatch.setattr(ledger_module.Ledger, "writer", writer)
    return ledger, types, writer


@pytest.fixture
def ledger_path_metadata(modules, monkeypatch):
    """Supply private-file observations without creating or opening disk state."""
    ledger_module, _ = modules
    uid = 501
    entries = {}
    links = {}
    inodes = count(1)

    class ObservedPath(type(Path())):
        def stat(self, *, follow_symlinks=True):
            name = str(self)
            try:
                return entries[links.get(name, name) if follow_symlinks else name]
            except KeyError:
                raise FileNotFoundError(
                    errno.ENOENT, "Test path is absent", self
                ) from None

        def lstat(self):
            return self.stat(follow_symlinks=False)

        def mkdir(self, *args, **kwargs):
            if str(self) in entries:
                raise FileExistsError(errno.EEXIST, "Test path already exists", self)
            pytest.fail(f"Ledger attempted to create {self} after invalid admission")

    def add_path(path, mode, *, owner=uid):
        entries[str(path)] = os.stat_result(
            (mode, next(inodes), 1, 1, owner, 0, 0, 0, 0, 0)
        )

    def add_directory(path):
        for directory in (*reversed(path.parents), path):
            if not directory.exists():
                add_path(directory, stat.S_IFDIR | 0o700)

    def alias_directory(alias, target):
        entries[str(alias)] = target.stat()

    def replace_with_link(path, target):
        entries[str(target)] = path.lstat()
        add_path(path, stat.S_IFLNK | 0o777)
        links[str(path)] = str(target)

    def lower_permissions(path, mode):
        info = path.stat()
        entries[str(path)] = os.stat_result(
            (stat.S_IFMT(info.st_mode) | mode, *info[1:])
        )

    def open_descriptor(path, flags, *_):
        assert not flags & os.O_CREAT, f"Ledger attempted to create {path}"
        if str(path) in links and flags & os.O_NOFOLLOW:
            raise OSError(errno.ELOOP, "Test path was opened without following links")
        return SimpleNamespace(path=path, status=path.stat())

    def unexpected_connection(*args, **kwargs):
        pytest.fail("Unsafe ledger path reached SQLite")

    monkeypatch.setattr(
        ledger_module,
        "os",
        SimpleNamespace(
            path=os.path,
            geteuid=lambda: uid,
            open=open_descriptor,
            fstat=lambda descriptor: descriptor.status,
            close=lambda _: None,
            O_RDONLY=os.O_RDONLY,
            O_RDWR=os.O_RDWR,
            O_DIRECTORY=os.O_DIRECTORY,
            O_NOFOLLOW=os.O_NOFOLLOW,
            O_NONBLOCK=os.O_NONBLOCK,
            O_CREAT=os.O_CREAT,
            O_EXCL=os.O_EXCL,
        ),
    )
    monkeypatch.setattr(
        ledger_module,
        "fcntl",
        SimpleNamespace(LOCK_EX=1, LOCK_NB=2, flock=lambda *_: None),
    )
    monkeypatch.setattr(
        ledger_module, "check_private_acl", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(ledger_module, "_connection", unexpected_connection)

    base = ObservedPath("/fixture")
    home = base / "home"
    control = home / "Library" / "Application Support" / "aitm-usage-control"
    add_directory(home)
    monkeypatch.setattr(ledger_module, "_control_root", lambda: control)
    return SimpleNamespace(
        base=base,
        home=home,
        control=control,
        add_path=add_path,
        add_directory=add_directory,
        alias_directory=alias_directory,
        replace_with_link=replace_with_link,
        lower_permissions=lower_permissions,
        entries=entries,
        uid=uid,
    )


@pytest.fixture
def path_metadata(request):
    if _uses_path_metadata(request):
        return request.getfixturevalue("ledger_path_metadata")
    return None


def _observe_storage(metadata, ledger):
    database = ledger.database_path
    metadata.add_directory(database.parent)
    metadata.add_directory(metadata.control)
    for path in (
        metadata.control / f"{ledger.identity.project_id}.lock",
        ledger.lock_path,
        ledger.key_path,
        database,
        database.with_name(database.name + "-wal"),
        database.with_name(database.name + "-shm"),
    ):
        metadata.add_path(path, stat.S_IFREG | 0o600)


def _observed_ledger(metadata, ledger_module):
    ledger = replace(
        _memory_ledger(ledger_module, PROJECT, b"a" * 32),
        root=metadata.base / "project",
    )
    _observe_storage(metadata, ledger)
    return ledger


def _storage_slots(ledger):
    database = ledger.database_path
    return {
        "project": ledger.root,
        "store": database.parent,
        "database": database,
        "lock": ledger.lock_path,
        "key": ledger.key_path,
        "wal": database.with_name(database.name + "-wal"),
        "shm": database.with_name(database.name + "-shm"),
    }


class _QueryRows(list):
    def fetchone(self):
        return self[0] if self else None


class _LedgerRows:
    """Adapt the ledger's SQL requests to observations of stored rows."""

    def __init__(self, identity, application_id, schema):
        self.version = identity.schema_version
        self.application_id = application_id
        self.schema = schema
        self.identity_row = (str(identity.project_id), identity.key_id)
        self.history = ([], [], [])
        self.writes = []

    def connect(self, *, write):
        return _LedgerConnection(self, write=write)


class _LedgerConnection:
    def __init__(self, store, *, write):
        self.store = store
        self.write = write

    def __enter__(self):
        self.history = tuple(rows.copy() for rows in self.store.history)
        return self

    def __exit__(self, error, *_):
        if error is None and self.write:
            self.store.history = self.history

    def rollback(self):
        self.history = tuple(rows.copy() for rows in self.store.history)

    def execute(self, statement, params=()):
        commits, revisions, checkpoints = self.history
        sql = " ".join(statement.split())
        headers = {
            "PRAGMA user_version": [(self.store.version,)],
            "PRAGMA application_id": [(self.store.application_id,)],
            "PRAGMA journal_mode": [("wal",)],
            "SELECT type, name, tbl_name, sql FROM sqlite_schema ORDER BY name": self.store.schema,
            "SELECT project_id, key_id FROM identity WHERE singleton = 1": [
                self.store.identity_row
            ],
        }
        if sql in headers:
            return _QueryRows(headers[sql])
        if sql == ("BEGIN IMMEDIATE" if self.write else "BEGIN"):
            return None
        if sql == "SELECT COALESCE(MAX(sequence), 0) FROM commits":
            return _QueryRows([(max((row[0] for row in commits), default=0),)])
        if sql == "SELECT payload FROM revisions WHERE key = ? AND revision = ?":
            return _QueryRows(
                (value,)
                for key, revision, _, value in revisions
                if (key, revision) == params
            )
        if (
            sql
            == "SELECT revision, payload FROM revisions WHERE key = ? ORDER BY revision DESC LIMIT 1"
        ):
            matching = [
                (revision, value)
                for key, revision, _, value in revisions
                if (key,) == params
            ]
            return _QueryRows([max(matching)] if matching else [])
        if (
            sql
            == "SELECT payload FROM checkpoints WHERE source_ref = ? ORDER BY sequence DESC LIMIT 1"
        ):
            matching = [
                (sequence, value)
                for source, sequence, value in checkpoints
                if (source,) == params
            ]
            return _QueryRows([(max(matching)[1],)] if matching else [])
        if (
            sql
            == "SELECT payload FROM revisions WHERE sequence <= ? ORDER BY sequence, key, revision"
        ):
            ordered = sorted(revisions, key=lambda row: (row[2], row[0], row[1]))
            return _QueryRows(
                (value,) for _, _, sequence, value in ordered if sequence <= params[0]
            )
        if sql == (
            "SELECT c.payload FROM checkpoints c JOIN ( SELECT source_ref, "
            "MAX(sequence) AS latest FROM checkpoints WHERE sequence <= ? "
            "GROUP BY source_ref ) h ON h.source_ref = c.source_ref "
            "AND h.latest = c.sequence ORDER BY c.source_ref"
        ):
            latest = {}
            for source, sequence, value in sorted(checkpoints):
                if sequence <= params[0]:
                    latest[source] = value
            return _QueryRows((latest[source],) for source in sorted(latest))
        destinations = {
            "INSERT INTO commits VALUES (?)": commits,
            "INSERT INTO revisions VALUES (?, ?, ?, ?)": revisions,
            "INSERT INTO checkpoints VALUES (?, ?, ?)": checkpoints,
        }
        assert self.write and sql in destinations, sql
        self.store.writes.append((sql, params))
        destinations[sql].append(params)
        return None


@pytest.fixture
def observe_ledger_rows(ledger_path_metadata, modules, monkeypatch):
    ledger_module, _ = modules
    keys = {}
    databases = {}

    class KeyBytes(BytesIO):
        def __init__(self, descriptor, payload):
            super().__init__(payload)
            self.descriptor = descriptor

        def fileno(self):
            return self.descriptor

    def open_key(descriptor, mode):
        assert mode == "rb"
        return KeyBytes(descriptor, keys[descriptor.path].key_bytes)

    definitions = {
        statement.strip().split()[2]: statement.strip()
        for statement in ledger_module._SCHEMA.split(";")
        if statement.strip().startswith("CREATE TABLE ")
    }
    schema = tuple(
        ("table", name, name, statement)
        for name, statement in sorted(definitions.items())
    )

    def observe(root, project_id, key):
        identity = ledger_module._identity(project_id, key)
        ledger = ledger_module.Ledger(root, identity, key)
        _observe_storage(ledger_path_metadata, ledger)
        rows = _LedgerRows(identity, ledger_module.APPLICATION_ID, schema)
        rows.key_bytes = project_id.bytes + key
        keys[ledger.key_path] = rows
        databases[ledger.database_path] = rows
        return rows

    def connection(path, *, write):
        return nullcontext(databases[path].connect(write=write))

    monkeypatch.setattr(ledger_module.os, "fdopen", open_key, raising=False)
    monkeypatch.setattr(ledger_module, "_supported_schema", lambda version: schema)
    monkeypatch.setattr(ledger_module, "_connection", connection)
    return observe


@pytest.fixture
def ledger_rows(ledger_path_metadata, modules, observe_ledger_rows):
    ledger_module, types = modules
    metadata = ledger_path_metadata
    root = metadata.base / "parent" / "project"
    rows = observe_ledger_rows(root, PROJECT, b"a" * 32)
    metadata.add_path(metadata.control / f"{OTHER_PROJECT}.lock", stat.S_IFREG | 0o600)
    return ledger_module.Ledger.open(root, PROJECT), types, rows


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
    _assert_real_private_creation_and_mode(ledger, types)
    secret_model = "sk-PRIVATE-CANARY"
    batch = _with_credential_shaped_metadata(
        sample_batch(ledger, types), "model", secret_model
    )
    with pytest.raises((ValueError, TypeError)):
        ledger.apply(_invalid_batch_variants(batch)[0])
    assert ledger.as_of().sequence == 0

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
    assert reopened.identity == ledger.identity
    session = reopened.pseudonymize("session", CANARY)
    assert session == ledger.pseudonymize("session", CANARY)
    assert session != reopened.pseudonymize("request", CANARY)
    assert reopened.as_of(0).project_id == PROJECT
    assert reopened.as_of().sequence == 0
    assert reopened.as_of().revisions == ()
    assert reopened.as_of().checkpoints == ()

    assert reopened.apply(batch) == 1
    assert reopened.apply(batch) == 1
    view = reopened.as_of(1)
    assert view.project_id == PROJECT
    assert view.revisions == batch.revisions
    assert view.checkpoints == (batch.checkpoint,)
    assert view.checkpoints[0].provider.request_prefix
    assert view.revisions[0].record.model == "unknown"
    assert view.revisions[0].record.client_version == "unknown"
    assert view.checkpoints[0].provider.client_version == "unknown"
    reopened.validate_source_ref(batch.checkpoint.cursor.anchor_ref)
    for path in reopened.root.rglob("*"):
        if path.is_file():
            payload = path.read_bytes()
            assert CANARY.encode() not in payload, path.name
            assert secret_model.encode() not in payload, path.name
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
    before = durable_data(reopened)
    with pytest.raises(ConflictError, match="Source checkpoint has changed"):
        reopened.apply(replace(batch, revisions=(next_revision,)))
    assert reopened.as_of().revisions == (revision,)
    assert durable_data(reopened) == before
    assert reopened.apply(types.LedgerBatch((next_revision,))) == 2
    assert reopened.as_of(1).current == (revision,)
    assert reopened.as_of(2).current == (next_revision,)
    assert reopened.as_of(2).revisions == (revision, next_revision)
    _assert_native_key_change_refuses_writer(reopened, types, batch)
    _assert_native_missing_constraints_refuses_store(reopened, types)


def test_cursor_replay_never_rewinds_current_provider_state(ledger_rows):
    from aitm_usage.ledger import ConflictError

    ledger, types, rows = ledger_rows
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
    before = rows.history
    with pytest.raises(ConflictError, match="Source checkpoint has changed"):
        ledger.apply(first)
    assert rows.history == before
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
from unittest.mock import Mock
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


def test_open_refuses_missing_state_without_creating_it(ledger_path_metadata, modules):
    ledger_module, _ = modules
    metadata = ledger_path_metadata
    metadata.add_directory(metadata.control)
    metadata.add_path(metadata.control / f"{PROJECT}.lock", stat.S_IFREG | 0o600)
    root = metadata.base / "missing"
    before = dict(metadata.entries)
    with pytest.raises(
        ledger_module.LedgerError, match="Private ledger path is unavailable"
    ):
        ledger_module.Ledger.open(root, PROJECT)
    assert not root.exists()
    with pytest.raises(
        ledger_module.LedgerError, match="Private ledger ancestry is unavailable"
    ):
        ledger_module.Ledger.open(root / "nested", PROJECT)
    assert not (root / "nested").exists()
    assert metadata.entries == before


def test_key_is_project_bound_and_pseudonyms_survive_restart(ledger_rows, modules):
    ledger, _, rows = ledger_rows
    ledger_module, _ = modules
    reopened = type(ledger).open(ledger.root, PROJECT)
    other_key = b"b" * 32
    other = type(ledger)(
        ledger.root.with_name("other"),
        ledger_module._identity(OTHER_PROJECT, other_key),
        other_key,
    )
    ref = ledger.pseudonymize("session", CANARY)
    assert reopened.pseudonymize("session", CANARY) == ref
    assert ledger.pseudonymize("request", CANARY) != ref
    assert other.pseudonymize("session", CANARY) != ref
    assert ledger.identity.key_id == reopened.identity.key_id
    assert ledger.identity.key_id != other.identity.key_id
    reused_key = replace(
        reopened, identity=replace(reopened.identity, project_id=OTHER_PROJECT)
    )
    assert rows.key_bytes.startswith(PROJECT.bytes)
    assert reused_key.pseudonymize("session", CANARY) != ref
    with pytest.raises(
        ledger_module.LedgerError, match="Source reference authentication failed"
    ):
        reused_key.validate_source_ref(ref)


def durable_data(ledger):
    return {
        path.relative_to(ledger.root): path.read_bytes()
        for path in ledger.root.rglob("*")
        if path.is_file() and not path.name.endswith("-shm")
    }


@pytest.mark.parametrize("damage", ["schema", "project", "key"])
def test_invalid_identity_refuses_before_durable_writes(ledger_rows, damage):
    from aitm_usage.ledger import LedgerError

    ledger, types, rows = ledger_rows
    batch = sample_batch(ledger, types)
    assert ledger.apply(batch) == 1
    message = "Ledger project or key identity mismatch"
    if damage == "schema":
        rows.version = 99
        message = "Unsupported ledger schema"
    elif damage == "project":
        with pytest.raises(
            LedgerError, match="Pseudonym key project identity mismatch"
        ):
            type(ledger).open(ledger.root, OTHER_PROJECT)
        rows.identity_row = (str(OTHER_PROJECT), rows.identity_row[1])
    else:
        rows.key_bytes = PROJECT.bytes + b"b" * 32

    before = rows.history
    rows.writes.clear()
    for operation in (
        lambda: type(ledger).open(ledger.root, PROJECT),
        lambda: type(ledger).initialize(ledger.root, PROJECT),
        lambda: ledger.apply(batch),
    ):
        with pytest.raises(LedgerError, match=message):
            operation()
    assert rows.history == before
    assert rows.writes == []


def test_schema_tag_alone_does_not_allow_a_missing_table(ledger_rows):
    from aitm_usage.ledger import LedgerError

    ledger, _, rows = ledger_rows
    rows.schema = tuple(row for row in rows.schema if row[1] != "checkpoints")
    before = rows.history
    with pytest.raises(LedgerError, match="Invalid ledger table schema"):
        type(ledger).open(ledger.root, PROJECT)
    assert rows.history == before
    assert rows.writes == []


def test_held_writer_checks_key_identity_before_each_batch(ledger_rows):
    from aitm_usage.ledger import LedgerError

    ledger, types, rows = ledger_rows
    batch = sample_batch(ledger, types)
    assert ledger.apply(batch) == 1
    before = rows.history
    rows.writes.clear()
    with ledger.writer() as writer:
        rows.key_bytes = PROJECT.bytes + b"b" * 32
        with pytest.raises(LedgerError, match="Ledger identity changed"):
            writer.apply(types.LedgerBatch())
        assert rows.history == before
    for operation in (
        lambda: type(ledger).open(ledger.root, PROJECT),
        lambda: type(ledger).initialize(ledger.root, PROJECT),
        lambda: ledger.apply(batch),
    ):
        with pytest.raises(
            LedgerError, match="Ledger project or key identity mismatch"
        ):
            operation()
    assert rows.history == before
    assert rows.writes == []


def _assert_native_key_change_refuses_writer(ledger, types, batch):
    from aitm_usage.ledger import LedgerError

    key = ledger.key_path
    original = key.read_bytes()
    identity = key.stat()
    changed = bytes([original[-1] ^ 1])
    try:
        with ledger.writer() as writer:
            key.write_bytes(original[:-1] + changed)
            assert os.path.samestat(identity, key.stat())
            before = durable_data(ledger)
            with pytest.raises(LedgerError, match="Ledger identity changed"):
                writer.apply(types.LedgerBatch())
            assert durable_data(ledger) == before
        for operation in (
            lambda: type(ledger).open(ledger.root, PROJECT),
            lambda: type(ledger).initialize(ledger.root, PROJECT),
            lambda: ledger.apply(batch),
        ):
            with pytest.raises(
                LedgerError, match="Ledger project or key identity mismatch"
            ):
                operation()
        assert durable_data(ledger) == before
    finally:
        key.write_bytes(original)


@pytest.mark.parametrize(
    "relative_path", ["project", "store", "database", "lock", "key", "wal", "shm"]
)
def test_private_paths_have_exact_modes_and_reject_looser_modes(
    ledger_path_metadata, modules, relative_path
):
    ledger_module, types = modules
    ledger = _observed_ledger(ledger_path_metadata, ledger_module)
    paths = _storage_slots(ledger)
    path = paths[relative_path]
    is_directory = relative_path in ("project", "store")
    assert stat.S_IMODE(path.stat().st_mode) == (0o700 if is_directory else 0o600)
    loose_mode = 0o755 if is_directory else 0o644
    ledger_path_metadata.lower_permissions(path, loose_mode)
    _assert_refuses_unsafe_storage_mode(ledger, types)


def _assert_refuses_unsafe_storage_mode(ledger, types):
    from aitm_usage.ledger import LedgerError

    with pytest.raises(LedgerError, match="Unsafe private ledger path"):
        type(ledger).open(ledger.root, PROJECT)
    with pytest.raises(LedgerError, match="Unsafe private ledger path"):
        ledger.apply(types.LedgerBatch())


def _assert_real_private_creation_and_mode(ledger, types):
    for name, created in _storage_slots(ledger).items():
        expected = 0o700 if name in {"project", "store"} else 0o600
        assert stat.S_IMODE(created.stat().st_mode) == expected
    guard = control_directory() / f"{PROJECT}.lock"
    assert stat.S_IMODE(guard.stat().st_mode) == 0o600
    assert guard.stat().st_uid == os.geteuid()
    ledger.root.chmod(0o755)
    try:
        _assert_refuses_unsafe_storage_mode(ledger, types)
    finally:
        ledger.root.chmod(0o700)


@pytest.mark.parametrize("file", ["lock", "key", "database", "wal", "shm"])
def test_symlink_state_files_are_refused_without_touching_target(
    request, modules, file, path_metadata
):
    from aitm_usage.ledger import LedgerError

    ledger_module, types = modules
    if path_metadata is not None:
        ledger = _observed_ledger(path_metadata, ledger_module)
        original = _storage_slots(ledger)[file]
        target = path_metadata.base / "outside"
        path_metadata.replace_with_link(original, target)
        assert original.stat() == target.lstat()
        before = dict(path_metadata.entries)
        with pytest.raises(LedgerError, match="Unsafe private ledger path"):
            type(ledger).open(ledger.root, PROJECT)
        with pytest.raises(LedgerError, match="Unsafe private ledger path"):
            ledger.apply(types.LedgerBatch())
        assert path_metadata.entries == before
        return

    ledger, _ = request.getfixturevalue("state")
    original = _storage_slots(ledger)[file]
    target = request.getfixturevalue("tmp_path") / "outside"
    original.rename(target)
    before = target.read_bytes()
    original.symlink_to(target)
    with pytest.raises(LedgerError):
        type(ledger).open(ledger.root, PROJECT)
    with pytest.raises(LedgerError):
        ledger.apply(types.LedgerBatch())
    assert target.read_bytes() == before
    original.unlink()
    target.rename(original)
    _assert_native_root_symlink_and_key_hardlink(
        ledger, types, request.getfixturevalue("tmp_path")
    )


def _assert_native_root_symlink_and_key_hardlink(ledger, types, tmp_path):
    from aitm_usage.ledger import LedgerError

    linked_root = tmp_path / "linked"
    linked_root.symlink_to(ledger.root, target_is_directory=True)
    with pytest.raises(LedgerError):
        type(ledger).open(linked_root, PROJECT)
    os.link(ledger.key_path, tmp_path / "copied-key")
    with pytest.raises(LedgerError):
        ledger.apply(types.LedgerBatch())


def test_symlink_state_root_and_hardlinked_private_key_are_refused(
    ledger_path_metadata, modules
):
    ledger_module, types = modules
    metadata = ledger_path_metadata
    ledger = _observed_ledger(metadata, ledger_module)
    linked_root = metadata.base / "linked"
    metadata.alias_directory(linked_root, ledger.root)
    metadata.replace_with_link(linked_root, ledger.root)
    with pytest.raises(ledger_module.LedgerError, match="Unsafe private ledger path"):
        ledger_module.Ledger.open(linked_root, PROJECT)
    key = ledger.key_path.lstat()
    metadata.entries[str(ledger.key_path)] = os.stat_result((*key[:3], 2, *key[4:]))
    with pytest.raises(ledger_module.LedgerError, match="Unsafe private ledger path"):
        ledger.apply(types.LedgerBatch())


def _invalid_batch_variants(batch):
    record = batch.revisions[0]
    return [
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


def test_closed_batch_rejects_raw_fields_before_write(memory_state):
    ledger, types, writer = memory_state
    for malformed in _invalid_batch_variants(sample_batch(ledger, types)):
        with pytest.raises((ValueError, TypeError)):
            ledger.apply(malformed)
    writer.assert_not_called()


def test_ledger_admission_and_real_commit_preserve_private_state(ledger_rows):
    ledger, types, rows = ledger_rows
    batch = sample_batch(ledger, types)
    with pytest.raises((ValueError, TypeError)):
        ledger.apply(_invalid_batch_variants(batch)[0])
    assert ledger.as_of().sequence == 0
    assert rows.writes == []
    assert ledger.apply(batch) == 1
    assert ledger.as_of().checkpoints[0].provider.request_prefix
    payloads = [entry[-1] for table in rows.history[1:] for entry in table]
    assert len(payloads) == 2
    assert all(CANARY not in payload for payload in payloads)


def test_marker_wire_allowlist_rejects_extra_or_raw_source_fields(memory_state):
    ledger, types, writer = memory_state
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
    writer.assert_not_called()


def test_installed_console_entry_uses_package_and_project_prefix(monkeypatch, capsys):
    cli = importlib.import_module("aitm_usage.cli")
    home = Path("/fixture/home")
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setattr(cli, "version", lambda _: "0.1.0")
    monkeypatch.setattr(
        sys, "argv", ["aitm-usage", "--project", "/fixture/test-project", "--version"]
    )
    with pytest.raises(SystemExit) as exit_:
        cli.main()
    assert exit_.value.code == 0
    assert capsys.readouterr().out == "aitm-usage 0.1.0\n"
    assert cli.default_project_root(PROJECT) == home / ROOT_PREFIX / str(PROJECT)


def test_stale_expected_checkpoint_cannot_append_new_revision(ledger_rows):
    from aitm_usage.ledger import ConflictError

    ledger, types, rows = ledger_rows
    batch = sample_batch(ledger, types)
    assert ledger.apply(batch) == 1
    novel = replace(batch.revisions[0], revision=2)
    before = rows.history
    rows.writes.clear()
    with pytest.raises(ConflictError, match="Source checkpoint has changed"):
        ledger.apply(replace(batch, revisions=(novel,)))
    assert ledger.as_of().revisions == batch.revisions
    assert rows.history == before
    assert [statement for statement, _ in rows.writes] == [
        "INSERT INTO commits VALUES (?)",
        "INSERT INTO revisions VALUES (?, ?, ?, ?)",
    ]
    assert ledger.apply(batch) == 1
    assert (
        ledger.apply(
            replace(batch, revisions=(novel,), prior_checkpoint=batch.checkpoint)
        )
        == 2
    )


def test_schema_with_same_columns_without_constraints_is_refused(ledger_rows):
    from aitm_usage.ledger import Ledger, LedgerError

    ledger, types, rows = ledger_rows
    rows.schema = tuple(
        (
            *row[:3],
            "CREATE TABLE revisions(key TEXT,revision INT,sequence INT,payload TEXT)",
        )
        if row[1] == "revisions"
        else row
        for row in rows.schema
    )
    before = rows.history
    with pytest.raises(LedgerError, match="Invalid ledger table schema"):
        Ledger.open(ledger.root, PROJECT)
    with pytest.raises(LedgerError, match="Invalid ledger table schema"):
        ledger.apply(types.LedgerBatch())
    assert rows.history == before
    assert rows.writes == []


def _assert_native_missing_constraints_refuses_store(ledger, types):
    from aitm_usage.ledger import Ledger, LedgerError

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


def _observe_path_replacement(metadata, ledger, kind, *, clone_ancestor=False):
    path = {
        "lock": ledger.lock_path,
        "root": ledger.root,
        "ancestor": ledger.root.parent,
    }[kind]
    if kind == "root" or clone_ancestor:
        for entry, info in metadata.entries.copy().items():
            if Path(entry).is_relative_to(path):
                metadata.add_path(entry, info.st_mode, owner=info.st_uid)
    else:
        metadata.add_path(path, path.lstat().st_mode)
    return path


def try_writer_in_other_process(root):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """import sys
from pathlib import Path
from unittest.mock import Mock
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
    request, modules, monkeypatch, kind, path_metadata
):
    ledger_module, _ = modules
    if path_metadata is not None:
        ledger, _, rows = request.getfixturevalue("ledger_rows")
        guard = path_metadata.control / f"{PROJECT}.lock"
        acquisitions = []
        held = set()

        def flock(descriptor, operation):
            assert (
                operation == ledger_module.fcntl.LOCK_EX | ledger_module.fcntl.LOCK_NB
            )
            identity = ledger_module._path_id(descriptor.status)
            acquisitions.append((descriptor.path, identity))
            if identity in held:
                raise BlockingIOError(errno.EAGAIN, "Writer lease already held")
            held.add(identity)

        monkeypatch.setattr(ledger_module.fcntl, "flock", flock)
        with ledger.writer():
            _observe_path_replacement(path_metadata, ledger, kind, clone_ancestor=True)
            contender = type(ledger).open(ledger.root, PROJECT)
            with pytest.raises(ledger_module.WriterActive, match="writer-active"):
                with contender.writer():
                    pytest.fail("Contender acquired a writer under a held UUID guard")
        assert [path for path, _ in acquisitions] == [guard, ledger.lock_path, guard]
        assert acquisitions[0] == acquisitions[-1]
        assert rows.writes == []
        return

    tmp_path = request.getfixturevalue("tmp_path")
    ledger = ledger_module.Ledger.initialize(tmp_path / "parent" / "project", PROJECT)
    with ledger.writer():
        drift_path(ledger, kind, clone_ancestor=True)
        assert try_writer_in_other_process(ledger.root) == "writer-active"


@pytest.mark.parametrize("kind", ["lock", "root", "ancestor"])
def test_held_writer_refuses_changed_state_paths_before_write(
    request, modules, kind, path_metadata
):
    ledger_module, types = modules
    if path_metadata is not None:
        ledger, types, rows = request.getfixturevalue("ledger_rows")
        batch = sample_batch(ledger, types)
        with ledger.writer() as writer:
            path = _observe_path_replacement(path_metadata, ledger, kind)
            (pin,) = (pin for pin in writer._write_paths.pinned if pin.path == path)
            assert not os.path.samestat(ledger_module.os.fstat(pin.fd), path.lstat())
            snapshot = rows.history
            with pytest.raises(
                ledger_module.LedgerError, match="Pinned private ledger path changed"
            ):
                writer.apply(batch)
        assert rows.history == snapshot
        assert rows.writes == []
        return

    tmp_path = request.getfixturevalue("tmp_path")
    ledger = ledger_module.Ledger.initialize(tmp_path / "parent" / "project", PROJECT)
    batch = sample_batch(ledger, types)
    with ledger.writer() as writer:
        drift_path(ledger, kind)
        before = durable_data(ledger)
        with pytest.raises(ledger_module.LedgerError):
            writer.apply(batch)
        assert durable_data(ledger) == before


def test_existing_state_refuses_missing_control_guard(ledger_path_metadata, modules):
    from aitm_usage.ledger import LedgerError, project_guard

    ledger_module, _ = modules
    metadata = ledger_path_metadata
    ledger = _observed_ledger(metadata, ledger_module)
    with project_guard(ledger.root, PROJECT) as guard:
        path = guard.path
        assert not path.is_relative_to(ledger.root)
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        assert path.stat().st_uid == metadata.uid
    del metadata.entries[str(path)]
    before = dict(metadata.entries)
    for operation in (type(ledger).open, type(ledger).initialize):
        with pytest.raises(LedgerError, match="Private ledger path is unavailable"):
            operation(ledger.root, PROJECT)
    assert not path.exists()
    assert metadata.entries == before


@pytest.mark.parametrize("destination", ["project", "guard"])
def test_inherited_macos_grant_refused_before_private_creation(
    modules, destination, monkeypatch, ledger_path_metadata, mac_acl_text
):
    from aitm_usage import host_fs

    ledger_module, _ = modules
    paths = ledger_path_metadata
    root = paths.base / "grant" / "project"
    parent = root.parent if destination == "project" else paths.control.parent.parent
    paths.add_directory(parent)
    monkeypatch.setattr(ledger_module, "check_private_acl", host_fs.check_private_acl)
    if sys.platform == "linux":

        def getxattr(path, name, *, follow_symlinks):
            assert not follow_symlinks
            if path == parent and name == "system.posix_acl_default":
                return b"test inherited ACL"
            raise OSError(errno.ENODATA, "No test ACL")

        monkeypatch.setattr(host_fs, "os", SimpleNamespace(getxattr=getxattr))
    else:
        mac_acl_text(
            parent,
            b"!#acl 1\ngroup:ABCDEFAB-CDEF-ABCD-EFAB-CDEF0000000C:everyone:12:allow:read\n",
        )

    before = paths.entries.copy()
    with pytest.raises(ledger_module.LedgerError, match="Unsafe private ACL"):
        ledger_module.Ledger.initialize(root, PROJECT)
    assert not root.exists()
    assert not (paths.control / f"{PROJECT}.lock").exists()
    assert paths.entries == before


def test_real_mac_default_ancestry_allows_standard_deny_delete(
    ledger_path_metadata, modules, monkeypatch, mac_acl_text
):
    from aitm_usage import host_fs
    from aitm_usage.ledger import LedgerError, validate_private_path

    ledger_module, _ = modules
    base = ledger_path_metadata.base / "private"
    ledger_path_metadata.add_directory(base)
    monkeypatch.setattr(ledger_module, "check_private_acl", host_fs.check_private_acl)
    mac_acl_text(
        base,
        b"!#acl 1\ngroup:ABCDEFAB-CDEF-ABCD-EFAB-CDEF0000000C:everyone:12:deny:delete\n",
    )
    monkeypatch.setattr(sys, "platform", "darwin")
    validate_private_path(base / "ancestry-probe", directory=True, allow_missing=True)
    with pytest.raises(LedgerError, match="Unsafe private ACL"):
        validate_private_path(base, directory=True)


def test_private_path_rejects_mismatched_owner(ledger_path_metadata):
    from aitm_usage.ledger import LedgerError, validate_private_path

    metadata = ledger_path_metadata
    path = metadata.base / "pseudonym.key"
    metadata.add_path(path, stat.S_IFREG | 0o600, owner=metadata.uid + 1)
    with pytest.raises(LedgerError, match="Unsafe private ledger path"):
        validate_private_path(path)
    metadata.add_path(path, stat.S_IFREG | 0o600)
    metadata.add_path(metadata.base, stat.S_IFDIR | 0o700, owner=metadata.uid + 1)
    with pytest.raises(LedgerError, match="Unsafe private ledger ancestry"):
        validate_private_path(path)


def _with_credential_shaped_metadata(batch, label, canary):
    checkpoint = batch.checkpoint
    if label == "checkpoint_version":
        return replace(
            batch,
            checkpoint=replace(
                checkpoint, provider=replace(checkpoint.provider, client_version=canary)
            ),
        )
    fields = {label: canary}
    if label == "model":
        version_canary = f"0.99.0-{canary}"
        fields["client_version"] = version_canary
        checkpoint = replace(
            checkpoint,
            provider=replace(checkpoint.provider, client_version=version_canary),
        )
    (revision,) = batch.revisions
    return replace(
        batch,
        revisions=(replace(revision, record=replace(revision.record, **fields)),),
        checkpoint=checkpoint,
    )


@pytest.mark.parametrize("label", ["model", "client_version", "checkpoint_version"])
def test_raw_credential_shaped_metadata_is_normalized_before_durable_write(
    ledger_rows, label
):
    ledger, types, rows = ledger_rows
    canary = "sk-PRIVATE-CANARY" if label == "model" else "0.99.0-sk-PRIVATE-CANARY"
    batch = _with_credential_shaped_metadata(sample_batch(ledger, types), label, canary)
    assert ledger.apply(batch) == 1
    view = type(ledger).open(ledger.root, PROJECT).as_of()
    result = (
        view.checkpoints[0].provider.client_version
        if label == "checkpoint_version"
        else getattr(view.revisions[0].record, label)
    )
    assert result == "unknown"
    if label == "model":
        assert view.revisions[0].record.client_version == "unknown"
        assert view.checkpoints[0].provider.client_version == "unknown"
    payloads = [entry[-1] for table in rows.history[1:] for entry in table]
    assert len(payloads) == 2
    assert all(canary not in payload for payload in payloads)


@pytest.mark.parametrize("kind", ["foreign-project", "foreign-key", "fabricated"])
def test_authenticated_refusal_for_nested_pseudonyms(memory_state, modules, kind):
    from aitm_usage.ledger import LedgerError

    ledger, types, writer = memory_state
    ledger_module, _ = modules
    batch = sample_batch(ledger, types)
    genuine = batch.checkpoint.cursor.anchor_ref
    if kind == "fabricated":
        prefix, digest, *proof = genuine.value.split(":")
        changed = ("0" if digest[0] != "0" else "1") + digest[1:]
        invalid = types.SourceRef(":".join((prefix, changed, *proof)))
    else:
        other_id = OTHER_PROJECT if kind == "foreign-project" else PROJECT
        other = _memory_ledger(ledger_module, other_id, b"b" * 32)
        invalid = other.pseudonymize("validation-anchor", CANARY)
    batch = replace(
        batch,
        checkpoint=replace(
            batch.checkpoint,
            cursor=replace(batch.checkpoint.cursor, anchor_ref=invalid),
        ),
    )
    with pytest.raises(LedgerError):
        ledger.apply(batch)
    writer.assert_not_called()


def test_genuine_pseudonyms_and_project_identity_survive_reopen(ledger_rows, modules):
    ledger_module, _ = modules
    ledger, types, rows = ledger_rows
    assert ledger.as_of(0).project_id == PROJECT
    batch = sample_batch(ledger, types)
    assert ledger.apply(batch) == 1
    reopened = type(ledger).open(ledger.root, PROJECT)
    assert reopened.as_of(1).project_id == PROJECT
    assert reopened.as_of(1).checkpoints == (batch.checkpoint,)
    reopened.validate_source_ref(batch.checkpoint.cursor.anchor_ref)
    other = _memory_ledger(ledger_module, OTHER_PROJECT, b"b" * 32)
    session = ledger.pseudonymize("session", CANARY)
    assert reopened.pseudonymize("session", CANARY) == session
    assert reopened.pseudonymize("request", CANARY) != session
    assert other.pseudonymize("session", CANARY) != session
    assert ledger.identity.key_id == reopened.identity.key_id
    assert ledger.identity.key_id != other.identity.key_id
    assert rows.key_bytes == PROJECT.bytes + ledger._key


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


def test_quota_envelope_roundtrips_only_account_window_evidence(memory_state):
    ledger, types, _ = memory_state
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
def test_quota_rejects_out_of_contract_scalar_values(memory_state, change):
    ledger, types, _ = memory_state
    quota = quota_sample(ledger, types)
    with pytest.raises(ValueError):
        replace(quota, **change)


def test_quota_rejects_foreign_account_reference(memory_state, modules):
    from aitm_usage.ledger import LedgerError

    ledger, types, _ = memory_state
    quota = quota_sample(ledger, types)
    ledger_module, _ = modules
    other = _memory_ledger(ledger_module, OTHER_PROJECT, b"b" * 32)
    foreign = replace(quota, account_ref=other.pseudonymize("codex-account", CANARY))
    with pytest.raises(LedgerError):
        ledger.validate_quota(foreign)


def test_extended_grant_on_private_key_refused_before_read(state, grant_extra_acl):
    from aitm_usage.ledger import LedgerError

    ledger, types = state
    grant_extra_acl(ledger.key_path, "system.posix_acl_access")
    before = durable_data(ledger)
    with pytest.raises(LedgerError, match="ACL"):
        type(ledger).open(ledger.root, PROJECT)
    with pytest.raises(LedgerError, match="ACL"):
        ledger.apply(types.LedgerBatch())
    assert durable_data(ledger) == before


def test_control_location_cannot_be_inside_project_state(modules, ledger_path_metadata):
    ledger_module, _ = modules
    root = ledger_path_metadata.control.parent
    with pytest.raises(
        ledger_module.LedgerError, match="Writer guard must be outside project state"
    ):
        ledger_module.Ledger.initialize(root, PROJECT)
    assert not root.exists()


def test_distinct_project_can_write_while_first_uuid_guard_held(
    ledger_rows, ledger_path_metadata, observe_ledger_rows, modules, monkeypatch
):
    ledger, types, first_rows = ledger_rows
    ledger_module, _ = modules
    metadata = ledger_path_metadata
    other_root = metadata.base / "other"
    other_rows = observe_ledger_rows(other_root, OTHER_PROJECT, b"b" * 32)
    first_guard = metadata.control / f"{PROJECT}.lock"
    other_guard = metadata.control / f"{OTHER_PROJECT}.lock"
    held = {}
    acquisitions = []

    def flock(descriptor, flags):
        assert flags == ledger_module.fcntl.LOCK_EX | ledger_module.fcntl.LOCK_NB
        identity = (descriptor.status.st_dev, descriptor.status.st_ino)
        if identity in held:
            raise BlockingIOError
        acquisitions.append((descriptor.path, tuple(pin.path for pin in held.values())))
        held[identity] = descriptor

    def close(descriptor):
        identity = (descriptor.status.st_dev, descriptor.status.st_ino)
        if held.get(identity) is descriptor:
            del held[identity]

    monkeypatch.setattr(ledger_module.fcntl, "flock", flock)
    monkeypatch.setattr(ledger_module.os, "close", close)
    with ledger.writer():
        other = type(ledger).initialize(other_root, OTHER_PROJECT)
        assert other.apply(sample_batch(other, types)) == 1
        assert other.identity.key_id != ledger.identity.key_id
        assert other.pseudonymize("session", CANARY) != ledger.pseudonymize(
            "session", CANARY
        )
        assert tuple(pin.path for pin in held.values()) == (
            first_guard,
            ledger.lock_path,
        )
    assert not held
    assert acquisitions == [
        (first_guard, ()),
        (ledger.lock_path, (first_guard,)),
        (other_guard, (first_guard, ledger.lock_path)),
        (other.lock_path, (first_guard, ledger.lock_path, other_guard)),
        (other_guard, (first_guard, ledger.lock_path)),
        (other.lock_path, (first_guard, ledger.lock_path, other_guard)),
    ]
    assert first_rows.history[0] == []
    assert other_rows.history[0] == [(1,)]


def test_control_location_rejects_case_alias_of_project_state(
    modules, ledger_path_metadata
):
    ledger_module, _ = modules
    root = ledger_path_metadata.control.with_name("AITM-USAGE-CONTROL")
    with pytest.raises(
        ledger_module.LedgerError, match="Writer guard must be outside project state"
    ):
        ledger_module.Ledger.initialize(root, PROJECT)
    assert not root.exists()


def test_source_proof_also_requires_exact_wire_shape(memory_state):
    from aitm_usage.ledger import LedgerError

    ledger, types, _ = memory_state
    genuine = ledger.pseudonymize("request", CANARY)
    _, digest, tag = genuine.value.split(":")
    invalid = object.__new__(types.SourceRef)
    object.__setattr__(invalid, "value", f"private-shape-canary:{digest}:{tag}")
    with pytest.raises(LedgerError):
        ledger.validate_source_ref(invalid)


@pytest.mark.parametrize("existing", [False, True], ids=["missing", "existing"])
@pytest.mark.parametrize(
    "relation", ["equal", "control-inside-state", "state-inside-control"]
)
def test_apfs_firmlink_overlap_refused_before_private_creation(
    modules, existing, relation, ledger_path_metadata
):
    ledger_module, _ = modules
    metadata = ledger_path_metadata
    home = metadata.home
    control = metadata.control
    alias = metadata.base / "alias"
    metadata.alias_directory(alias, home)
    project = {
        "equal": alias / control.relative_to(home),
        "control-inside-state": alias / control.parent.relative_to(home),
        "state-inside-control": alias / control.relative_to(home) / "project",
    }[relation]
    if existing:
        for path in (control, project):
            metadata.add_directory(path)
    before = dict(metadata.entries)

    with pytest.raises(
        ledger_module.LedgerError, match="Writer guard must be outside project state"
    ):
        ledger_module.Ledger.initialize(project, PROJECT)

    assert project.exists() == control.exists() == existing
    assert metadata.entries == before


def test_distinct_apfs_alias_cannot_admit_a_second_writer(
    tmp_path, modules, alias_directory_identity
):
    ledger_module, _ = modules
    root = tmp_path / "project"
    ledger = ledger_module.Ledger.initialize(root, PROJECT)
    identity = root.stat()
    with ledger.writer():
        other = ledger_module.Ledger.initialize(tmp_path / "other", OTHER_PROJECT)
        assert other.identity.key_id != ledger.identity.key_id
        alias = root.rename(tmp_path / "alias")
        try:
            assert os.path.samestat(alias.stat(), identity)
            assert ledger_module.Ledger.open(alias, PROJECT).identity == ledger.identity
            assert try_writer_in_other_process(alias) == "writer-active"
        finally:
            alias.rename(root)

    control = control_directory()
    overlap_alias = tmp_path / "overlap-alias"
    alias_directory_identity(overlap_alias, Path.home())
    overlapping = overlap_alias / control.parent.relative_to(Path.home())
    overlapping.mkdir(mode=0o700, parents=True)
    before = sorted(control.iterdir())
    with pytest.raises(
        ledger_module.LedgerError, match="Writer guard must be outside project state"
    ):
        ledger_module.Ledger.initialize(overlapping, OTHER_PROJECT)
    assert not list(overlapping.iterdir())
    assert sorted(control.iterdir()) == before
