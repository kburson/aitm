import json
from hashlib import sha256
from pathlib import Path
from uuid import UUID

import pytest

from aitm_usage.effort import Enrollment, Outcome, Role, UsageScope
from aitm_usage.effort.capture import CaptureGap
from aitm_usage.effort.session_codex import parse_codex_hook, recover_codex_desktop
from aitm_usage.types import Availability, SourceRef


def uid(value):
    return str(UUID(int=value))


SESSION, TURN, CHILD, CHILD_TURN, OTHER = map(uid, range(1, 6))
BUILD = "0.171.0-alpha.13.2"
MODEL = "gpt-6.2-sol"
ENROLLMENT = Enrollment(
    UUID(int=10), UUID(int=11), UUID(int=12), Role.ORCHESTRATOR, 457
)
WORKER = Enrollment(
    UUID(int=10),
    UUID(int=11),
    UUID(int=13),
    Role.WORKER,
    457,
    parent_attempt_id=ENROLLMENT.attempt_id,
)


def ref(namespace, text):
    digest = sha256(f"{namespace}:{text}".encode()).hexdigest()
    return SourceRef(f"hmac-sha256:{digest}:{'0' * 64}")


def event(kind, **payload):
    return {
        "type": "event_msg",
        "timestamp": "2026-11-25T18:01:00Z",
        "payload": {"type": kind, **payload},
    }


def frame(kind, **payload):
    return {"type": kind, "timestamp": "2026-11-25T18:00:00Z", "payload": payload}


def metadata(thread=SESSION, parent=None, *, root_source="user"):
    source = (
        "vscode"
        if parent is None
        else {"subagent": {"thread_spawn": {"parent_thread_id": parent, "depth": 1}}}
    )
    return frame(
        "session_meta",
        id=thread,
        session_id=thread if parent is None else parent,
        source=source,
        thread_source=root_source if parent is None else "subagent",
        cli_version=BUILD,
        originator="Codex Desktop",
    )


def tokens(multiplier):
    return {
        "input_tokens": 19 * multiplier,
        "cached_input_tokens": 12 * multiplier,
        "cache_write_input_tokens": 0,
        "output_tokens": 4 * multiplier,
        "reasoning_output_tokens": multiplier,
        "total_tokens": 23 * multiplier,
    }


def turn(
    id=TURN,
    thread=SESSION,
    parent=SESSION,
    root=None,
    *,
    terminal="task_complete",
    trigger="composer",
    parent_turn=None,
):
    root_id = root or id
    identity = {"turn_id": id, "root_turn_id": root_id}
    attribution = dict(
        identity, parent_turn_id=parent_turn or root, turn_trigger=trigger
    )
    start = event("task_started", **identity, turn_attribution=attribution)
    start["timestamp"] = "2026-11-25T18:00:00Z"
    first = frame(
        "token_usage_record",
        **identity,
        session_id=parent,
        thread_id=thread,
        response_id="private-response-01",
        usage=tokens(1),
        turn_token_usage=tokens(1),
        thread_token_usage=tokens(70),
    )
    duplicate_counter = event(
        "token_count",
        info={"last_token_usage": tokens(1), "total_token_usage": tokens(1)},
    )
    second = frame(
        "token_usage_record",
        **identity,
        session_id=parent,
        thread_id=thread,
        response_id="private-response-02",
        usage=tokens(1),
        turn_token_usage=tokens(2),
        thread_token_usage=tokens(71),
    )
    start_and_usage = [
        start,
        frame("turn_context", **identity, model=MODEL),
        first,
        duplicate_counter,
        second,
    ]
    return start_and_usage + ([] if terminal is None else [event(terminal, **identity)])


def save(tmp_path, *rows):
    path = tmp_path / "exact.jsonl"
    path.write_bytes(b"".join(json.dumps(row).encode() + b"\n" for row in rows))
    return path


def recover(path, **kwargs):
    options = dict(
        enrollment=ENROLLMENT,
        account=ref("account", "fixture"),
        pseudonymize=ref,
        session_id=SESSION,
        turn_id=TURN,
        path=path,
    )
    return recover_codex_desktop(**(options | kwargs))


def test_hook_extracts_exact_private_binding_without_retaining_payload():
    secret = "a-private-prompt"
    exact = str(Path.cwd() / "private-exact.jsonl")
    parent = str(Path.cwd() / "private-parent.jsonl")
    raw = json.dumps(
        {
            "hook_event_name": "SubagentStop",
            "session_id": SESSION,
            "turn_id": TURN,
            "agent_id": CHILD,
            "agent_transcript_path": exact,
            "transcript_path": parent,
            "model": MODEL,
            "last_assistant_message": secret,
        }
    ).encode()
    hook = parse_codex_hook(raw)
    assert (hook.event, hook.session_id, hook.turn_id, hook.agent_id) == (
        "SubagentStop",
        SESSION,
        TURN,
        CHILD,
    )
    assert hook.transcript_path == exact
    assert secret not in repr(hook) and "private" not in repr(hook)
    with pytest.raises(ValueError, match="Invalid"):
        parse_codex_hook(raw.replace(b'"turn_id":', b'"turn_id":null,"turn_id":'))
    with pytest.raises(ValueError, match="Invalid"):
        parse_codex_hook(raw.replace(CHILD.encode(), b"unconfirmed-path"))


def test_subagent_start_and_stop_expose_the_same_child_path():
    owner = str(Path.cwd() / "private-owner.jsonl")
    child = str(Path.cwd() / "private-child.jsonl")
    common = {"session_id": SESSION, "turn_id": CHILD_TURN, "agent_id": CHILD}
    start = dict(common, hook_event_name="SubagentStart", transcript_path=child)
    stop = dict(
        common,
        hook_event_name="SubagentStop",
        transcript_path=owner,
        agent_transcript_path=child,
    )
    assert parse_codex_hook(json.dumps(start).encode()).transcript_path == child
    assert parse_codex_hook(json.dumps(stop).encode()).transcript_path == child


def test_exact_bound_owner_uses_request_evidence_and_counts_only_once(tmp_path):
    capture = recover(save(tmp_path, metadata(), *turn()))
    receipt = capture.observation.receipt
    assert receipt.coverage == Availability.COMPLETE
    assert receipt.turn.surface == "desktop"
    assert receipt.scope == UsageScope.BOUNDED
    assert receipt.tokens.total_tokens == 46
    assert receipt.started_at < receipt.ended_at
    assert capture.model == MODEL
    assert [request.tokens.total_tokens for request in capture.requests] == [23, 23]
    assert "private-response" not in receipt.to_json()


def test_forked_child_discards_copied_parent_and_binds_exact_dispatch(tmp_path):
    path = save(
        tmp_path,
        metadata(CHILD, SESSION),
        metadata(),
        *turn(),
        *turn(CHILD_TURN, CHILD, SESSION, TURN),
    )
    capture = recover(
        path,
        enrollment=WORKER,
        session_id=CHILD,
        turn_id=None,
        parent_session_id=SESSION,
        parent_turn_id=TURN,
    )
    receipt = capture.observation.receipt
    assert receipt.tokens.total_tokens == 46
    assert receipt.turn.surface == "desktop-subagent"
    assert receipt.turn.session == ref("codex-session", CHILD)
    assert receipt.turn.turn == ref("codex-turn", f"{CHILD}:{CHILD_TURN}")
    assert not recover(
        path,
        enrollment=WORKER,
        session_id=CHILD,
        turn_id=CHILD_TURN,
        parent_session_id=SESSION,
        parent_turn_id=OTHER,
    ).observation.receipt
    assert not recover(
        path,
        enrollment=WORKER,
        session_id=CHILD,
        turn_id=TURN,
        parent_session_id=SESSION,
        parent_turn_id=TURN,
    ).observation.receipt


def test_missing_terminal_is_pending_and_trailing_fragment_is_ignored(tmp_path):
    path = save(tmp_path, metadata(), *turn(terminal=None))
    with path.open("ab") as stream:
        stream.write(b'{"type":')
    result = recover(path).observation
    assert result.gap == CaptureGap.MISSING
    assert result.receipt is None


def test_interruption_keeps_observed_usage_as_partial(tmp_path):
    obs = recover(
        save(tmp_path, metadata(), *turn(terminal="turn_aborted"))
    ).observation
    assert obs.outcome == Outcome.INTERRUPTED
    assert obs.receipt.coverage == Availability.PARTIAL
    assert obs.receipt.tokens.total_tokens == 46


def test_refuses_unsound_usage_and_wrong_exact_file(tmp_path):
    corrupt = turn()
    corrupt[-2]["payload"]["turn_token_usage"] = tokens(3)
    obs = recover(save(tmp_path, metadata(), *corrupt)).observation
    assert obs.gap == CaptureGap.MALFORMED
    assert not obs.receipt
    obs = recover(save(tmp_path, metadata(), *turn()), session_id=OTHER).observation
    assert obs.gap == CaptureGap.WRONG_TURN
    assert not obs.receipt
    obs = recover(save(tmp_path, metadata(), *turn()), max_bytes=128).observation
    assert obs.gap == CaptureGap.EVIDENCE_LIMIT
    assert not obs.receipt


def test_refuses_ambiguous_child_history_without_explicit_turn(tmp_path):
    path = save(
        tmp_path,
        metadata(CHILD, SESSION),
        metadata(),
        *turn(),
        *turn(CHILD_TURN, CHILD, SESSION, TURN),
        *turn(OTHER, CHILD, SESSION, TURN),
    )
    obs = recover(
        path,
        enrollment=WORKER,
        session_id=CHILD,
        turn_id=None,
        parent_session_id=SESSION,
        parent_turn_id=TURN,
    ).observation
    assert obs.gap == CaptureGap.WRONG_TURN
    assert not obs.receipt


def test_exact_child_parent_turn_is_available_before_completion(tmp_path):
    from aitm_usage.effort.session_codex import codex_child_parent_turn

    path = save(
        tmp_path,
        metadata(CHILD, SESSION),
        metadata(),
        *turn(),
        turn(CHILD_TURN, CHILD, SESSION, TURN)[0],
    )
    args = dict(
        path=path, session_id=CHILD, turn_id=CHILD_TURN, parent_session_id=SESSION
    )
    assert codex_child_parent_turn(**args) == TURN
    assert codex_child_parent_turn(**(args | {"turn_id": OTHER})) is None
    with pytest.raises(ValueError, match="invalid"):
        codex_child_parent_turn(**(args | {"parent_session_id": OTHER}))
    with pytest.raises(ValueError, match="invalid"):
        codex_child_parent_turn(**(args | {"turn_id": TURN}))


def test_cli_callbacks_keep_dispatch_story_and_can_replay_after_restart(
    tmp_path, monkeypatch
):
    import io
    import sys
    from types import SimpleNamespace

    from aitm_usage.effort.cli import main
    from aitm_usage.effort.session import SessionStore, validate_public_receipt

    database = tmp_path / "effort.db"
    project, session = UUID(int=31), UUID(int=32)
    store = SessionStore(database, project)
    remote = "https://example.invalid/aitm.git"
    store.select(session, 457, remote)
    args = [
        "--database",
        str(database),
        "--project",
        str(project),
        "session-codex-hook",
        str(session),
        SESSION,
        "configured",
        str(tmp_path.resolve()),
    ]
    owner_path = save(
        tmp_path,
        metadata(root_source="agent_created_thread"),
        *turn(root=OTHER, trigger="app_tool_send_message"),
    )
    child_path = tmp_path / "child.jsonl"
    child_rows = [
        metadata(CHILD, SESSION),
        metadata(root_source="agent_created_thread"),
        *turn(root=OTHER, trigger="app_tool_send_message"),
        *turn(
            CHILD_TURN,
            CHILD,
            SESSION,
            OTHER,
            trigger="app_tool_send_message",
            parent_turn=TURN,
        ),
    ]
    child_path.write_bytes(
        b"".join(json.dumps(row).encode() + b"\n" for row in child_rows)
    )

    def hook(name, *, child=False, path=None):
        event = {
            "hook_event_name": name,
            "session_id": SESSION,
            "turn_id": CHILD_TURN if child else TURN,
        }
        if child:
            event.update(agent_id=CHILD)
        if path:
            event["agent_transcript_path" if child else "transcript_path"] = str(
                path.resolve()
            )
        monkeypatch.setattr(
            sys, "stdin", SimpleNamespace(buffer=io.BytesIO(json.dumps(event).encode()))
        )
        return main(args)

    assert hook("UserPromptSubmit") == 0
    store.select(session, 458, remote)
    assert hook("SubagentStart", child=True) == 0
    assert set(store.status(session).values()) == {"pending-binding"}
    child_evidence = child_path.read_bytes()
    child_path.unlink()
    assert hook("SubagentStop", child=True, path=child_path) == 3
    child_attempt = next(
        attempt
        for attempt in store.status(session)
        if store.expected(session, attempt).enrollment.role is Role.WORKER
    )
    child_path.write_bytes(child_evidence)
    assert main(args + ["--retry", str(child_attempt)]) == 0
    assert hook("Stop", path=owner_path) == 0
    assert hook("Stop", path=owner_path) == 0
    reopened = SessionStore(database, project)
    rows = [
        validate_public_receipt(payload)
        for payload in reopened.public_receipts(session)
    ]
    assert {row["role"] for row in rows} == {"orchestrator", "worker"}
    assert {row["story"] for row in rows} == {457}
    assert all(row["model"] == MODEL and len(row["rate_inputs"]) == 2 for row in rows)
