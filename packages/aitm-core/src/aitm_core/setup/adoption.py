"""Explicit adoption of a committed change to installation authority."""

from dataclasses import dataclass, replace
from tomllib import loads
from uuid import uuid4

from aitm_core.config import CONFIG_PATH, _committed_file
from aitm_core.models.common import CommandResult, LocalOutcome, StoreAnchor
from aitm_core.models.config import CommittedConfig
from aitm_core.services import ServicePorts
from aitm_core.setup.init import (
    InitRequest,
    InitResult,
    _active_installation,
    _branch,
    _check_installed_tip,
    _code_candidate,
    _from_config,
    _load_policy,
    _record_installation,
    prepare_init,
    resume_init,
)
from aitm_core.setup.journal import ReplacementBasis, read_proposal, state_directory
from aitm_core.store.fetch import _direct_ref, _drop_candidate, _fetch, _is_ancestor
from aitm_core.store.gate import RefIdentity, RefMutationKind, _worktrees, ref_gate
from aitm_core.store.objects import Repository
from aitm_core.store.validation import validate_history


@dataclass(frozen=True, slots=True)
class AdoptionProposal:
    request: InitRequest
    ports: ServicePorts = ServicePorts()


@dataclass(frozen=True, slots=True)
class AdoptionResult:
    command: CommandResult
    prior: StoreAnchor
    current: StoreAnchor


def reconfigure(proposal: AdoptionProposal) -> AdoptionResult:
    """Adopt only committed routing with proven old/new planning continuity."""
    request = proposal.request
    probe = Repository(request.repository, "refs/heads/aitm-bootstrap-probe")
    current, accepted = _active_installation(probe)
    repo = current.repository
    code_ref = current.store.code_default_ref
    if (
        _branch(repo, request.default_branch) != code_ref
        or request.code_remote != current.code_remote
    ):
        raise ValueError(
            "Use the established code default to evaluate reconfiguration."
        )
    with ref_gate(repo, RefIdentity(repo.ref), RefMutationKind.PLANNING):
        reread, accepted_now = _active_installation(repo)
        if reread != current or accepted_now != accepted:
            raise ValueError(
                "Another installation change completed. Retry against its authority."
            )
        revision, ref, fetched = _code_candidate(repo, code_ref, current.code_remote)
        try:
            if _is_ancestor(repo, accepted, revision) is not True:
                raise ValueError(
                    "The replacement policy must extend the accepted code history."
                )
            tree = repo.read_tree(revision).tree
            config = CommittedConfig.model_validate(
                loads(_committed_file(repo, tree, CONFIG_PATH).content.decode())
            )
            candidate = _from_config(repo, request, config)
            policy = _load_policy(candidate, revision, ref)
            prior_tip = repo.tip().revision
            next_repo = candidate.repository
            next_tip = next_repo.tip().revision
            if _worktrees(next_repo, RefIdentity(next_repo.ref)):
                raise ValueError("The replacement planning ref is checked out.")
            for installation, tip in ((current, prior_tip), (candidate, next_tip)):
                anchor = installation.store.model_copy(update={"code_default_ref": ref})
                report = validate_history(
                    anchor, tip, repository=installation.repository
                )
                if report.outcome != LocalOutcome.COMPLETED:
                    raise ValueError(
                        report.reason or "Cannot validate both planning histories."
                    )
                _check_installed_tip(installation, tip)
                remote = installation.store.planning_remote
                if remote is not None:
                    seen = _fetch(
                        installation.repository,
                        remote,
                        installation.repository.ref,
                        "adoption",
                    )
                    try:
                        if (
                            seen.observation is None
                            or seen.observation.observed_commit != tip
                        ):
                            raise ValueError(
                                "Reconfiguration requires exact shared and local planning tips."
                            )
                    finally:
                        _drop_candidate(installation.repository, seen)
            if _is_ancestor(next_repo, prior_tip, next_tip) is not True:
                raise ValueError(
                    "Replacement planning history must retain every issued ID and provider reference."
                )
            if candidate.issuer != current.issuer:
                verify = getattr(proposal.ports.init_provider, "verify_adoption", None)
                if (
                    not callable(verify)
                    or verify(current, candidate, prior_tip, next_tip) is not True
                ):
                    raise ValueError(
                        "An issuer change requires verified provider continuity."
                    )
            previous = repo.read_tree(accepted).tree
            old_config = CommittedConfig.model_validate(
                loads(_committed_file(repo, previous, CONFIG_PATH).content.decode())
            )
            old_workflow = _committed_file(repo, previous, old_config.workflow.file)
            if old_workflow != policy.workflow:
                reconcile = getattr(proposal.ports.workflow_cutover, "reconcile", None)
                if (
                    not callable(reconcile)
                    or reconcile(current, candidate, old_workflow, policy) is not True
                ):
                    raise ValueError(
                        "The revised workflow requires verified C98 cutover."
                    )
            if _direct_ref(repo, ref) != revision:
                raise ValueError(
                    "The code default moved while reconfiguration was verified."
                )
            _record_installation(candidate, revision, replace_existing=True)
            result = CommandResult(
                operation_id=uuid4().hex,
                local=LocalOutcome.COMPLETED,
                evidence=(
                    f"Adopted committed routing at {revision}; retained planning history through {prior_tip}.",
                ),
            )
            return AdoptionResult(result, current.store, candidate.store)
        finally:
            if fetched is not None:
                _drop_candidate(repo, fetched)


def prepare_replacement(request: InitRequest, new_branch: str) -> InitResult:
    """Propose new authority only when the original unpublished objects cannot be found."""
    repo = Repository(request.repository, "refs/heads/aitm-bootstrap-probe")
    if (state_directory(repo) / "installation.json").exists():
        raise ValueError("An active store requires continuity-based reconfiguration.")
    journal = read_proposal(repo)
    if journal is not None:
        if journal.replacement is None or journal.anchor.planning_ref != _branch(
            repo, new_branch
        ):
            raise ValueError(
                "An existing bootstrap already holds installation authority."
            )
        request = replace(
            request,
            planning_branch=new_branch,
            planning_remote=journal.anchor.planning_remote,
        )
        proposal = prepare_init(request, replacement=journal.replacement)
        return resume_init(request, proposal.operation_id)
    code_ref = _branch(repo, request.default_branch)
    revision, ref, fetched = _code_candidate(repo, code_ref, request.code_remote)
    try:
        tree = repo.read_tree(revision).tree
        config = CommittedConfig.model_validate(
            loads(_committed_file(repo, tree, CONFIG_PATH).content.decode())
        )
        old = _from_config(repo, request, config)
        _load_policy(old, revision, ref)
        if old.store.planning_ref == _branch(repo, new_branch):
            raise ValueError(
                "The replacement proposal requires a different planning branch."
            )
        basis = ReplacementBasis(anchor=old.store, revision=revision)
        request = replace(
            request,
            planning_branch=new_branch,
            planning_remote=old.store.planning_remote,
        )
        proposal = prepare_init(request, replacement=basis)
        return resume_init(request, proposal.operation_id)
    finally:
        if fetched is not None:
            _drop_candidate(repo, fetched)
