"""Exercise the exact macOS Grok installation in a disposable, owner-scoped run."""

from __future__ import annotations

import argparse
import ctypes
import hmac
import json
import os
import re
import secrets
import shlex
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from uuid import uuid4

from aitm_usage._isolated_qualification import (
    _GROK_DIGEST,
    _NAMESPACE,
    _canonical,
    _install_isolated_profile,
    _NativeClosure,
    _OpenedExecutable,
    _PilotLayout,
    _prepare_isolated_issuer,
)
from aitm_usage.install import _BSDProcessInfo, _libproc, _process_identity
from aitm_usage.ledger import (
    LedgerError,
    _check_acl,
    _pin_directory,
    validate_private_path,
)
from aitm_usage.monitor_registry import Registry, SourceApprovalRequest
from aitm_usage.monitor_scope import ScopeState
from aitm_usage.scopes import _publish, _read_private
from aitm_usage.sources.adapter import GrokOrigin, SourceRoot
from aitm_usage.sources.grok import GrokAdapter, _update


def _fail(stage: str) -> LedgerError:
    return LedgerError(f"Isolated Grok pilot failed at {stage}")


def _put_private(root: Path, name: str, data: bytes) -> None:
    with _pin_directory(root) as pin:
        if not _publish(pin, name, data):
            raise _fail("scratch publication")


def _load(root: Path, name: str) -> bytes:
    with _pin_directory(root) as pin:
        raw = _read_private(pin, name)
    if raw is None:
        raise _fail("private evidence read")
    return raw


def _under_process(child: int) -> bool:
    current = os.getpid()
    for _ in range(24):
        info = _BSDProcessInfo()
        size = ctypes.sizeof(info)
        if (
            _libproc().proc_pidinfo(current, 3, 0, ctypes.byref(info), size) != size
            or info.pid != current
            or info.uid != os.geteuid()
            or info.parent_pid < 2
            or info.parent_pid == current
        ):
            return False
        if info.parent_pid == child:
            return True
        current = info.parent_pid
    return False


def _hook(control: Path) -> None:
    row = json.loads(sys.stdin.buffer.read(65536))
    pending = json.loads(_load(control, "pending.json"))
    event, session, prompt = (
        row.get(key) for key in ("hookEventName", "sessionId", "promptId")
    )
    if (
        event != "user_prompt_submit"
        or os.environ.get("GROK_HOOK_EVENT") != event
        or session != os.environ.get("GROK_SESSION_ID")
        or session != pending["session"]
        or row.get("workspaceRoot") != pending["workspace"]
        or os.environ.get("AITM_PILOT_NONCE") != pending["nonce"]
        or type(prompt) is not str
        or not re.fullmatch(r"[0-9A-Fa-f-]{36}", prompt)
    ):
        raise _fail("hook envelope")
    deadline = monotonic() + 3
    while not (control / "child.json").exists() and monotonic() < deadline:
        sleep(0.02)
    child = json.loads(_load(control, "child.json"))["pid"]
    process = _process_identity(child)
    if (
        process is None
        or str(process.executable) != pending["image"]
        or not _under_process(child)
    ):
        raise _fail("live child custody")
    body = {
        "event": event,
        "session": session,
        "prompt": prompt,
        "nonce": pending["nonce"],
        "started": process.started.isoformat(),
        "pid": process.pid,
    }
    sealed = {
        "body": body,
        "tag": hmac.digest(
            _load(control, "receipt.key"), _canonical(body), "sha256"
        ).hex(),
    }
    _put_private(control, "one-use-receipt.json", _canonical(sealed))


def _completed_carrier(layout: _PilotLayout, session: str) -> _NativeClosure:
    control = layout.control
    pending = json.loads(_load(control, "pending.json"))
    child = json.loads(_load(control, "child.json"))
    receipt = _load(control, "one-use-receipt.json")
    sealed = json.loads(receipt)
    body = sealed["body"]
    expected_tag = hmac.digest(
        _load(control, "receipt.key"), _canonical(body), "sha256"
    ).hex()
    if (
        _canonical(sealed) != receipt
        or not hmac.compare_digest(expected_tag, sealed["tag"])
        or body["session"] != session
        or body["nonce"] != pending["nonce"]
        or body["event"] != "user_prompt_submit"
        or body["pid"] != child["pid"]
        or body["started"] != child["started"]
    ):
        raise _fail("receipt authentication")
    directory = layout.native_session(session)
    if tuple(path for path in layout.capture.iterdir() if path.is_dir()) != (
        directory.parent,
    ) or tuple(path for path in directory.parent.iterdir() if path.is_dir()) != (
        directory,
    ):
        raise _fail("exclusive native carrier")
    raw = _load(directory, "updates.jsonl")
    usage = _load(directory, "usage.json")
    if not raw.endswith(b"\n") or not usage:
        raise _fail("native closure")
    rows = tuple(_update(json.loads(line), session) for line in raw.splitlines())
    hooks = [i for i, row in enumerate(rows) if row.kind == "hook_execution"]
    finals = [i for i, row in enumerate(rows) if row.kind == "turn_completed"]
    if len(hooks) != 1 or len(finals) != 1 or hooks[0] >= finals[0]:
        raise _fail("native hook and completion sequence")
    hook, done = rows[hooks[0]], rows[finals[0]]
    runs = hook.fields["runs"]
    started = datetime.fromisoformat(child["started"])
    if (
        hook.fields.get("event_name") != body["event"]
        or hook.fields.get("prompt_id") != body["prompt"]
        or type(runs) is not list
        or len(runs) != 1
        or runs[0]["status"]["status"] != "success"
        or done.fields.get("prompt_id") != body["prompt"]
        or done.fields.get("stop_reason") != "end_turn"
        or not started <= hook.time <= done.time <= datetime.now(UTC)
    ):
        raise _fail("native receipt join")
    return _NativeClosure(
        session,
        body["prompt"],
        hook.event_id,
        started,
        sha256(raw).hexdigest(),
        sha256(usage).hexdigest(),
        sha256(receipt).hexdigest(),
    )


def _capture(
    layout: _PilotLayout,
    image: _OpenedExecutable,
    session: str,
    provider: Path,
    workspace: Path,
) -> _NativeClosure:
    control = layout.control
    hook_root = workspace / ".grok" / "hooks"
    hook_root.parent.mkdir(mode=0o700)
    hook_root.mkdir(mode=0o700)
    command = shlex.join(
        (sys.executable, str(Path(__file__).resolve()), "--hook", str(control))
    )
    _put_private(
        hook_root,
        "prompt.json",
        _canonical(
            {
                "hooks": {
                    "UserPromptSubmit": [
                        {
                            "hooks": [
                                {"type": "command", "command": command, "timeout": 10},
                            ]
                        }
                    ]
                }
            }
        ),
    )
    trust = f"[folders.{json.dumps(str(workspace))}]\ntrusted = true\ndecided_at = {int(datetime.now(UTC).timestamp())}\n"
    _put_private(provider, "trusted_folders.toml", trust.encode())
    _put_private(
        provider,
        "config.toml",
        b"[cli]\nauto_update = false\n[compat.claude]\nhooks = false\n[compat.cursor]\nhooks = false\n",
    )
    nonce = secrets.token_hex(32)
    _put_private(control, "receipt.key", secrets.token_bytes(32))
    _put_private(
        control,
        "pending.json",
        _canonical(
            {
                "session": session,
                "nonce": nonce,
                "workspace": str(workspace),
                "image": str(image.path),
            }
        ),
    )
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(provider),
        "GROK_HOME": str(provider),
        "GROK_DISABLE_AUTOUPDATER": "1",
        "AITM_PILOT_NONCE": nonce,
        # The hook runs the same audited Python source with the same package.
        "PYTHONPATH": str(
            Path(__file__).resolve().parents[2] / "packages" / "aitm-usage" / "src"
        ),
    }
    layout.check()
    image.check()
    arguments = [
        str(image.path),
        "--leader-socket",
        str(provider / "pilot.sock"),
        "--session-id",
        session,
        "--max-turns",
        "1",
        "--tools",
        "",
        "--no-subagents",
        "--disable-web-search",
        "--output-format",
        "streaming-json",
        "-p",
        "Reply with the single word ready. Do not use any tools.",
    ]
    with (
        (control / "stdout").open("xb") as stdout,
        (control / "stderr").open("xb") as stderr,
    ):
        with subprocess.Popen(
            arguments,
            env=env,
            cwd=workspace,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            umask=0o077,
        ) as child:
            try:
                identity = None
                deadline = monotonic() + 4
                while (
                    identity is None and monotonic() < deadline and child.poll() is None
                ):
                    current = _process_identity(child.pid)
                    if current is not None and current.executable == image.path:
                        identity = current
                    else:
                        sleep(0.02)
                if identity is None:
                    raise _fail("opened executable observation")
                _put_private(
                    control,
                    "child.json",
                    _canonical(
                        {
                            "pid": identity.pid,
                            "started": identity.started.isoformat(),
                        }
                    ),
                )
                if child.wait(timeout=90) != 0:
                    raise _fail("native process completion")
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait()
    layout.check()
    image.check()
    return _completed_carrier(layout, session)


def _prove(
    writer: Registry,
    layout: _PilotLayout,
    image: _OpenedExecutable,
    closure: _NativeClosure,
) -> dict[str, object]:
    key = layout.control / "owner"
    subprocess.run(
        ["/usr/bin/ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
        check=True,
        timeout=10,
        capture_output=True,
    )
    issuer = _prepare_isolated_issuer(
        writer, layout, image, closure, key.with_suffix(".pub").read_bytes()
    )

    def commit(operation: str, generation: int):
        proposal = issuer.proposal(
            operation, generation, datetime.now(UTC) + timedelta(minutes=5)
        )
        signature = subprocess.run(
            ["/usr/bin/ssh-keygen", "-Y", "sign", "-n", _NAMESPACE, "-f", str(key)],
            input=proposal,
            check=True,
            timeout=10,
            capture_output=True,
        ).stdout
        if operation == "revoke":
            issuer.revoke(proposal, signature)
        else:
            proof = _install_isolated_profile(issuer, proposal, signature)
            if proof is not writer._live_profile.installations[0]:
                raise _fail("exact installed proof")

    commit("activate", 1)
    evidence = writer.source_evidence()
    path = layout.native_session(closure.session) / "updates.jsonl"
    origin = GrokOrigin(
        session_id=closure.session,
        system="Darwin",
        architecture="arm64",
        version="1.0.77",
        build="50ca579fa996",
        executable_digest=image.sha256,
        format_version=1,
        lineage_id=closure.session,
        incarnation=evidence.pseudonymize(
            "isolated-grok-incarnation-v1", closure.updates_sha256
        ),
    )
    receipt_ref = evidence.pseudonymize(
        "isolated-grok-prompt-v1", closure.receipt_sha256
    )
    reader = GrokAdapter(
        lambda candidate: origin if candidate == path else None,
        lambda *marker: (
            receipt_ref
            if marker == (closure.session, closure.prompt, closure.event)
            else None
        ),
    )
    source = uuid4()
    writer.approve_source(
        SourceApprovalRequest(
            source,
            "grok",
            "grok-build-macos",
            "Darwin",
            "arm64",
            "1.0.77",
            1,
            str(layout.capture),
        )
    )
    (locator,) = reader.discover(
        SourceRoot(layout.capture, closure.process_started, (), evidence)
    )
    scopes = ScopeState(writer, grok_reader=reader)
    batch = scopes.read_source(source, locator)
    if len(batch.observations) != 1 or len(batch.boundaries) != 1 or batch.diagnostics:
        raise _fail("authenticated source read")
    commit("revoke", 2)
    from aitm_usage._monitor_qualification import _LiveSourceUnavailable

    refusal = None
    try:
        scopes.view(batch)
    except _LiveSourceUnavailable as error:
        refusal = error
    if type(refusal) is not _LiveSourceUnavailable or refusal.decision is not None:
        raise _fail("post-revoke recheck")
    return {
        "schema": "aitm.isolated-grok-pilot/v1",
        "status": "pass",
        "provider": "grok",
        "system": "Darwin",
        "architecture": "arm64",
        "version": "1.0.77",
        "build": "50ca579fa996",
        "executable_sha256": image.sha256,
        "native_format": 1,
        "live_owned_image": True,
        "signed_owner_generation": True,
        "writer_sealed_current_revision": True,
        "receipt_closure_join": True,
        "qualified_scope_observations": len(batch.observations),
        "qualified_scope_boundaries": len(batch.boundaries),
        "post_revoke_refused": True,
        "journal_cursor_exercised": False,
    }


def _source_binding() -> dict[str, str]:
    runner = Path(__file__).resolve()
    repo = runner.parents[2]
    package = repo / "packages" / "aitm-usage" / "src" / "aitm_usage"
    module = sys.modules[_install_isolated_profile.__module__]
    issuer = Path(module.__file__).resolve()
    with_source = subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(repo),
            "status",
            "--porcelain",
            "--untracked-files=no",
        ],
        capture_output=True,
        check=True,
        timeout=10,
    ).stdout
    if with_source or issuer.parent != package:
        raise _fail("exact source binding")
    head, tree = subprocess.run(
        ["/usr/bin/git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        capture_output=True,
        check=True,
        timeout=10,
        text=True,
    ).stdout.splitlines()
    return {
        "commit": head,
        "tree": tree,
        "runner_sha256": sha256(runner.read_bytes()).hexdigest(),
        "issuer_sha256": sha256(issuer.read_bytes()).hexdigest(),
    }


def _read_login(auth_file: Path) -> bytes:
    validate_private_path(auth_file)
    with os.fdopen(
        os.open(auth_file, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb"
    ) as secret:
        info = os.fstat(secret.fileno())
        _check_acl(secret.fileno())
        content = secret.read(65537)
        if (
            not os.path.samestat(info, auth_file.lstat())
            or not content
            or len(content) > 65536
        ):
            raise _fail("owner-authorized login custody")
        validate_private_path(auth_file)
        return content


def _pilot(binary: Path, auth_file: Path) -> dict[str, object]:
    from platform import machine, system

    if system() != "Darwin" or machine() != "arm64":
        raise _fail("exact host selection")
    with TemporaryDirectory(prefix="aitm-grok-pilot-", dir="/private/tmp") as base:
        root = Path(base)
        control, provider, workspace, images = (
            root / name for name in ("c", "p", "w", "executable")
        )
        capture = provider / "sessions"
        for directory in (control, provider, workspace, images, capture):
            directory.mkdir(mode=0o700)
        layout = _PilotLayout.create(control, provider, workspace, images, capture)
        # Only the already authorized login state is copied. It dies with the scratch root.
        _put_private(provider, "auth.json", _read_login(auth_file))
        with _OpenedExecutable.copy(binary, images / "grok") as image:
            if image.sha256 != _GROK_DIGEST:
                raise _fail("exact provider binary")
            closure = _capture(layout, image, str(uuid4()), provider, workspace)
            with Registry(root / "writer").writer() as writer:
                return _prove(writer, layout, image, closure)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grok", type=Path)
    parser.add_argument("--auth-file", type=Path)
    parser.add_argument("--hook", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        if args.hook is not None and args.grok is None and args.auth_file is None:
            _hook(args.hook)
        elif args.hook is None and args.grok is not None and args.auth_file is not None:
            binding = _source_binding()
            evidence = _pilot(args.grok, args.auth_file)
            if _source_binding() != binding:
                raise _fail("end-to-end source binding")
            print(_canonical(evidence | {"source": binding}).decode())
        else:
            parser.error(
                "provide the exact installed Grok executable and its owner-authorized login file"
            )
    except Exception as error:
        print(
            str(error)
            if type(error) is LedgerError
            else f"Isolated Grok pilot failed ({type(error).__name__})",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
