"""Exercise forward repair and independent validation through the installed CLI."""

from json import dumps, loads
from os import environ
from pathlib import Path
from shlex import quote
from shutil import which
from subprocess import run

from aitm_core.models.common import LocalOutcome
from aitm_core.services import refresh
from aitm_core.store.validation import validate_history
from tests.integration.test_c08 import PLANNING, PLANNING_REMOTE, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import cloned


def planning(topology, scratch, action, *arguments, environment=None):
    scratch.mkdir(exist_ok=True)
    installation = topology.policy.installation
    anchor_file = scratch / "anchor.json"
    anchor_file.write_text(installation.store.model_dump_json())
    descriptor = scratch / "installation.json"
    descriptor.write_text(
        dumps(
            {
                "code_repository": installation.code_repository,
                "planning_repository": installation.planning_repository,
                "bootstrap_source": installation.bootstrap_source,
                "issuer": installation.issuer.model_dump(),
                "code_remote": installation.code_remote,
                "code_remote_ref": installation.code_remote_ref,
            }
        )
    )
    cli = which("aitm")
    assert cli is not None
    return run(
        [
            cli,
            "--json",
            "planning",
            action,
            "--anchor",
            str(anchor_file),
            "--installation",
            str(descriptor),
            *arguments,
        ],
        cwd=topology.local,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )


def test_maximal_prefix_is_independently_recomputed(topology, tmp_path):
    installation = topology.policy.installation
    repo = installation.repository
    path = ".aitm/README.md"
    prior = topology.advance_planning(path, b"previously observed\n")
    assert refresh(installation).planning.observed_commit == prior
    unpublished = repo.create_commit(
        repo.tip(), {path: b"unpublished\n"}, "local-draft"
    )
    git(topology.local, "update-ref", PLANNING, unpublished.revision, prior)
    maximal = topology.advance_planning(path, b"new maximal valid content\n")
    bad = topology.advance_planning("outside.txt", b"invalid tail\n")

    stale = planning(topology, tmp_path / "repair", "repair", "--expected-tip", prior)
    assert loads(stale.stdout)["local"] == "conflict", stale.stdout
    assert topology.writer() == unpublished.revision

    shim = tmp_path / "shim"
    shim.mkdir()
    executable = which("git")
    assert executable
    wrapper = shim / "git"
    wrapper.write_text(
        f'#!/bin/sh\nif [ "$3" = push ]; then exit 69; fi\nexec {quote(executable)} "$@"\n'
    )
    wrapper.chmod(0o755)
    uncertain = planning(
        topology,
        tmp_path / "repair",
        "repair",
        "--expected-tip",
        bad,
        environment=dict(environ, PATH=f"{shim}:{environ['PATH']}"),
    )
    pending = loads(uncertain.stdout)
    assert pending["local"] == "completed" and pending["publication"] == "pending"
    prepared = repo.tip()
    assert repo.parent(prepared) == bad

    repaired = planning(topology, tmp_path / "repair", "repair", "--expected-tip", bad)
    observed = loads(repaired.stdout)
    assert observed["local"] == "completed", repaired.stdout
    assert observed["publication"] == "verified"
    new = repo.tip()
    assert new == prepared
    assert repo.parent(new) == bad
    assert repo.read_blobs(new.tree, (path, "outside.txt")) == {
        path: b"new maximal valid content\n",
        "outside.txt": None,
    }
    assert (
        git(topology.local, "rev-parse", observed["recovery"]) == unpublished.revision
    )
    remote = Path(git(topology.local, "remote", "get-url", PLANNING_REMOTE))
    assert git(remote, "rev-parse", PLANNING) == new.revision

    fresh = cloned(topology, tmp_path)
    validated = planning(fresh, tmp_path / "fresh", "validate", "--refresh")
    assert loads(validated.stdout)["local"] == "completed", validated.stdout
    assert fresh.writer() == new.revision

    receipt_path = next(
        line
        for line in git(
            topology.local,
            "ls-tree",
            "-r",
            "--name-only",
            new.revision,
        ).splitlines()
        if line.startswith(".aitm/repairs/")
    )
    receipt = repo.read_blobs(new.tree, (receipt_path,))[receipt_path]
    parsed = loads(receipt)
    assert parsed["valid_prefix"]["commit"] == maximal

    for winner, proof in (
        (prior, receipt),
        (maximal, receipt.replace(maximal.encode(), prior.encode())),
    ):
        alternate = repo.create_commit(
            repo.read_tree(winner), {receipt_path: proof}, "forged"
        )
        forged = git(
            topology.local,
            "commit-tree",
            alternate.tree,
            "-p",
            bad,
            "-m",
            "Forged restoration",
        )
        response = validate_history(installation.store, forged, repository=repo)
        assert response.outcome == LocalOutcome.INTEGRITY_ERROR
        assert response.first_invalid == bad

    wrong_ancestry = validate_history(
        installation.store, topology.old_code, repository=repo
    )
    assert wrong_ancestry.outcome == LocalOutcome.INTEGRITY_ERROR
    assert wrong_ancestry.reason == "code-ancestry"
