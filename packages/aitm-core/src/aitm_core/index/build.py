"""Rebuild an index from one pinned tree without consulting a worktree."""

import sqlite3
from collections import defaultdict
from contextlib import closing
from dataclasses import dataclass
from os import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from aitm_core.documents import DocumentError, _parse
from aitm_core.events import core_reducers, fold
from aitm_core.models.events import validate_envelope
from aitm_core.models.evidence import OutcomeRecorded
from aitm_core.models.lifecycle import LifecycleState
from aitm_core.models.operations import story_event_path, story_scope
from aitm_core.reducers.evidence import EvidenceState
from aitm_core.store.backend import Snapshot
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.validation import _entries

from .schema import (
    DOCUMENT_TABLES,
    INDEX_VERSION,
    TABLES,
    IndexRow,
    initialize,
    open_index,
)

TABLE_BY_KIND = dict(zip(("story", "idea", "draft"), DOCUMENT_TABLES, strict=True))


@dataclass(frozen=True, slots=True)
class IndexView:
    snapshot: Snapshot
    repository: Repository
    database: Path


def _owner(path: str) -> str:
    story = story_scope(path)
    if story is not None:
        return f"story/{story}"
    if path.startswith(".aitm/ideas/") and path.endswith(".md"):
        return f"idea/{path}"
    if path.startswith(".aitm/drafts/") and path.endswith("/draft.md"):
        return f"draft/{path}"
    return f"file/{path}"


def _changed_owners(view: IndexView, previous: str, all_owners: set[str]) -> set[str]:
    if not previous:
        return all_owners
    repo = view.repository
    try:
        data = repo._git(
            "diff-tree",
            "-r",
            "--no-commit-id",
            "--name-only",
            "--no-renames",
            "-z",
            repo._oid(previous),
            view.snapshot.tree,
        )
    except (GitCommandError, ValueError):
        return all_owners
    return {_owner(path.decode()) for path in data.split(b"\0") if path}


def _story(
    owner: str, event_path: str, stream: bytes
) -> tuple[IndexRow | None, tuple[tuple[int, str], ...]]:
    records = tuple(validate_envelope(raw) for raw in stream.splitlines(keepends=True))
    story = fold(records, core_reducers())
    events = tuple(
        (sequence, record.model_dump_json(exclude_none=True))
        for sequence, record in sorted(
            {record.sequence: record for record in records}.items()
        )
    )
    lifecycle = story.domains.get("lifecycle")
    if not isinstance(lifecycle, LifecycleState):
        return None, events
    evidence = story.domains.get("evidence")
    lessons = ()
    if isinstance(evidence, EvidenceState):
        lessons = tuple(
            lesson
            for entry in evidence.facts.get("core.outcome.recorded", ())
            if isinstance(entry.payload, OutcomeRecorded)
            for lesson in entry.payload.lessons
        )
    description = lifecycle.description
    text = ""
    if description is not None:
        text = "\n".join(
            (
                description.actor,
                description.want,
                description.so_that,
                description.scope,
            )
        )
    return IndexRow(
        key=owner,
        kind="story",
        story_id=lifecycle.story_id,
        title=description.title if description else f"Story {lifecycle.story_id}",
        text=text,
        path=event_path,
        state=lifecycle.workflow_state.state_id,
        relationships=lifecycle.relationships,
        lessons=lessons,
    ), events


def _authored(owner: str, path: str, raw: bytes) -> IndexRow:
    kind = "idea" if owner.startswith("idea/") else "draft"
    title = None
    try:
        document = _parse(raw)
        candidate = document.header.get("title")
        if isinstance(candidate, str):
            title = candidate
        body = document.body.decode("utf-8")
    except DocumentError:
        body = raw.decode("utf-8")
    heading = next(
        (line[2:].strip() for line in body.splitlines() if line.startswith("# ")), None
    )
    return IndexRow(
        key=owner,
        kind=kind,
        title=title or heading or Path(path).stem,
        text=body,
        path=path,
    )


def _store(connection: sqlite3.Connection, view: IndexView) -> None:
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version != INDEX_VERSION:
        for table in TABLES:
            connection.execute(f"DROP TABLE IF EXISTS {table}")
    initialize(connection)
    old = connection.execute("SELECT tree FROM metadata WHERE singleton = 1").fetchone()
    if old and old[0] == view.snapshot.tree:
        return

    repo = view.repository
    files = _entries(repo, view.snapshot)
    groups = defaultdict(list)
    for path in sorted(files):
        groups[_owner(path)].append(path)
    changed = _changed_owners(view, old[0] if old else "", set(groups))
    if old:
        # Include vanished groups if the old tree is no longer readable.
        present = {
            item[0] for item in connection.execute("SELECT DISTINCT owner FROM files")
        }
        changed.update(present - groups.keys())
    source_paths = {}
    for owner in sorted(changed):
        paths = groups.get(owner, ())
        if owner.startswith(("idea/", "draft/")) and paths:
            source_paths[owner] = paths[0]
        elif owner.startswith("story/"):
            story = int(owner.removeprefix("story/"))
            source = story_event_path(story)
            if source in paths:
                source_paths[owner] = source
    blobs = repo.read_blobs(view.snapshot.tree, tuple(source_paths.values()))
    for owner in sorted(changed):
        connection.execute("DELETE FROM files WHERE owner = ?", (owner,))
        connection.execute("DELETE FROM events WHERE owner = ?", (owner,))
        connection.execute("DELETE FROM search WHERE key = ?", (owner,))
        kind = owner.split("/", 1)[0]
        if kind != "file":
            connection.execute(
                f"DELETE FROM {TABLE_BY_KIND[kind]} WHERE key = ?", (owner,)
            )
        paths = groups.get(owner, ())
        connection.executemany(
            "INSERT INTO files VALUES (?, ?, ?)",
            ((path, owner, files[path].oid) for path in paths),
        )
        source = source_paths.get(owner)
        if source is None:
            continue
        raw = blobs[source]
        if raw is None:
            raise ValueError("indexed source is missing from the pinned tree")
        if kind == "story":
            row, events = _story(owner, source, raw)
            connection.executemany(
                "INSERT INTO events VALUES (?, ?, ?)",
                ((owner, sequence, event) for sequence, event in events),
            )
        else:
            row = _authored(owner, source, raw)
        if row is not None:
            connection.execute(
                f"INSERT INTO {TABLE_BY_KIND[kind]} VALUES (?, ?)",
                (owner, row.model_dump_json()),
            )
            connection.execute(
                "INSERT INTO search VALUES (?, ?, ?)",
                (owner, row.title, "\n".join((row.text, *row.lessons))),
            )
    connection.execute(
        "INSERT OR REPLACE INTO metadata VALUES (1, ?)", (view.snapshot.tree,)
    )


def build_connection(connection: sqlite3.Connection, view: IndexView) -> None:
    connection.execute("BEGIN IMMEDIATE")
    with connection:
        _store(connection, view)


def _build_file(view: IndexView) -> None:
    with closing(open_index(view.database)) as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        build_connection(connection, view)


def index_snapshot(
    snapshot: Snapshot, *, repository: Repository, database: Path
) -> IndexView:
    """Build an index and atomically swap its tree in a WAL write transaction."""
    if snapshot != repository.read_tree(snapshot.revision):
        raise ValueError("snapshot does not name the pinned repository tree")
    database.parent.mkdir(parents=True, exist_ok=True)
    view = IndexView(snapshot, repository, database)
    identity = _file_identity(database) if database.exists() else None
    try:
        _build_file(view)
    except sqlite3.DatabaseError as error:
        if error.sqlite_errorcode & 0xFF not in {
            sqlite3.SQLITE_CORRUPT,
            sqlite3.SQLITE_NOTADB,
        }:
            raise
        with TemporaryDirectory(
            prefix=".aitm-index-", dir=database.parent
        ) as temporary:
            replacement = Path(temporary) / "index.sqlite"
            _build_file(IndexView(snapshot, repository, replacement))
            current = _file_identity(database)
            if identity is None or current != identity:
                raise sqlite3.OperationalError(
                    "the damaged index changed during rebuild"
                ) from error
            replace(replacement, database)
    return view


def _file_identity(database: Path) -> tuple[int, int, int, int]:
    current = database.stat()
    return current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns
