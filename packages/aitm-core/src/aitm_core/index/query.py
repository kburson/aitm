"""Query an exact indexed tree with an equivalent real-tree fallback."""

import sqlite3
from contextlib import closing
from dataclasses import dataclass

from .build import IndexView, active_index, build_connection, index_snapshot
from .schema import DOCUMENT_TABLES, INDEX_VERSION, IndexRow, open_index


@dataclass(frozen=True, slots=True)
class Query:
    text: str | None = None
    story: int | None = None
    stories_only: bool = False


@dataclass(frozen=True, slots=True)
class QueryResult:
    commit: str
    tree: str
    source: str
    rows: tuple[IndexRow, ...]


def _read(connection: sqlite3.Connection, filter: Query) -> tuple[IndexRow, ...]:
    tables = (
        DOCUMENT_TABLES[:1] if filter.stories_only or filter.story else DOCUMENT_TABLES
    )
    conditions = []
    bindings = []
    if filter.text:
        phrase = " ".join(
            '"' + term.replace('"', '""') + '"' for term in filter.text.split()
        )
        if phrase:
            conditions.append("key IN (SELECT key FROM search WHERE search MATCH ?)")
            bindings.append(phrase)
    if filter.story is not None:
        conditions.append("key = ?")
        bindings.append(f"story/{filter.story}")
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    rows = [
        IndexRow.model_validate_json(payload)
        for table in tables
        for (payload,) in connection.execute(
            f"SELECT payload FROM {table}{where}", bindings
        )
    ]
    return tuple(
        sorted(rows, key=lambda row: (row.story_id is None, row.story_id or 0, row.key))
    )


def _indexed(view: IndexView, filter: Query) -> tuple[IndexRow, ...] | None:
    with closing(open_index(active_index(view.database), read_only=True)) as connection:
        connection.execute("PRAGMA query_only = ON")
        connection.execute("BEGIN")
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        cached = connection.execute(
            "SELECT tree FROM metadata WHERE singleton = 1"
        ).fetchone()
        if version == INDEX_VERSION and cached == (view.snapshot.tree,):
            return _read(connection, filter)
    return None


def query(view: IndexView, filter: Query) -> QueryResult:
    """Select from a single read transaction or rebuild only the requested tree."""
    snapshot = view.snapshot
    if snapshot != view.repository.read_tree(snapshot.revision):
        raise ValueError("query snapshot does not name the pinned repository tree")
    try:
        rows = _indexed(view, filter)
        if rows is None and view.repository.tip().tree == snapshot.tree:
            # Advance the local cache only for the current writer. Historical
            # pinned readers can always rebuild their exact view in memory.
            index_snapshot(snapshot, repository=view.repository, database=view.database)
            rows = _indexed(view, filter)
        if rows is not None:
            return QueryResult(snapshot.revision, snapshot.tree, "index", rows)
    except (OSError, sqlite3.DatabaseError, ValueError):
        pass
    with closing(sqlite3.connect(":memory:")) as connection:
        build_connection(connection, view)
        return QueryResult(
            snapshot.revision, snapshot.tree, "tree", _read(connection, filter)
        )
