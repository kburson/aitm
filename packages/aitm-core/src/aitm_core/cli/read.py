"""Installed read routes for a pinned planning snapshot."""

import argparse
import sqlite3
from collections.abc import Callable
from os import fsdecode
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from aitm_core.context import ContextPacket, discuss
from aitm_core.events import UnavailableReducer
from aitm_core.index.build import IndexView, index_snapshot
from aitm_core.index.query import Query, query
from aitm_core.index.schema import IndexRow
from aitm_core.models.common import CommandResult, LocalOutcome, StoreAnchor
from aitm_core.services import load_installation, refresh
from aitm_core.store.objects import GitCommandError, Repository

type Explain = Callable[[IndexRow, IndexView], tuple[str, ...]]


class ReadEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    commit: str
    tree: str
    code_freshness: str
    shared_freshness: str
    source: str
    rows: tuple[IndexRow, ...] = ()
    context: ContextPacket | None = None


class ReadResult(CommandResult):
    read: ReadEvidence


def handle(
    route: tuple[str, ...],
    arguments: tuple[str, ...],
    *,
    explanation: Explain | None = None,
) -> CommandResult:
    identity = uuid4().hex
    action = route[-1]
    parser = argparse.ArgumentParser(
        prog=f"aitm {' '.join(route)}", exit_on_error=False
    )
    if action in {"show", "explain", "discuss"}:
        parser.add_argument("story", type=int)
    if action == "search":
        parser.add_argument("terms", nargs="+")
    parser.add_argument("--anchor", type=Path)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--installation", type=Path)
    parser.add_argument("--refresh", action="store_true")
    try:
        options = parser.parse_args(arguments)
        if options.anchor is None:
            return CommandResult(
                operation_id=identity,
                local=LocalOutcome.UNAVAILABLE,
                evidence=("Supply the trusted store anchor with --anchor.",),
            )
        return _read(identity, action, options, explanation)
    except (argparse.ArgumentError, ValueError) as error:
        outcome = LocalOutcome.INTEGRITY_ERROR
        message = str(error)
    except (
        GitCommandError,
        OSError,
        sqlite3.DatabaseError,
        UnavailableReducer,
    ) as error:
        outcome = LocalOutcome.UNAVAILABLE
        message = str(error)
    return CommandResult(operation_id=identity, local=outcome, evidence=(message,))


def _read(
    identity: str, action: str, options: argparse.Namespace, explanation: Explain | None
) -> CommandResult:
    story = getattr(options, "story", None)
    if story is not None and story < 1:
        raise ValueError("query requires a positive story ID")
    anchor = StoreAnchor.model_validate_json(options.anchor.read_bytes())
    repository = Repository(options.repository, anchor.planning_ref)
    installation = load_installation(repository, anchor, options.installation)
    views = refresh(installation, cached=not options.refresh)
    revision = views.planning.observed_commit
    if revision is None:
        return CommandResult(
            operation_id=identity,
            local=LocalOutcome.UNAVAILABLE,
            evidence=("No local planning snapshot is available.",),
        )
    snapshot = repository.read_tree(revision)
    common = repository._git("rev-parse", "--path-format=absolute", "--git-common-dir")
    database = Path(fsdecode(common.removesuffix(b"\n"))) / "aitm" / "index.sqlite"
    view = IndexView(snapshot, repository, database)
    if action == "rebuild":
        view = index_snapshot(snapshot, repository=repository, database=database)

    search = " ".join(options.terms) if action == "search" else None
    result = query(view, Query(text=search, story=story, stories_only=action == "list"))
    shared = views.shared.status.value if views.shared is not None else "unknown"
    details = ReadEvidence(
        commit=result.commit,
        tree=result.tree,
        source=result.source,
        code_freshness=views.code_freshness.value,
        shared_freshness=shared,
        rows=result.rows,
    )
    freshness = (
        f"Pinned planning tree {result.tree} at {result.commit}.",
        f"Code freshness {details.code_freshness}. Shared planning {shared}.",
    )
    outcome = LocalOutcome.COMPLETED
    if action == "explain" and explanation is None:
        outcome = LocalOutcome.UNAVAILABLE
        details = details.model_copy(update={"rows": ()})
        messages = ("The required transition explanation capability is unavailable.",)
    elif story is not None and not result.rows:
        outcome = LocalOutcome.UNAVAILABLE
        messages = (f"Story {story} is absent from the pinned planning tree.",)
    elif action == "explain":
        assert explanation is not None
        messages = explanation(result.rows[0], view)
    elif action == "discuss":
        assert story is not None
        packet = discuss(story, view)
        details = details.model_copy(update={"context": packet})
        messages = (packet.title, packet.description, packet.suggested_invocation)
    elif action == "rebuild":
        messages = ("Rebuilt the index for the pinned planning tree.",)
    elif action == "show":
        row = result.rows[0]
        messages = (f"#{row.story_id} {row.title} ({row.state})", row.text)
    else:
        messages = tuple(row.title for row in result.rows) or ("No matching records.",)
    return ReadResult(
        operation_id=identity,
        local=outcome,
        evidence=(*messages, *freshness),
        read=details,
    )
