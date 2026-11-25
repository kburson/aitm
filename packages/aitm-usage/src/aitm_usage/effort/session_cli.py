"""Command callbacks for explicitly enrolled effort sessions."""

import json
import sys
from argparse import Namespace, _SubParsersAction
from dataclasses import replace
from pathlib import Path
from uuid import UUID

from ..types import _decode
from .receipts import NativeTurn, ReviewBinding, Role, UsageReceipt
from .session import RateEvidence, SessionStore, validate_public_receipt
from .session_codex import (
    codex_child_parent_turn,
    parse_codex_hook,
    recover_codex_desktop,
)
from .store import EffortError


def add_session_commands(commands: _SubParsersAction) -> None:
    select = commands.add_parser(
        "session-select", help="select the story for future turns"
    )
    select.add_argument("session", type=UUID)
    select.add_argument("story", type=int)
    select.add_argument("remote")
    select.add_argument("--epic", type=int)
    expect = commands.add_parser(
        "session-expect", help="record a dispatch before launch"
    )
    expect.add_argument("session", type=UUID)
    expect.add_argument("attempt", type=UUID)
    expect.add_argument("role", type=Role, choices=list(Role))
    expect.add_argument("launch")
    expect.add_argument("--parent", type=UUID)
    expect.add_argument("--review")
    expect.add_argument("--round", type=int)
    bind = commands.add_parser(
        "session-bind", help="attach a verified private native reference"
    )
    bind.add_argument("session", type=UUID)
    bind.add_argument("attempt", type=UUID)
    bind.add_argument("launch")
    bind.add_argument("native", type=Path)
    settle = commands.add_parser(
        "session-settle", help="ingest an exact adapter receipt"
    )
    settle.add_argument("session", type=UUID)
    settle.add_argument("receipt", type=Path)
    status = commands.add_parser("session-status", help="show private capture coverage")
    status.add_argument("session", type=UUID)
    publish = commands.add_parser(
        "session-publish", help="publish sanitized receipts to planning"
    )
    publish.add_argument("session", type=UUID)
    publish.add_argument("repository", type=Path)
    hook = commands.add_parser(
        "session-codex-hook", help="handle one authorized Codex lifecycle event"
    )
    hook.add_argument("session", type=UUID)
    hook.add_argument("thread")
    hook.add_argument("account")
    hook.add_argument("rollout_root", type=Path)
    hook.add_argument("--retry", type=UUID, help="retry one retained terminal callback")


def _read(path: Path, limit: int = 2 << 20) -> bytes:
    with path.open("rb") as stream:
        content = stream.read(limit + 1)
    if len(content) > limit:
        raise EffortError("Private input exceeds its byte limit")
    return content


def _codex_hook(args: Namespace, store: SessionStore) -> int:
    raw = (
        sys.stdin.buffer.read((1 << 20) + 1)
        if args.retry is None
        else store.codex_callback(args.session, args.retry)
    )
    event = parse_codex_hook(raw)
    if event.session_id != args.thread:
        return 0
    child = event.agent_id if event.event in {"SubagentStart", "SubagentStop"} else None
    key = f"{event.session_id}:{event.turn_id}"
    owner = UUID(hex=store.reference("codex-owner", key).value[-64:-32])
    attempt = (
        owner
        if child is None
        else UUID(hex=store.reference("codex-child", f"{key}:{child}").value[-64:-32])
    )
    launch = store.reference("launch", f"{key}:{child or ''}")
    if event.event in {"UserPromptSubmit", "SubagentStart"}:
        store.expect(
            args.session,
            attempt,
            Role.ORCHESTRATOR if child is None else Role.WORKER,
            launch,
        )
        return 0
    if event.event not in {"Stop", "Interrupt", "SubagentStop"}:
        return 0
    expected = store.expected(args.session, attempt)
    if not event.transcript_path:
        return 3
    root = args.rollout_root.resolve(strict=True)
    path = Path(event.transcript_path)
    safe = path.resolve()
    if safe != path or not safe.is_relative_to(root):
        raise EffortError("Codex callback path is outside its authorized rollout root")
    retained = {
        "hook_event_name": event.event,
        "session_id": event.session_id,
        "turn_id": event.turn_id,
        "agent_id": event.agent_id,
        "agent_transcript_path" if child else "transcript_path": str(safe),
    }
    store.retain_codex_callback(
        args.session, attempt, json.dumps(retained, sort_keys=True)
    )
    if not safe.is_file():
        return 3
    parent_turn = None
    enrollment = expected.enrollment
    if child:
        parent_turn = codex_child_parent_turn(
            path=safe,
            session_id=child,
            turn_id=event.turn_id,
            parent_session_id=event.session_id,
        )
        if parent_turn is None:
            return 3
        parent_attempt = UUID(
            hex=store.reference(
                "codex-owner", f"{event.session_id}:{parent_turn}"
            ).value[-64:-32]
        )
        store.attach_parent(args.session, attempt, parent_attempt)
        enrollment = replace(enrollment, parent_attempt_id=parent_attempt)
    result = recover_codex_desktop(
        enrollment,
        account=store.reference("codex-account", args.account),
        pseudonymize=store.reference,
        path=safe,
        session_id=child or event.session_id,
        turn_id=event.turn_id,
        parent_session_id=event.session_id if child else None,
        parent_turn_id=parent_turn,
    )
    receipt = result.observation.receipt
    if receipt is None:
        return 3
    models = {request.model for request in result.requests}
    rates = None
    if len(models) == 1 and None not in models:
        rates = RateEvidence(
            models.pop(), tuple(request.tokens for request in result.requests)
        )
    store.bind(args.session, attempt, launch, receipt.turn)
    store.accept(args.session, receipt, rates)
    return 0


def run_session_command(args: Namespace) -> int:
    store = SessionStore(args.database, args.project)
    match args.command:
        case "session-select":
            store.select(args.session, args.story, args.remote, epic=args.epic)
        case "session-expect":
            if (args.review is None) != (args.round is None):
                raise EffortError("Supply both review identity and round")
            review = (
                None
                if args.review is None
                else ReviewBinding(store.reference("review", args.review), args.round)
            )
            store.expect(
                args.session,
                args.attempt,
                args.role,
                store.reference("launch", args.launch),
                parent=args.parent,
                review=review,
            )
        case "session-bind":
            store.bind(
                args.session,
                args.attempt,
                store.reference("launch", args.launch),
                _decode(_read(args.native), NativeTurn),
            )
        case "session-settle":
            print(
                store.accept(args.session, UsageReceipt.from_json(_read(args.receipt)))
            )
        case "session-status":
            print(
                json.dumps(
                    {str(k): v for k, v in store.status(args.session).items()},
                    sort_keys=True,
                )
            )
        case "session-publish":
            from .session_publication import PublicationEntry, publish_receipts

            entries = []
            for payload in store.public_receipts(args.session):
                row = validate_public_receipt(payload)
                entries.append(
                    PublicationEntry(
                        row["story"], row["identity"], row["revision"], payload
                    )
                )
            print(
                publish_receipts(
                    args.repository, store.remote(), store.project_id, entries
                )
            )
        case "session-codex-hook":
            return _codex_hook(args, store)
    return 0
