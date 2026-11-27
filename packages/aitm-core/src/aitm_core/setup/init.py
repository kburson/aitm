"""Prepare and resume disposable local installation under the anchored policy."""

from dataclasses import dataclass
from json import dumps
from json import loads as json_loads
from os import fsdecode
from pathlib import Path
from textwrap import dedent
from tomllib import loads
from typing import Protocol
from uuid import uuid4

from aitm_core.config import (
    CONFIG_PATH,
    CommittedFile,
    PolicySnapshot,
    _committed_file,
    resolve_policy,
)
from aitm_core.machine.profile import load_profile
from aitm_core.models.common import (
    CommandResult,
    LocalOutcome,
    PublicationOutcome,
    RefObservation,
    RefreshResult,
    StoreAnchor,
)
from aitm_core.models.config import BacklogIssuer, CommittedConfig
from aitm_core.providers.githost import ProtectionRules
from aitm_core.services import (
    ServicePorts,
    _unique_coordinates,
    load_installation,
    refresh,
)
from aitm_core.setup.journal import (
    BootstrapProposal,
    ReplacementBasis,
    prepare_file,
    read_proposal,
    record_proposal,
    state_directory,
)
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.fetch import (
    Freshness,
    _CandidateInstallation,
    _direct_ref,
    _drop_candidate,
    _fetch,
    _is_ancestor,
)
from aitm_core.store.gate import (
    RefIdentity,
    RefMutationKind,
    _atomic_write,
    ref_gate,
)
from aitm_core.store.installation import Installation
from aitm_core.store.objects import Repository
from aitm_core.store.validation import validate_history

WORKFLOW_PATH = "aitm-workflow.toml"
LANDING_COMMANDS = (
    f"git add -- {CONFIG_PATH} {WORKFLOW_PATH}",
    f'git commit -m "Configure AITM" -- {CONFIG_PATH} {WORKFLOW_PATH}',
)


@dataclass(frozen=True, slots=True)
class InitRequest:
    repository: Path
    default_branch: str
    planning_branch: str = "planning"
    review_policy: str | None = None
    workflow: str | None = None
    code_remote: str | None = None
    planning_remote: str | None = None


@dataclass(frozen=True, slots=True)
class InitResult:
    command: CommandResult
    installation: Installation | None = None
    policy: PolicySnapshot | None = None


class InitHooks(Protocol):
    def install(self, context: Installation) -> tuple[str, ...]: ...


def _branch(repo: Repository, branch: str) -> str:
    ref = f"refs/heads/{branch}"
    if branch.startswith("-") or repo._run("check-ref-format", ref).returncode != 0:
        raise ValueError(f"Invalid branch name: {branch!r}.")
    return ref


def _installation(repo: Repository, proposal: BootstrapProposal) -> Installation:
    return Installation(
        repository=repo,
        store=proposal.anchor,
        code_repository=proposal.code_repository,
        planning_repository=proposal.planning_repository,
        issuer=proposal.issuer,
        bootstrap_source="explicit-default"
        if proposal.code_remote is None
        else "remote-default",
        code_remote=proposal.code_remote,
        code_remote_ref=proposal.anchor.code_default_ref
        if proposal.code_remote
        else None,
    )


def _config(
    anchor: StoreAnchor,
    identity: str,
    request: InitRequest,
) -> str:
    assert request.review_policy is not None
    trunk = (
        f"{request.code_remote}/{request.default_branch}"
        if request.code_remote
        else request.default_branch
    )
    remote = (
        f"remote = {dumps(request.planning_remote, ensure_ascii=False)}"
        if request.planning_remote
        else ""
    )
    return (
        dedent(f"""\
        [store]
        code_repository = {dumps(identity)}
        repository = {dumps(identity)}
        branch = {dumps(request.planning_branch, ensure_ascii=False)}
        trunk = {dumps(trunk, ensure_ascii=False)}
        {remote}
        uuid = {dumps(anchor.store_uuid)}
        root_commit = {dumps(anchor.root_commit)}

        [enforcement]
        mode = "advisory"
        [limits]
        leaf_agent_hours = 4
        expansions_per_attempt = 1
        idle_gap_minutes = 15
        [providers]
        backlog = "local"
        backlog_repository = {dumps(identity)}
        numbering_namespace = {dumps(anchor.store_uuid)}
        githost = "none"
        [extensions]
        enabled = []
        [test]
        command = "uv run pytest"
        inputs = []
        assurance = "captured-export"
        prepare_network = "deny"
        [workflow]
        file = "{WORKFLOW_PATH}"

        """)
        + request.review_policy
    )


def _allocate(
    repo: Repository, code_ref: str, request: InitRequest
) -> BootstrapProposal:
    if request.review_policy is None or request.workflow is None:
        raise ValueError("A new installation requires --review-policy and --workflow.")
    operation_id = uuid4().hex
    store_uuid = str(uuid4())
    identity = f"aitm:{store_uuid}"
    empty_tree = repo._git("mktree", data=b"").decode("ascii").strip()
    genesis = (
        repo._git("commit-tree", empty_tree, "-m", "aitm-planning-root: v1")
        .decode("ascii")
        .strip()
    )
    anchor = StoreAnchor(
        store_uuid=store_uuid,
        code_default_ref=code_ref,
        planning_ref=repo.ref,
        planning_remote=request.planning_remote,
        root_commit=genesis,
    )
    config = _config(anchor, identity, request)
    settings = CommittedConfig.model_validate(loads(config))
    issuer = BacklogIssuer(
        backlog=settings.providers.backlog,
        backlog_repository=settings.providers.backlog_repository,
        numbering_namespace=settings.providers.numbering_namespace,
    )
    state = {
        "schema": "aitm.store/v1",
        "store_uuid": store_uuid,
        "root_commit": genesis,
        "provider": issuer.model_dump(mode="json"),
        "operation_id": operation_id,
    }
    tip = repo.create_commit(
        repo.read_tree(genesis),
        {
            ".aitm/README.md": b"# AITM planning store\n",
            ".aitm/store.json": (dumps(state, sort_keys=True) + "\n").encode(),
        },
        operation_id,
    )
    proposal = BootstrapProposal(
        operation_id=operation_id,
        anchor=anchor,
        initial_tip=tip.revision,
        code_repository=identity,
        planning_repository=identity,
        issuer=issuer,
        config=config,
        workflow=request.workflow,
        code_remote=request.code_remote,
    )
    install = _installation(repo, proposal)
    load_profile(
        PolicySnapshot(
            genesis,
            empty_tree,
            CommittedFile(CONFIG_PATH, config.encode()),
            CommittedFile(WORKFLOW_PATH, request.workflow.encode()),
            settings,
            install.routing,
            install.routing,
        )
    )
    return proposal


def prepare_init(
    request: InitRequest,
    *,
    replacement: ReplacementBasis | None = None,
) -> BootstrapProposal:
    """Allocate one proposal before exposing its objects or prepared files."""
    repo = Repository(request.repository, "refs/heads/aitm-bootstrap-probe")
    target = _branch(repo, request.planning_branch)
    code_ref = _branch(repo, request.default_branch)
    if code_ref == target:
        raise ValueError("The code default and planning branches must differ.")
    code = _direct_ref(repo, code_ref)
    if code is None:
        raise ValueError("The selected default branch does not exist.")
    repo = Repository(repo.root, target)
    with ref_gate(repo, RefIdentity(target), RefMutationKind.PLANNING) as gate:
        proposal = read_proposal(repo)
        previous = _direct_ref(repo, target)
        if proposal is None:
            if previous is not None:
                raise ValueError(
                    "The planning branch exists without a trusted bootstrap."
                )
            checked_out = repo._run("symbolic-ref", "-q", "HEAD")
            if checked_out.stdout.strip().decode("utf-8") != code_ref:
                raise ValueError(
                    "Prepare a new installation from the default worktree."
                )
            if replacement is not None:
                _assert_original_missing(repo, replacement.anchor)
            elif (
                repo.read_blobs(repo.read_tree(code).tree, (CONFIG_PATH,))[CONFIG_PATH]
                is not None
            ):
                raise ValueError("Committed installation already exists.")
            if replacement is None:
                for file in (repo.root / CONFIG_PATH, repo.root / WORKFLOW_PATH):
                    if file.exists() or file.is_symlink():
                        raise ValueError(
                            f"Existing {file.name} prevents new bootstrap."
                        )
            if request.planning_remote is not None:
                observed = _fetch(repo, request.planning_remote, target, "bootstrap")
                try:
                    if observed.observation is None:
                        raise ValueError(
                            observed.reason
                            or "Could not observe the hosted planning branch."
                        )
                    if observed.observation.observed_commit is not None:
                        raise ValueError(
                            "The hosted planning branch exists without a trusted bootstrap."
                        )
                finally:
                    _drop_candidate(repo, observed)
            proposal = _allocate(repo, code_ref, request).model_copy(
                update={"replacement": replacement}
            )
            record_proposal(repo, proposal)
        if (
            proposal.anchor.code_default_ref != code_ref
            or proposal.anchor.planning_ref != target
            or proposal.code_remote != request.code_remote
            or proposal.anchor.planning_remote != request.planning_remote
        ):
            raise ValueError("Bootstrap already exists for different refs.")
        candidate = previous or proposal.initial_tip
        _check_history(repo, proposal, candidate)
        if previous is None:
            gate.assert_excluded()
            repo._git(
                "update-ref",
                "--no-deref",
                target,
                proposal.initial_tip,
                "0" * repo.oid_length,
            )
    return proposal


def _check_store_identity(anchor: StoreAnchor, content: bytes | None) -> None:
    try:
        data = json_loads(content or b"", object_pairs_hook=_unique_coordinates)
    except ValueError as error:
        raise ValueError("Planning store metadata is missing or invalid.") from error
    if (
        not isinstance(data, dict)
        or data.get("schema") != "aitm.store/v1"
        or data.get("store_uuid") != anchor.store_uuid
        or data.get("root_commit", anchor.root_commit) != anchor.root_commit
    ):
        raise ValueError("Planning store metadata disagrees with the trusted anchor.")


def _check_installed_tip(installation: Installation, tip: str) -> None:
    repo = installation.repository
    path = ".aitm/store.json"
    _check_store_identity(
        installation.store, repo.read_blobs(repo.read_tree(tip).tree, (path,))[path]
    )


def _check_history(repo: Repository, proposal: BootstrapProposal, tip: str) -> None:
    report = validate_history(proposal.anchor, tip, repository=repo)
    if (
        report.outcome != LocalOutcome.COMPLETED
        or repo._run(
            "merge-base", "--is-ancestor", proposal.initial_tip, tip
        ).returncode
    ):
        raise ValueError(
            report.reason or "Planning history differs from the retained bootstrap."
        )
    data = repo.read_blobs(repo.read_tree(tip).tree, (".aitm/store.json",))
    original = repo.read_blobs(
        repo.read_tree(proposal.initial_tip).tree, (".aitm/store.json",)
    )
    if data != original:
        raise ValueError("Planning store identity differs from the retained bootstrap.")


def _pending(operation_id: str, step: str, *evidence: str) -> InitResult:
    return InitResult(
        CommandResult(
            operation_id=operation_id,
            local=LocalOutcome.COMPLETED,
            publication=PublicationOutcome.PENDING,
            pending=(step,),
            evidence=evidence,
        )
    )


def _load_policy(
    installation: Installation, revision: str, candidate_ref: str
) -> PolicySnapshot:
    remote = installation.code_remote
    active = installation
    if remote is not None:
        active = _CandidateInstallation(
            repository=installation.repository,
            store=installation.store,
            code_repository=installation.code_repository,
            planning_repository=installation.planning_repository,
            issuer=installation.issuer,
            bootstrap_source=installation.bootstrap_source,
            code_remote=remote,
            code_remote_ref=installation.code_remote_ref,
            legacy_root=installation.legacy_root,
            candidate_ref=candidate_ref,
        )
    policy = resolve_policy(
        active,
        RefreshResult(
            local=RefObservation(
                ref=installation.store.code_default_ref,
                observed_commit=revision,
                remote=remote,
            )
        ),
    )
    load_profile(policy)
    if policy.writes_fenced:
        raise ValueError("Committed routing requires explicit reconfiguration.")
    return policy


def _code_candidate(repo: Repository, code_ref: str, remote: str | None):
    if remote is None:
        revision = _direct_ref(repo, code_ref)
        if revision is None:
            raise ValueError("The anchored code default is unavailable.")
        return revision, code_ref, None
    fetched = _fetch(repo, remote, code_ref, "bootstrap-code")
    if (
        fetched.observation is None
        or fetched.observation.observed_commit is None
        or fetched.ref is None
    ):
        _drop_candidate(repo, fetched)
        raise ValueError(fetched.reason or "The hosted code default is unavailable.")
    revision = fetched.observation.observed_commit
    local = _direct_ref(repo, code_ref)
    if local is None or not (
        _is_ancestor(repo, local, revision) is True
        or _is_ancestor(repo, revision, local) is True
    ):
        _drop_candidate(repo, fetched)
        raise ValueError(
            "The selected hosted and local defaults do not share a verified history."
        )
    return revision, fetched.ref, fetched


def _record_installation(
    installation: Installation, revision: str, *, replace_existing: bool = False
) -> None:
    state = state_directory(installation.repository)
    descriptor = state / "installation.json"
    anchor_file = state / "store-anchor.json"
    if descriptor.exists() and not replace_existing:
        active, _accepted = _active_installation(installation.repository)
        if (
            active.routing != installation.routing
            or active.code_remote != installation.code_remote
        ):
            raise ValueError(
                "The installed authority differs from the proposed anchor."
            )
        return
    coordinates = {
        "anchor": installation.store.model_dump(mode="json"),
        "accepted_revision": revision,
        "code_repository": installation.code_repository,
        "planning_repository": installation.planning_repository,
        "bootstrap_source": installation.bootstrap_source,
        "issuer": installation.issuer.model_dump(mode="json"),
        "code_remote": installation.code_remote,
        "code_remote_ref": installation.code_remote_ref,
        "legacy_root": installation.legacy_root.model_dump(mode="json")
        if installation.legacy_root
        else None,
    }
    if replace_existing:
        _atomic_write(anchor_file, installation.store.model_dump(mode="json"))
        _atomic_write(descriptor, coordinates)
    else:
        prepare_file(
            anchor_file, (installation.store.model_dump_json() + "\n").encode()
        )
        prepare_file(descriptor, (dumps(coordinates, sort_keys=True) + "\n").encode())


def _active_installation(repository: Repository) -> tuple[Installation, str]:
    descriptor = state_directory(repository) / "installation.json"
    saved = json_loads(descriptor.read_bytes())
    if (
        not isinstance(saved, dict)
        or "anchor" not in saved
        or "accepted_revision" not in saved
    ):
        raise ValueError(
            "The established installation has no retained anchor authority."
        )
    anchor = StoreAnchor.model_validate(saved["anchor"])
    repo = Repository(repository.root, anchor.planning_ref)
    return load_installation(repo, anchor, descriptor), repo._oid(
        saved["accepted_revision"]
    )


def _readiness(
    installation: Installation, ports: ServicePorts
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    from aitm_core.setup.doctor import (
        MANUAL_PROTECTION,
        protection_evidence,
        protection_target,
        retain_protection,
    )

    messages = []
    pending = []
    if installation.store.planning_remote is None:
        messages.append(MANUAL_PROTECTION)
    else:
        protect = getattr(ports.init_git_host, "protect_branch", None)
        result = (
            protect(protection_target(installation), ProtectionRules())
            if callable(protect)
            else None
        )
        if result is None:
            messages.append(MANUAL_PROTECTION)
            pending.append("init_git_host")
        else:
            retain_protection(installation, result)
            messages.extend(protection_evidence(result))
            if result.status not in ("applied", "already-protected"):
                pending.append("init_git_host")
    for slot, method in (
        ("init_hooks", "install"),
        ("init_doctor", "check"),
        ("init_provider", "initialize"),
    ):
        step = getattr(getattr(ports, slot), method, None)
        if callable(step):
            messages.extend(step(installation))
        else:
            pending.append(slot)
            messages.append(f"Installation step is unavailable: {slot}.")
    return tuple(messages), tuple(pending)


def _ready(
    operation_id: str,
    installation: Installation,
    policy: PolicySnapshot,
    published: bool,
    ports: ServicePorts,
) -> InitResult:
    _check_installed_tip(installation, installation.repository.tip().revision)
    _record_installation(installation, policy.revision)
    messages, pending = _readiness(installation, ports)
    return InitResult(
        CommandResult(
            operation_id=operation_id,
            local=LocalOutcome.COMPLETED,
            publication=PublicationOutcome.VERIFIED
            if published
            else PublicationOutcome.NOT_APPLICABLE,
            pending=pending,
            evidence=(
                f"Verified committed policy and workflow at {policy.revision}.",
                *messages,
            ),
        ),
        installation,
        policy,
    )


def _assert_original_missing(repo: Repository, original: StoreAnchor) -> None:
    original_tip = _direct_ref(repo, original.planning_ref)
    has_root = repo._run(
        "cat-file", "-e", f"{repo._oid(original.root_commit)}^{{commit}}"
    )
    if original_tip is not None or has_root.returncode == 0:
        raise ValueError(
            "Original planning history is available locally. Resume or repair it."
        )
    if original.planning_remote is not None:
        observed = _fetch(
            repo, original.planning_remote, original.planning_ref, "original-bootstrap"
        )
        try:
            if observed.observation is None:
                raise ValueError("Cannot prove the original planning branch is absent.")
            if observed.observation.observed_commit is not None:
                raise ValueError(
                    "Original planning history became available. Adopt it instead."
                )
        finally:
            _drop_candidate(repo, observed)


def _prepare_worktree(repo: Repository, proposal: BootstrapProposal) -> tuple[str, ...]:
    from aitm_core.setup.hooks import ignore_landing_commands, prepare_ignore

    checked_out = repo._run("symbolic-ref", "-q", "HEAD")
    if checked_out.stdout.strip().decode("utf-8") == proposal.anchor.code_default_ref:
        prepare_file(repo.root / CONFIG_PATH, proposal.config.encode())
        prepare_file(repo.root / WORKFLOW_PATH, proposal.workflow.encode())
        prepare_ignore(repo)
        return ignore_landing_commands(repo)
    return ()


def _bootstrap_publish(
    installation: Installation, proposal: BootstrapProposal
) -> str | None:
    repo = installation.repository
    remote = proposal.anchor.planning_remote
    assert remote is not None
    observed = _fetch(repo, remote, repo.ref, "bootstrap")
    try:
        if observed.observation is None:
            return observed.reason or "Cannot observe the hosted planning ref."
        tip = observed.observation.observed_commit
        if tip is None:
            cached = refresh(installation, cached=True).shared
            if cached is not None and cached.valid_tip is not None:
                return "A previously verified planning branch disappeared. Resolve continuity before publishing."
            # A branch-creation lease cannot overwrite an existing remote history.
            endpoint = fsdecode(
                repo._git("remote", "get-url", "--", remote).rstrip(b"\n")
            )
            repo._run(
                "push",
                "--porcelain",
                f"--force-with-lease={repo.ref}:",
                "--",
                endpoint,
                f"{proposal.initial_tip}:{repo.ref}",
            )
        else:
            _check_history(repo, proposal, tip)
    finally:
        _drop_candidate(repo, observed)
    return None


def resume_init(
    request: InitRequest, operation_id: str, ports: ServicePorts | None = None
) -> InitResult:
    repo = Repository(request.repository, f"refs/heads/{request.planning_branch}")
    with ref_gate(repo, RefIdentity(repo.ref), RefMutationKind.PLANNING) as gate:
        proposal = read_proposal(repo)
        if proposal is None or proposal.operation_id != operation_id:
            raise ValueError("Unknown bootstrap operation.")
        installation = _installation(repo, proposal)
        _check_history(repo, proposal, repo.tip().revision)
        revision, candidate_ref, fetched = _code_candidate(
            repo, proposal.anchor.code_default_ref, proposal.code_remote
        )
        try:
            if proposal.replacement is not None:
                basis = proposal.replacement
                _assert_original_missing(repo, basis.anchor)
                if revision == basis.revision:
                    stage = state_directory(repo) / "replacement"
                    stage.mkdir(exist_ok=True)
                    prepare_file(stage / CONFIG_PATH, proposal.config.encode())
                    prepare_file(stage / WORKFLOW_PATH, proposal.workflow.encode())
                    return _pending(
                        operation_id,
                        "committed-bootstrap-policy",
                        f"Copy the proposed files from {stage} into the code worktree.",
                        *LANDING_COMMANDS,
                        "Land that commit on the anchored default through the usual repository workflow.",
                        "aitm init",
                    )
                if _is_ancestor(repo, basis.revision, revision) is not True:
                    raise ValueError(
                        "Replacement policy must extend the original committed default."
                    )
            commit = repo.read_tree(revision)
            committed = repo.read_blobs(commit.tree, (CONFIG_PATH, WORKFLOW_PATH))
            if committed[CONFIG_PATH] is None and proposal.activated_revision is None:
                ignore_commands = _prepare_worktree(repo, proposal)
                return _pending(
                    operation_id,
                    "committed-bootstrap-policy",
                    "Run these commands from the worktree holding the proposed policy.",
                    *LANDING_COMMANDS,
                    *ignore_commands,
                    "Land that commit on the anchored default through the usual repository workflow.",
                    "aitm init",
                )
            policy = _load_policy(installation, revision, candidate_ref)
            if proposal.activated_revision is None:
                if (
                    policy.source.content != proposal.config.encode()
                    or policy.workflow.content != proposal.workflow.encode()
                ):
                    raise ValueError(
                        "The exact bootstrap proposal has not landed on the default branch."
                    )
                proposal = proposal.model_copy(update={"activated_revision": revision})
                record_proposal(repo, proposal)
            elif _is_ancestor(repo, proposal.activated_revision, revision) is not True:
                raise ValueError(
                    "The code default no longer contains the activated bootstrap."
                )
            if installation.store.planning_remote is None:
                return _ready(
                    operation_id, installation, policy, False, ports or ServicePorts()
                )
            gate.assert_excluded()
            reason = _bootstrap_publish(installation, proposal)
            if reason is not None:
                return _pending(operation_id, "bootstrap-publication", reason)
        finally:
            if fetched is not None:
                _drop_candidate(repo, fetched)
    observed = refresh(installation, trusted_checkpoint=proposal.initial_tip)
    shared = observed.shared
    if (
        observed.code_freshness != Freshness.FRESH
        or shared is None
        or shared.status != ContinuityStatus.VERIFIED
    ):
        return _pending(
            operation_id,
            "bootstrap-publication",
            "Hosted bootstrap publication remains pending.",
        )
    return _ready(operation_id, installation, policy, True, ports or ServicePorts())


def adopt_committed(
    request: InitRequest, check_branch: bool = False, ports: ServicePorts | None = None
) -> InitResult | None:
    """A new clone adopts the anchor from its selected committed default history."""
    operation_id = uuid4().hex
    repo = Repository(request.repository, "refs/heads/aitm-bootstrap-probe")
    code_ref = _branch(repo, request.default_branch)
    journal = read_proposal(repo)
    if journal is not None:
        operation_id = journal.operation_id
    descriptor = state_directory(repo) / "installation.json"
    active = _active_installation(repo) if descriptor.exists() else None
    staged_replacement = journal.replacement if active is None and journal else None
    if active is None and journal is not None and staged_replacement is None:
        return None
    if active is not None and (
        active[0].store.code_default_ref != code_ref
        or active[0].code_remote != request.code_remote
    ):
        raise ValueError("Initialization cannot change the selected code default.")
    revision, ref, fetched = _code_candidate(repo, code_ref, request.code_remote)
    try:
        tree = repo.read_tree(revision).tree
        if repo.read_blobs(tree, (CONFIG_PATH,))[CONFIG_PATH] is None:
            if active is not None:
                raise ValueError("The anchored default has lost its committed policy.")
            return None
        config = CommittedConfig.model_validate(
            loads(_committed_file(repo, tree, CONFIG_PATH).content.decode())
        )
        if check_branch and config.store.branch != request.planning_branch:
            raise ValueError(
                "The requested planning branch differs from committed policy."
            )
        if (
            request.planning_remote is not None
            and request.planning_remote != config.store.remote
        ):
            raise ValueError("The requested remote differs from committed policy.")
        expected_trunk = (
            f"{request.code_remote}/{request.default_branch}"
            if request.code_remote
            else request.default_branch
        )
        if config.store.trunk != expected_trunk:
            raise ValueError(
                "Committed policy does not name the selected code default."
            )
        if active is not None:
            installation, accepted = active
            if _is_ancestor(repo, accepted, revision) is not True:
                raise ValueError(
                    "The current default does not extend the accepted policy."
                )
        else:
            installation = _from_config(repo, request, config)
        if staged_replacement is not None:
            assert journal is not None
            if installation.store == journal.anchor:
                return None
            if (
                installation.store != staged_replacement.anchor
                or _is_ancestor(repo, staged_replacement.revision, revision) is not True
            ):
                raise ValueError(
                    "The committed anchor differs from both retained proposals."
                )
        repo = installation.repository
        target = repo.ref
        policy = _load_policy(installation, revision, ref)
        if request.code_remote is None:
            tip = _direct_ref(repo, target)
            if tip is None:
                if staged_replacement is not None:
                    return None
                return _pending(
                    operation_id,
                    "bootstrap-history",
                    "The original planning objects are unavailable. Use explicit reconfiguration if they are irretrievable.",
                )
            if (
                validate_history(installation.store, tip, repository=repo).outcome
                != LocalOutcome.COMPLETED
            ):
                raise ValueError(
                    "Local planning history does not match committed policy."
                )
            return _ready(
                operation_id, installation, policy, False, ports or ServicePorts()
            )
    finally:
        if fetched is not None:
            _drop_candidate(repo, fetched)
    observed = refresh(installation)
    shared = observed.shared
    if (
        observed.code_freshness != Freshness.FRESH
        or shared is None
        or shared.status != ContinuityStatus.VERIFIED
    ):
        if staged_replacement is not None:
            return None
        return _pending(
            operation_id,
            "bootstrap-history",
            "The anchored planning history has not been published or could not be verified.",
        )
    return _ready(operation_id, installation, policy, True, ports or ServicePorts())


def _from_config(
    repo: Repository, request: InitRequest, config: CommittedConfig
) -> Installation:
    code_ref = _branch(repo, request.default_branch)
    target = _branch(repo, config.store.branch)
    repo = Repository(repo.root, target)
    return Installation(
        repository=repo,
        store=StoreAnchor(
            store_uuid=config.store.uuid,
            code_default_ref=code_ref,
            planning_ref=target,
            planning_remote=config.store.remote,
            root_commit=config.store.root_commit,
        ),
        issuer=BacklogIssuer(
            backlog=config.providers.backlog,
            backlog_repository=config.providers.backlog_repository,
            numbering_namespace=config.providers.numbering_namespace,
        ),
        code_repository=config.store.code_repository,
        planning_repository=config.store.repository,
        code_remote=request.code_remote,
        code_remote_ref=code_ref if request.code_remote else None,
        bootstrap_source="explicit-default"
        if request.code_remote is None
        else "remote-default",
        legacy_root=config.store.legacy_root,
    )
