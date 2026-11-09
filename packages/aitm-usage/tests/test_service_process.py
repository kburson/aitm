import json
import os
import shlex
import signal
import socket
import subprocess
import sys
from collections import Counter
from contextlib import contextmanager
from datetime import timedelta
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from uuid import UUID

import test_claude as claude
import test_codex as codex

from aitm_usage.export import MANIFEST_NAME, USAGE_NAME
from aitm_usage.ledger import Ledger
from aitm_usage.pricing import load_rate_card
from aitm_usage.scopes import ACKS_NAME, INBOX_NAME, session_reference
from aitm_usage.sources.claude import (
    claude_receipt_reference,
    claude_request_boundary_reference,
)
from aitm_usage.sources.codex import (
    codex_receipt_reference,
    codex_request_boundary_reference,
)
from aitm_usage.sources.scan import discover, scan
from aitm_usage.types import (
    BoundaryKind,
    CommandReceipt,
    DiagnosticCode,
    InboxCommand,
    ItemKey,
    ItemKind,
    MarkerDisposition,
    Provider,
    Registration,
    ScopeEnrollment,
    ScopeMarker,
    UsageObservation,
    WorkPhase,
    encode_command,
    encode_marker,
)

PROJECT = UUID("380323ba-b6ec-4c33-b2df-a102e8f9ac48")
EPIC, CHILD = 83, 93
CX_EPIC, CX_CHILD, CL_CHILD, TORN = (UUID(int=0xB00 + n) for n in range(4))
RUNNER = Path(__file__).parent / "fixtures/service/run_cli.py"
CONSOLE = Path(sys.executable).with_name("aitm-usage")
TIMEOUT = 15

PROMPT = "u12-private-prompt-ae063a"
REASONING = "u12-private-reasoning-b7ab5c"
CREDENTIAL = "u12-private-credential-d82538"
ACCOUNT = "u12-private-account-c4410e"
BRANCH = "u12-private-branch-d8bee0"
MALFORMED_CLAUDE = "u12-malformed-claude-ffa3f0"
MALFORMED_CODEX = "u12-malformed-codex-5dbb4e"
MALFORMED_MARKER = "u12-malformed-marker-79d0c3"


class _Project:
    def __init__(self, base):
        self.root = base / "project"
        self.control = base / "control"
        self.logs = base / "logs"
        self.logs.mkdir(mode=0o700)
        assert CONSOLE.is_file(), "run the locked suite with the installed console"
        self.env = {**os.environ, "CODEX_THREAD_ID": str(codex.SESSION)}

    def args(self, *args, barrier=None, stop="-", target="-"):
        return [
            sys.executable,
            str(RUNNER),
            str(self.control),
            str(CONSOLE),
            "-" if barrier is None else str(barrier),
            stop,
            str(target),
            "--project",
            str(self.root),
            *args,
        ]

    def command(self, *args, expected=0):
        result = subprocess.run(
            self.args(*args),
            env=self.env,
            capture_output=True,
            timeout=TIMEOUT,
            check=False,
        )
        # Persist the same bytes that a launcher would capture for privacy QA.
        with (self.logs / "cli.stdout").open("ab") as output:
            output.write(result.stdout)
        with (self.logs / "cli.stderr").open("ab") as output:
            output.write(result.stderr)
        assert result.returncode == expected, args[0]
        return result.stdout if result.stdout else result.stderr

    def json(self, *args, expected=0):
        return json.loads(self.command(*args, "--json", expected=expected))

    @contextmanager
    def service(self, name, *, stop="between-scans", target="-"):
        parent, child = socket.socketpair()
        with (
            parent,
            child,
            (self.logs / f"{name}.stdout").open("wb") as output,
            (self.logs / f"{name}.stderr").open("wb") as errors,
            subprocess.Popen(
                self.args(
                    "service", "run", barrier=child.fileno(), stop=stop, target=target
                ),
                env=self.env,
                pass_fds=(child.fileno(),),
                stdout=output,
                stderr=errors,
            ) as process,
        ):
            child.close()
            parent.settimeout(TIMEOUT)
            with parent.makefile("rb") as messages:
                try:
                    yield _Service(process, parent, messages)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=TIMEOUT)


class _Service:
    def __init__(self, process, socket, messages):
        self.process = process
        self.socket = socket
        self.messages = messages

    def at(self, event):
        line = self.messages.readline()
        assert line, f"collector exited before {event} (rc={self.process.poll()})"
        message = json.loads(line)
        assert message["event"] == event
        assert message["pid"] == self.process.pid
        assert self.process.poll() is None
        return message

    def resume(self):
        self.socket.sendall(b"\n")

    def kill(self):
        self.process.send_signal(signal.SIGKILL)
        assert self.process.wait(timeout=TIMEOUT) == -signal.SIGKILL

    def stop(self):
        self.process.send_signal(signal.SIGINT)
        assert self.process.wait(timeout=TIMEOUT) == 0


def _marker(ledger, provider, command_id, sequence, issue):
    raw, target, receipt = (
        (codex.SESSION, codex_request_boundary_reference, codex_receipt_reference)
        if provider is Provider.CODEX
        else (
            claude.SESSION,
            claude_request_boundary_reference,
            claude_receipt_reference,
        )
    )
    session = session_reference(ledger, provider, str(raw))
    return ScopeMarker(
        command_id,
        provider,
        session,
        sequence,
        BoundaryKind.REQUEST,
        target(ledger, session, command_id),
        claude.AFTER,
        ItemKey(ItemKind.ISSUE, issue),
        WorkPhase.PLANNING,
        ledger.pseudonymize("participant", ACCOUNT),
        PROJECT,
        receipt_ref=receipt(ledger, session, command_id),
    )


def _mark_args(base, marker):
    path = base / f"marker-{marker.marker_id}.json"
    path.write_bytes(encode_marker(marker))
    args = ("scope", "mark", "--marker", str(path))
    if marker.provider is Provider.CLAUDE:
        args += ("--session-id", str(claude.SESSION))
    return (*args, "--json")


def _queued(command_id):
    return (
        json.dumps({"command_id": str(command_id), "status": "queued"}) + "\n"
    ).encode()


def _claude_rows(earlier, reviewer, later, shell, stdout):
    route = claude._native_tool_turn(reviewer, shell, stdout.decode())
    route[0]["message"]["content"][0]["input"]["credential"] = CREDENTIAL
    route[-1]["message"]["content"] = [{"type": "thinking", "thinking": REASONING}]
    route[-1]["message"]["usage"] = claude.usage(output=11)
    malformed = claude.request(
        reviewer,
        req=MALFORMED_CLAUDE,
        msg=MALFORMED_CLAUDE,
        counts=claude.usage(output=MALFORMED_CLAUDE),
        time=claude.AFTER + timedelta(seconds=1),
    )
    return [
        claude.user(earlier),
        claude.request(earlier, req="earlier", msg="earlier", counts=claude.usage(31)),
        claude.user(reviewer, prompt=PROMPT),
        *route,
        malformed,
        claude.user(later),
        claude.request(later, req="later", msg="later", counts=claude.usage(47)),
    ]


def _codex_rows(ledger, checkout, epic_args, child_args, epic_stdout, child_stdout):
    rows = [
        codex.startup(checkout, account=ACCOUNT, git={"branch": BRANCH}),
        *codex.begin(checkout),
        codex.event("user_message", message=PROMPT),
        codex.event(
            "thread_settings_applied",
            thread_id=str(codex.SESSION),
            thread_settings={
                "model": "gpt-6-astra",
                "model_provider_id": "openai",
                "service_tier": "default",
            },
        ),
    ]
    running_input = running_output = 0
    for arguments, stdout, output in (
        (epic_args, epic_stdout, 3),
        (child_args, child_stdout, 5),
    ):
        mark_id = json.loads(stdout)["command_id"]
        call = codex.tool_call(ledger, arguments[3])
        call["payload"]["call_id"] = f"u12-tool-{mark_id}"
        result = codex.tool_output(stdout=stdout.decode())
        result["payload"]["call_id"] = call["payload"]["call_id"]
        prior, target = codex.usage(8, 2), codex.usage(9, output)
        running_input += 8
        running_output += 2
        before = codex.usage(running_input, running_output)
        running_input += 9
        running_output += output
        after = codex.usage(running_input, running_output)
        rows.extend(
            (
                call,
                codex.response(f"u12-before-{mark_id}", before, prior),
                result,
                codex.counter(before, prior),
                codex.response(f"u12-first-{mark_id}", after, target),
                codex.counter(after, target),
            )
        )
    return [
        *rows,
        codex.end(),
        codex.counter({"output_tokens": MALFORMED_CODEX}, codex.usage(0, 0)),
    ]


def _observations(view):
    return tuple(
        revision
        for revision in view.current
        if isinstance(revision.record, UsageObservation)
    )


def _receipt(ledger, marker):
    return ledger.command_receipt(InboxCommand(marker.marker_id, PROJECT, marker))


def _privacy_scan(ledger, roots, canaries):
    needles = tuple(value.encode() for value in canaries)
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file() or path == ledger.key_path:
                continue
            data = path.read_bytes()
            assert all(needle not in data for needle in needles), path.name


def _export(project, sequence, destination):
    return project.json(
        "export",
        "--as-of",
        str(sequence),
        "--rate-card",
        load_rate_card().version,
        "--output",
        str(destination),
    )


def test_real_service_crash_enrollment_and_private_state(tmp_path, monkeypatch):
    base = tmp_path.resolve()
    project = _Project(base)
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: project.control)
    ledger = Ledger.initialize(project.root, PROJECT)
    sources, approved, reviewer, earlier, later = (
        base / name
        for name in ("sources", "approved", "u12-reviewer-path", "earlier", "later")
    )
    for path in (sources, approved, reviewer, earlier, later):
        path.mkdir(mode=0o700)

    epic = _marker(ledger, Provider.CODEX, CX_EPIC, 1, EPIC)
    child = _marker(ledger, Provider.CODEX, CX_CHILD, 2, CHILD)
    review = _marker(ledger, Provider.CLAUDE, CL_CHILD, 1, CHILD)
    torn_marker = _marker(ledger, Provider.CODEX, TORN, 3, CHILD)
    epic_args, child_args, review_args = (
        _mark_args(base, marker) for marker in (epic, child, review)
    )
    shell = shlex.join(("aitm-usage", "--project", str(project.root), *review_args))
    review_file = sources / "u12-claude-source-path.jsonl"
    # The controlled unrelated sections have independently known CWDs.
    # Derive their exact segment refs from the complete controlled fixture.
    claude.write(
        review_file, _claude_rows(earlier, reviewer, later, shell, _queued(CL_CHILD))
    )
    registration = Registration(
        PROJECT, project.root, (sources,), (approved,), claude.CUTOFF
    )
    (candidate,) = discover(registration)
    scanned = scan(candidate, None, registration.cutoff)
    preceding, following = scanned.frames[0], scanned.frames[-1]
    assert preceding.anchor_ref is None and following.anchor_ref is None
    segments = {frame.segment_ref for frame in scanned.frames}
    assert len(segments) == 3 and preceding.segment_ref != following.segment_ref
    config = base / "registration.json"
    config.write_text(
        json.dumps(
            {
                "project_id": str(PROJECT),
                "source_roots": [str(sources)],
                "checkout_anchors": [str(approved)],
                "cutoff": claude.CUTOFF.isoformat(),
                "excluded_segments": [
                    preceding.segment_ref.value,
                    following.segment_ref.value,
                ],
            }
        ),
        encoding="utf-8",
    )
    project.json("register", "--config", str(config))
    review_stdout = project.command(*review_args)
    assert review_stdout == _queued(CL_CHILD)
    claude.write(
        review_file, _claude_rows(earlier, reviewer, later, shell, review_stdout)
    )
    inbox = project.root / INBOX_NAME
    review_publication = inbox / f"{CL_CHILD}.json"
    review_ack = inbox / ACKS_NAME / review_publication.name
    staged = base / "withheld-delivery.json"
    review_publication.rename(staged)
    epic_stdout, child_stdout = (
        project.command(*args) for args in (epic_args, child_args)
    )
    assert (epic_stdout, child_stdout) == (_queued(CX_EPIC), _queued(CX_CHILD))

    # Malformed inputs originate outside the state to test the write
    # boundary. The torn temp contains only a prefix of a real wire command.
    invalid_marker = base / "malformed-marker.json"
    invalid_marker.write_text(
        json.dumps({"private": MALFORMED_MARKER}), encoding="utf-8"
    )
    assert project.command(
        "scope", "mark", "--marker", str(invalid_marker), "--json", expected=1
    ) == (b"aitm-usage: invalid private inbox command or project\n")
    torn_bytes = encode_command(InboxCommand(TORN, PROJECT, torn_marker))[:-7]
    torn = inbox / f".publishing-{TORN.hex}"
    torn.touch(mode=0o600)
    torn.write_bytes(torn_bytes)

    relationship = project.json(
        "item", "parent", "--child", str(CHILD), "--epic", str(EPIC)
    )
    assert relationship["status"] == "queued"
    relationship_id = UUID(relationship["command_id"])

    cx_file = sources / "u12-codex-source-path.jsonl"
    canaries = (
        PROMPT,
        REASONING,
        CREDENTIAL,
        ACCOUNT,
        BRANCH,
        MALFORMED_CLAUDE,
        MALFORMED_CODEX,
        MALFORMED_MARKER,
        str(claude.SESSION),
        str(codex.SESSION),
        str(codex.TURN),
        str(reviewer),
        str(earlier),
        str(later),
        str(invalid_marker),
        epic_args[3],
        child_args[3],
        review_args[3],
        review_file.name,
        cx_file.name,
        "req-next",
        "native-client-request",
        f"u12-tool-{CX_CHILD}",
        f"u12-first-{CX_CHILD}",
    )
    private_roots = (project.root, project.control, project.logs)

    with project.service("first") as first:
        barrier = first.at("between-scans")
        [(review_boundary, review_ordinal)] = barrier["boundaries"]
        assert review_boundary == review.boundary_ref.value
        initial = ledger.as_of()
        assert not _observations(initial)
        assert not any(isinstance(r.record, ScopeEnrollment) for r in initial.current)
        assert _receipt(ledger, review) is None
        assert all(
            _receipt(ledger, marker).disposition is MarkerDisposition.PENDING
            for marker in (epic, child)
        )
        status = project.json("status")
        assert status["held_sources"] == 1
        assert 0 < status["sources"][0]["offset"] < review_file.stat().st_size
        assert any(
            isinstance(r.record, CommandReceipt)
            and r.record.command.command_id == relationship_id
            and r.record.disposition is MarkerDisposition.ACCEPTED
            for r in initial.current
        )
        assert status["invalid_inbox"] == 1
        assert status["relationship_halted"] is False
        assert project.json("collect-once", expected=1) == {"status": "writer-active"}
        _privacy_scan(ledger, private_roots, canaries)
        first.kill()

    # Claude's actual boundary was present in the previous poll, while
    # the exact command publication was withheld from that drain.
    assert project.command(*review_args) == review_stdout
    assert review_publication.read_bytes() == staged.read_bytes()
    with project.service("disposition", stop="before-ack", target=CL_CHILD) as second:
        second.at("before-ack")
        committed = ledger.as_of()
        disposition = _receipt(ledger, review)
        assert disposition.disposition is MarkerDisposition.ACCEPTED
        assert disposition.boundary.ordinal == review_ordinal
        (scope,) = [
            r.record for r in committed.current if isinstance(r.record, ScopeEnrollment)
        ]
        assert scope.marker == review and scope.boundary == disposition.boundary
        assert review_publication.exists() and not review_ack.exists()
        assert committed.checkpoints == initial.checkpoints
        assert not _observations(committed)
        assert committed.sequence == initial.sequence + 1
        _privacy_scan(ledger, private_roots, canaries)
        second.kill()

    # Kill again after actual observation and checkpoint writes in SQLite
    # but before their transaction commits. Other readers see the old view.
    with project.service("transaction", stop="before-commit", target="claude") as third:
        uncommitted = third.at("before-commit")
        assert uncommitted["sequence"] == committed.sequence + 1
        assert ledger.as_of() == committed
        assert not review_publication.exists()
        acknowledgment = review_ack.read_bytes()
        assert json.loads(acknowledgment) == {
            "command_id": str(CL_CHILD),
            "digest": {"value": disposition.digest.value},
            "disposition": "accepted",
        }
        assert _receipt(ledger, review) == disposition
        _privacy_scan(ledger, private_roots, canaries)
        third.kill()
    assert ledger.as_of() == committed
    assert _receipt(ledger, review) == disposition

    codex.write(
        cx_file,
        _codex_rows(ledger, approved, epic_args, child_args, epic_stdout, child_stdout),
    )
    with project.service("recover") as fourth:
        fourth.at("between-scans")
        recovered = ledger.as_of()
        assert [r.record.boundary.provider for r in _observations(recovered)] == [
            Provider.CLAUDE
        ]
        assert project.json("status")["deferred_sources"] == 1
        fourth.resume()
        fourth.at("between-scans")
        settled = ledger.as_of()
        assert project.json("status")["deferred_sources"] == 0
        fourth.stop()

    assert torn.read_bytes() == torn_bytes
    assert _receipt(ledger, torn_marker) is None
    receipts = [
        r.record for r in settled.current if isinstance(r.record, CommandReceipt)
    ]
    assert {r.command.command_id for r in receipts} == {
        CX_EPIC,
        CX_CHILD,
        CL_CHILD,
        relationship_id,
    }
    assert review_ack.read_bytes() == acknowledgment
    assert all(r.disposition is MarkerDisposition.ACCEPTED for r in receipts)
    assert sum(isinstance(r.record, ScopeEnrollment) for r in settled.current) == 3
    assert (
        _receipt(ledger, epic).boundary.ordinal
        < _receipt(ledger, child).boundary.ordinal
    )
    assert sum(isinstance(r.record, UsageObservation) for r in settled.revisions) == 4
    offsets = {s["provider"]: s["offset"] for s in project.json("status")["sources"]}
    assert offsets == {
        "claude": review_file.stat().st_size,
        "codex": cx_file.stat().st_size,
    }

    export = base / "export"
    receipt = _export(project, settled.sequence, export)
    totals = project.json("rollup", "--item", str(EPIC))

    # Replay the exact successful command inputs and unchanged source bytes.
    for args, marker in ((epic_args, epic), (child_args, child), (review_args, review)):
        assert json.loads(project.command(*args)) == {
            "command_id": str(marker.marker_id),
            "status": "accepted",
        }
    project.json("collect-once")
    assert ledger.as_of() == settled

    replay = base / "replay"
    assert _export(project, settled.sequence, replay) == receipt
    assert project.json("rollup", "--item", str(EPIC)) == totals
    for name in (USAGE_NAME, MANIFEST_NAME):
        assert (replay / name).read_bytes() == (export / name).read_bytes()

    exported = (export / USAGE_NAME).read_bytes()
    rows = [json.loads(line) for line in exported.splitlines()]
    manifest = json.loads((export / MANIFEST_NAME).read_bytes())
    assert receipt["row_count"] == manifest["row_count"] == len(rows) == 4
    assert receipt["sha256"] == manifest["sha256"] == sha256(exported).hexdigest()
    assert Counter(
        (row["provider"], row["scope"]["item"]["id"], row["tokens"]["output_tokens"])
        for row in rows
    ) == Counter(
        [
            ("codex", EPIC, 3),
            ("codex", EPIC, 2),
            ("codex", CHILD, 5),
            ("claude", CHILD, 11),
        ]
    )
    for marker, output in ((epic, 3), (child, 5), (review, 11)):
        (usage,) = [
            r.record
            for r in _observations(settled)
            if r.record.boundary.boundary_ref == marker.boundary_ref
        ]
        assert usage.boundary == _receipt(ledger, marker).boundary
        assert usage.tokens.output_tokens == output
    assert len({row["source"] for row in rows}) == 4
    assert {row["observation_revision"] for row in rows} == {1}
    assert {
        entry["provider"]
        for entry in manifest["diagnostics"]
        if entry["code"] == DiagnosticCode.MALFORMED_USAGE.value
    } == {"claude", "codex"}

    direct, inclusive = totals["direct"], totals["inclusive"]
    assert direct["observation_count"] == 2 and direct["tokens"]["output_tokens"] == 5
    assert inclusive["observation_count"] == 4
    assert inclusive["tokens"]["output_tokens"] == sum(
        row["tokens"]["output_tokens"] for row in rows
    )
    assert (
        inclusive["unknown_price_count"]
        == sum(row["price"]["usd"] is None for row in rows)
        == 1
    )
    assert (
        Decimal(inclusive["known_usd"])
        == sum(
            Decimal(row["price"]["usd"])
            for row in rows
            if row["price"]["usd"] is not None
        )
        > 0
    )

    status = project.json("status")
    assert status["sequence"] == status["status_sequence"] == settled.sequence
    assert status["invalid_inbox"] == 1 and status["relationship_halted"] is False
    assert not status["read_gap"] and not status["registration_gap"]
    wal = ledger.database_path.with_name(f"{ledger.database_path.name}-wal")
    assert wal.stat().st_size > 32
    _privacy_scan(ledger, (*private_roots, export, replay), canaries)
    # Approved paths belong in the private configuration only.
    _privacy_scan(ledger, (project.logs, export, replay), (str(sources), str(approved)))
