"""Exercise installed scoped sync with disposable local and hosted Git repositories."""

import json
from os import environ
from pathlib import Path
from shlex import quote
from shutil import which

from aitm_core.services import ServicePorts, preflight_policy
from aitm_core.setup.init import _record_installation
from aitm_core.store.objects import Repository
from aitm_core.store.publication import Publisher
from tests.integration.test_c08 import PLANNING, PLANNING_REMOTE, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import cloned
from tests.integration.test_c16 import cli
from tests.unit.test_c15 import EVENTS, graduated

PLAN = ".aitm/stories/000/16/plan/current.md"
ATTACHMENT = ".aitm/stories/000/16/attachments/note.txt"


def test_sync_and_reconcile(topology, tmp_path, monkeypatch):
    topology.advance_planning(EVENTS, graduated())
    topology.advance_planning(PLAN, b"Shared plan\n")
    topology.advance_planning(ATTACHMENT, b"Original attachment\n")
    installation = topology.policy.installation
    observation = preflight_policy(installation)
    assert observation.policy is not None, observation.reason
    _record_installation(installation, observation.policy.revision)
    local = topology.local

    bound = cli(
        local, "bind", "16", "--session", "writer", "--path", PLAN, "--path", ATTACHMENT
    )
    assert bound["local"] == "completed", bound
    lease = json.loads(bound["evidence"][0])
    options = (
        "16",
        "--binding",
        lease["identity"],
        "--generation",
        str(lease["generation"]),
        "--session",
        "writer",
    )
    path = local / PLAN
    path.write_bytes(b"First authored edit\n")
    generated = local / ".aitm/stories/000/16/story.md"
    generated.write_bytes(b"Scratch generated edit\n")
    refused = cli(local, "sync", *options, "--path", EVENTS)
    assert refused["local"] == "integrity-error", refused
    result = cli(local, "sync", *options, "--push", "--path", PLAN)
    assert result["publication"] == "verified", result
    assert any("Ignored unbound workspace path" in line for line in result["evidence"])
    repo = Repository(local, PLANNING)
    assert repo.read_blobs(repo.tip().tree, (PLAN, EVENTS, ATTACHMENT)) == {
        PLAN: b"First authored edit\n",
        EVENTS: graduated(),
        ATTACHMENT: b"Original attachment\n",
    }

    (local / ATTACHMENT).unlink()
    failed = cli(local, "unbind", *options)
    assert failed["local"] == "refused", failed
    deleted = cli(local, "sync", *options, "--delete", ATTACHMENT)
    assert deleted["publication"] == "verified", deleted
    assert repo.read_blobs(repo.tip().tree, (ATTACHMENT,))[ATTACHMENT] is None

    rival = cloned(topology, tmp_path)
    rival_repo = Repository(rival.local, PLANNING)
    remote_tip = rival_repo.create_commit(
        rival_repo.tip(), {PLAN: b"Rival plan\n"}, "rival"
    )
    remote = git(local, "remote", "get-url", PLANNING_REMOTE)
    hook_path = (
        Path(git(local, "rev-parse", "--path-format=absolute", "--git-path", "hooks"))
        / "pre-push"
    )
    assert not hook_path.exists()
    marker = tmp_path / "race-triggered"
    hook_path.write_text(
        "#!/bin/sh\n"
        f"if test ! -e {quote(str(marker))}; then\n"
        f"  touch {quote(str(marker))}\n"
        "  unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR\n"
        f"  git -C {quote(str(rival.local))} push --quiet --no-verify -- {quote(remote)} "
        f"{quote(f'{remote_tip.revision}:{PLANNING}')}\n"
        "fi\n"
    )
    hook_path.chmod(0o755)
    path.write_bytes(b"Local competing plan\n")
    contested = cli(local, "sync", *options, "--push", "--path", PLAN)
    assert contested["publication"] == "pending", contested
    assert contested["recovery"]
    retained = git(local, "rev-parse", contested["recovery"])
    assert git(Path(remote), "rev-parse", PLANNING) == remote_tip.revision
    reconcile_args = (
        "--reconcile",
        contested["operation_id"],
        "--retained",
        retained,
        "--expected-shared",
        remote_tip.revision,
        "--path",
        PLAN,
    )
    inspect = cli(local, "sync", *options, "--reconcile", contested["operation_id"])
    assert inspect["local"] == "conflict", inspect
    copies = Path(inspect["recovery"])
    assert (copies / "local" / PLAN).read_bytes() == b"Local competing plan\n"
    assert (copies / "shared" / PLAN).read_bytes() == b"Rival plan\n"

    refused_deletion = cli(
        local, "sync", *options, *reconcile_args, "--delete", PLAN, "--resolve"
    )
    assert refused_deletion["local"] == "conflict", refused_deletion
    assert git(Path(remote), "rev-parse", PLANNING) == remote_tip.revision

    path.write_bytes(b"Explicit merged plan\n")
    shim = tmp_path / "lost-ack"
    shim.mkdir()
    real_git = which("git")
    assert real_git is not None
    log = shim / "calls"
    wrapper = shim / "git"
    wrapper.write_text(
        f'#!/bin/sh\nif [ "$3" = push ]; then\nprintf "push\\n" >> {quote(str(log))}\n'
        f'{quote(real_git)} "$@"\nexit 69\nfi\n'
        f'if [ "$3" = ls-remote ]; then printf "observe\\n" >> {quote(str(log))}; fi\n'
        f'exec {quote(real_git)} "$@"\n'
    )
    wrapper.chmod(0o755)
    with monkeypatch.context() as context:
        context.setenv("PATH", f"{shim}:{environ['PATH']}")
        resolved = cli(local, "sync", *options, *reconcile_args, "--resolve")
    commands = log.read_text().splitlines()
    assert commands.count("push") == 1
    assert "observe" in commands[commands.index("push") + 1 :]
    assert resolved["publication"] == "verified", resolved
    assert resolved["operation_id"] != contested["operation_id"]
    assert repo.read_blobs(repo.tip().tree, (PLAN,))[PLAN] == b"Explicit merged plan\n"
    assert git(local, "rev-parse", contested["recovery"]) == retained
    assert (
        Publisher(installation).request(resolved["operation_id"]).owner.binding
        == lease["identity"]
    )

    git(rival.local, "fetch", "--quiet", "--", remote, PLANNING)
    later = rival_repo.create_commit(
        rival_repo.read_tree(git(rival.local, "rev-parse", "FETCH_HEAD")),
        {PLAN: b"New shared plan\n"},
        "advance-shared",
    )
    git(
        rival.local,
        "push",
        "--quiet",
        "--no-verify",
        "--",
        remote,
        f"{later.revision}:{PLANNING}",
    )
    path.write_bytes(b"Changes based on prior plan\n")
    stale_base = cli(local, "unbind", *options)
    assert stale_base["local"] == "conflict", stale_base
    retained_bodies = Path(stale_base["recovery"])
    assert (
        retained_bodies / "local" / PLAN
    ).read_bytes() == b"Changes based on prior plan\n"
    assert (retained_bodies / "shared" / PLAN).read_bytes() == b"New shared plan\n"
    path.write_bytes(b"New shared plan\n")
    assert cli(local, "sync", *options)["local"] == "completed"

    from aitm_core.cli.sync import handle

    observed = []
    original = Publisher._push

    def observe_push(publisher, *args):
        observed.append(args)
        return original(publisher, *args)

    monkeypatch.setattr(Publisher, "_push", observe_push)
    monkeypatch.chdir(local)
    path.write_bytes(b"One more edit\n")
    applied = handle(
        ("sync",),
        (*options, "--push", "--path", PLAN),
        ports=ServicePorts(action_retry=None),
    )
    assert applied.publication == "verified"
    assert len(observed) == 1
    assert "action-retry" in applied.pending
    released = cli(local, "unbind", *options)
    assert released["local"] == "completed", released
    stale = cli(local, "sync", *options, "--path", PLAN)
    assert stale["local"] == "conflict", stale
    unavailable = cli(local, "sync", "--entity", "entity-without-adapter")
    assert unavailable["local"] == "unavailable", unavailable
