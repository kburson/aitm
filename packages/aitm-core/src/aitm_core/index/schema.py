"""Versioned local SQLite projection for immutable planning trees."""

import sqlite3
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from aitm_core.models.lifecycle import Relationships

INDEX_VERSION = 1
DOCUMENT_TABLES = ("stories", "ideas", "drafts")
TABLES = (*DOCUMENT_TABLES, "events", "files", "search", "metadata")


class IndexRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str
    kind: Literal["story", "idea", "draft"]
    title: str
    text: str
    path: str
    story_id: int | None = None
    state: str | None = None
    relationships: Relationships | None = None
    lessons: tuple[str, ...] = ()


def open_index(database: Path, *, read_only: bool = False) -> sqlite3.Connection:
    if read_only:
        return sqlite3.connect(
            database.resolve().as_uri() + "?mode=ro", uri=True, timeout=0.05
        )
    return sqlite3.connect(database, timeout=0.05)


def initialize(connection: sqlite3.Connection) -> None:
    for table in DOCUMENT_TABLES:
        connection.execute(
            f"CREATE TABLE IF NOT EXISTS {table} (key TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS events (owner TEXT, sequence INTEGER, event TEXT, PRIMARY KEY (owner, sequence))"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS files (path TEXT PRIMARY KEY, owner TEXT NOT NULL, oid TEXT NOT NULL)"
    )
    connection.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(key UNINDEXED, title, content)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS metadata (singleton INTEGER PRIMARY KEY CHECK (singleton = 1), tree TEXT NOT NULL)"
    )
    connection.execute(f"PRAGMA user_version = {INDEX_VERSION}")
