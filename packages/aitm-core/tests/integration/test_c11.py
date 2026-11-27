"""Exercise installation through the installed command and real Git refs."""

import json
import subprocess
from pathlib import Path
from sys import executable
from textwrap import dedent
from types import SimpleNamespace

import pytest

from aitm_core.services import ServicePorts
from aitm_core.setup.init import InitRequest
from aitm_core.store.objects import Repository
from tests.unit.test_c15 import DESCRIPTION, EVENTS, graduated

DEFAULT = "refs/heads/trunk"
RECORDS = "refs/heads/project/records"


def git(root, *args):
    return subprocess.check_output(
        ("git", "-C", str(root), *args), stderr=subprocess.PIPE, text=True
    ).strip()


def init(root, *args):
    process = subprocess.run(
        (
            str(Path(executable).with_name("aitm")),
            "init",
            "--json",
            *args,
        ),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return process.returncode, json.loads(process.stdout)


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, "init", "-q", "-b", "trunk")
    git(tmp_path, "config", "user.name", "C11 fixture")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "commit", "--allow-empty", "-qm", "Code root")
    return tmp_path


@pytest.fixture
def policy_inputs(tmp_path_factory):
    inputs = tmp_path_factory.mktemp("install-inputs")
    review = inputs / "review.toml"
    review.write_text(
        dedent("""\
        [review]
            schema = "aitm.review-policy/v1"
        id = "disposable-test"
        [review.documents]
        binding = "exact-content"
        design_coverage = "own-document"
        design = ["xpr"]
        plan = ["sar"]
        assurances = ["declared-manual"]
        [review.source]
        record_schema = "aitm.source-review/v1"
        independence = "distinct-session"
        assurances = ["declared-manual"]
        [review.exceptions]
        enabled = false
        """)
    )
    workflow = inputs / "workflow.toml"
    workflow.write_text(
        dedent("""\
        schema = "aitm.workflow/v1"
        id = "disposable"
        contract = "fixture.installation/v1"
        [lifecycle]
        terminal = "done"
        non_delivery = "done"
        reopen_design = "design"
        reopen_plan = "plan"
        [recovery]
        design_rework = "design"
        implementation_rework = "dev"
        trip = "plan"
        scope_pivot = "plan"
        """)
        + "".join(
            f'\n[[states]]\nid = "{state}"\nlabel = "{state.title()}"\n'
            for state in ("design", "plan", "dev", "done")
        )
    )
    return ("--review-policy", str(review), "--workflow", str(workflow))


def test_init_resume_preserves_one_genesis_without_committing_policy(
    repository, policy_inputs
):
    root = repository
    code = git(root, "rev-parse", DEFAULT)
    options = (
        "--local",
        "--default-branch",
        "trunk",
        "--planning-branch",
        "project/records",
    )
    code_status, proposal = init(root, *options, *policy_inputs)
    assert proposal["local"] == "completed", proposal
    assert proposal["publication"] == "pending"
    assert code_status == 4
    tip = git(root, "rev-parse", RECORDS)
    genesis = git(root, "rev-list", "--max-parents=0", tip)
    assert git(root, "show", "-s", "--format=%B", genesis) == "aitm-planning-root: v1"

    config = root / ".aitm.toml"
    original = config.read_bytes()
    config.unlink()
    _, resumed = init(root)
    assert resumed["operation_id"] == proposal["operation_id"], resumed
    assert git(root, "rev-parse", RECORDS) == tip
    assert config.read_bytes() == original
    assert git(root, "rev-parse", DEFAULT) == code
    assert git(root, "diff", "--cached", "--name-only") == ""

    git(root, "add", ".aitm.toml", "aitm-workflow.toml")
    git(root, "commit", "-qm", "Land proposed policy")
    _, ready = init(root, *options)
    assert ready["local"] == "completed", ready
    assert ready["publication"] == "not-applicable"
    assert not (root / ".git/aitm/bootstrap.json").read_bytes() == b""
    assert (root / ".git/aitm/installation.json").is_file()

    story = root.parent / f"{root.name}-story"
    git(root, "worktree", "add", "-qb", f"{root.name}-story", str(story), DEFAULT)
    (story / ".aitm.toml").write_text("untrusted story policy")
    (story / "aitm-workflow.toml").write_text("untrusted story workflow")
    _, checked = init(story, *options)
    assert checked["local"] == "completed", checked
    assert checked["operation_id"] == proposal["operation_id"]


@pytest.mark.parametrize("name", ["trunk", "bad..name"])
def test_init_refuses_invalid_or_code_branch(repository, name):
    _, result = init(
        repository, "--local", "--default-branch", "trunk", "--planning-branch", name
    )
    assert result["local"] in {"integrity-error", "refused"}
    assert (
        git(repository, "for-each-ref", "--format=%(refname)", "refs/heads") == DEFAULT
    )
    assert not (repository / ".aitm.toml").exists()


def test_init_preserves_unrecognized_local_planning_history(repository):
    git(repository, "branch", "project/records")
    prior = git(repository, "rev-parse", RECORDS)
    _, result = init(
        repository,
        "--local",
        "--default-branch",
        "trunk",
        "--planning-branch",
        "project/records",
    )
    assert result["local"] in {"integrity-error", "refused", "conflict"}
    assert git(repository, "rev-parse", RECORDS) == prior
    assert not (repository / ".aitm.toml").exists()


def test_hosted_bootstrap_waits_for_landed_policy_and_retained_publication(
    repository, policy_inputs, tmp_path_factory
):
    root = repository
    shared = tmp_path_factory.mktemp("hosted-bootstrap")
    git(shared, "init", "-q", "--bare", "-b", "trunk")
    git(root, "remote", "add", "origin", str(shared))
    git(root, "push", "-q", "origin", "trunk")
    opts = ("--planning-branch", "project/records")

    _, proposal = init(root, *opts, *policy_inputs)
    assert proposal["publication"] == "pending", proposal
    tip = git(root, "rev-parse", RECORDS)
    assert git(shared, "for-each-ref", "--format=%(refname)") == DEFAULT

    git(root, "add", ".aitm.toml", "aitm-workflow.toml")
    git(root, "commit", "-qm", "Prepare policy")
    _, still_pending = init(root, *opts)
    assert still_pending["publication"] == "pending", still_pending
    assert git(shared, "for-each-ref", "--format=%(refname)") == DEFAULT
    git(root, "push", "-q", "origin", "trunk")

    fresh = shared.parent / f"{shared.name}-fresh"
    git(root, "clone", "-q", str(shared), str(fresh))
    _, waiting = init(fresh)
    assert waiting["publication"] == "pending", waiting
    assert git(fresh, "for-each-ref", "--format=%(refname)", "refs/heads") == DEFAULT
    assert not (fresh / ".git/aitm/installation.json").exists()

    alternate = shared.parent / f"{shared.name}-replacement"
    git(root, "clone", "-q", str(shared), str(alternate))
    git(alternate, "config", "user.name", "C11 fixture")
    git(alternate, "config", "user.email", "fixture@example.invalid")
    _, replacement = init(
        alternate,
        "--reconfigure",
        "--replacement-branch",
        "replacement",
        *policy_inputs,
    )
    assert replacement["publication"] == "pending", replacement
    assert "committed-bootstrap-policy" in replacement["pending"]
    stage = alternate / ".git/aitm/replacement"
    assert (stage / ".aitm.toml").exists()
    assert (
        git(alternate, "show", "HEAD:.aitm.toml")
        == (alternate / ".aitm.toml").read_text().strip()
    )
    assert git(shared, "for-each-ref", "--format=%(refname)") == DEFAULT

    _, published = init(root, *opts)
    assert published["operation_id"] == proposal["operation_id"]
    assert published["publication"] == "verified", published
    assert git(shared, "rev-parse", RECORDS) == tip
    _, original_recovered = init(alternate)
    assert original_recovered["local"] == "integrity-error", original_recovered

    _, adopted = init(fresh)
    assert adopted["publication"] == "verified", adopted
    assert git(fresh, "rev-parse", RECORDS) == tip
    assert (fresh / ".git/aitm/installation.json").is_file()

    anchor = fresh / ".git/aitm/store-anchor.json"
    checked = subprocess.run(
        (
            str(Path(executable).with_name("aitm")),
            "--json",
            "planning",
            "validate",
            "--anchor",
            str(anchor),
            "--refresh",
        ),
        cwd=fresh,
        capture_output=True,
        text=True,
        check=False,
    )
    validation = json.loads(checked.stdout)
    assert validation["local"] == "completed", validation
    assert "Shared planning status: verified." in validation["evidence"]

    git(fresh, "config", "user.name", "C11 fixture")
    git(fresh, "config", "user.email", "fixture@example.invalid")
    repo = Repository(fresh, RECORDS)
    seed = repo.create_commit(repo.tip(), {EVENTS: graduated()}, "fixture-story")
    git(fresh, "push", "-q", "origin", f"{seed.revision}:{RECORDS}")
    scope = fresh / "scope.md"
    scope.write_text("Verify publication against the configured planning ref.\n")
    description = subprocess.run(
        (
            str(Path(executable).with_name("aitm")),
            "--json",
            "describe",
            "16",
            "--title",
            "Non-default planning",
            "--as",
            "operator",
            "--want",
            "one route",
            "--so-that",
            "the store remains anchored",
            "--scope-file",
            str(scope),
            "--anchor",
            str(anchor),
        ),
        cwd=fresh,
        capture_output=True,
        text=True,
        check=False,
    )
    assert description.returncode == 0, description.stdout
    assert json.loads(description.stdout)["publication"] == "verified"
    assert "Verify publication" in git(shared, "show", f"{RECORDS}:{DESCRIPTION}")

    git(shared, "update-ref", "-d", RECORDS)
    _, deleted = init(root, *opts)
    assert deleted["publication"] == "pending", deleted
    assert git(shared, "for-each-ref", "--format=%(refname)") == DEFAULT


def test_reconfigure_continuity_preserves_history_and_refuses_a_forged_anchor(
    repository, policy_inputs
):
    root = repository
    opts = ("--local", "--default-branch", "trunk")
    _, proposal = init(
        root, *opts, "--planning-branch", "project/records", *policy_inputs
    )
    assert proposal["publication"] == "pending", proposal
    git(root, "add", ".aitm.toml", "aitm-workflow.toml")
    git(root, "commit", "-qm", "Land original anchor")
    _, ready = init(root, *opts, "--planning-branch", "project/records")
    assert ready["local"] == "completed", ready
    original = (root / ".aitm.toml").read_text()
    stored = Repository(root, RECORDS)
    previous = stored.tip()
    seeded = stored.create_commit(previous, {EVENTS: graduated()}, "fixture-issued-id")
    assert stored.compare_and_swap(seeded.revision, previous.revision)
    tip = seeded.revision
    git(root, "branch", "next", "trunk")
    (root / ".aitm.toml").write_text(original.replace('"project/records"', '"next"'))
    git(root, "commit", "-qam", "Propose replacement ref")
    _, fenced = init(root, *opts, "--planning-branch", "project/records")
    assert fenced["local"] == "integrity-error", fenced
    _, invalid = init(root, *opts, "--reconfigure")
    assert invalid["local"] == "integrity-error", invalid
    old = root / ".git/aitm/store-anchor.json"
    assert json.loads(old.read_bytes())["planning_ref"] == RECORDS

    git(root, "update-ref", "refs/heads/next", tip)
    _, adopted = init(root, *opts, "--reconfigure")
    assert adopted["local"] == "completed", adopted
    assert json.loads(old.read_bytes())["planning_ref"] == "refs/heads/next"
    assert git(root, "rev-parse", "refs/heads/next") == tip
    assert git(root, "rev-parse", RECORDS) == tip
    _, checked = init(root, *opts)
    assert checked["local"] == "completed", checked

    from aitm_core.setup.adoption import AdoptionProposal, reconfigure

    config = root / ".aitm.toml"
    original = config.read_text()
    namespace_line = next(
        line for line in original.splitlines() if line.startswith("numbering_namespace")
    )
    config.write_text(
        original.replace(namespace_line, 'numbering_namespace = "new-issuer"')
    )
    git(root, "commit", "-qam", "Propose issuer namespace")
    _, ordinary = init(root, *opts)
    assert ordinary["local"] == "integrity-error", ordinary
    _, no_proof = init(root, *opts, "--reconfigure")
    assert no_proof["local"] == "integrity-error", no_proof

    def verify(current, candidate, prior_tip, next_tip):
        assert (
            current.issuer.numbering_namespace != candidate.issuer.numbering_namespace
        )
        assert candidate.issuer.numbering_namespace == "new-issuer"
        assert prior_tip == next_tip == seeded.revision
        return True

    adoption = reconfigure(
        AdoptionProposal(
            InitRequest(root, "trunk"),
            ServicePorts(init_provider=SimpleNamespace(verify_adoption=verify)),
        )
    )
    assert adoption.command.local == "completed"
    assert stored.read_blobs(seeded.tree, (EVENTS,))[EVENTS] == graduated()
    assert git(root, "rev-parse", "refs/heads/next") == seeded.revision
    _, switched = init(root, *opts)
    assert switched["local"] == "completed", switched
