"""Read-only installation diagnostics with independent readiness facets."""

from dataclasses import dataclass
from hashlib import sha256

from aitm_core.models.common import LocalOutcome
from aitm_core.providers.githost import ProtectionRules, ProtectResult, RemoteRef
from aitm_core.services import ServicePorts, preflight_policy
from aitm_core.setup.hooks import NAMES, ROOT_IGNORE, inspect_hooks
from aitm_core.setup.journal import state_directory
from aitm_core.store.gate import RefIdentity, _atomic_write, _worktrees
from aitm_core.store.installation import Installation
from aitm_core.store.validation import validate_history
from aitm_core.verification.lanes import select_lane


@dataclass(frozen=True, slots=True)
class ReadinessReport:
    evidence: tuple[str, ...]
    pending: tuple[str, ...]


MANUAL_PROTECTION = (
    "For a shared planning branch, block deletion and force pushes, require linear "
    "history, leave pull requests optional, and disable bypass."
)


def protection_target(context: Installation) -> RemoteRef:
    return RemoteRef(
        repository=context.planning_repository,
        ref=RefIdentity(context.store.planning_ref),
        remote=context.store.planning_remote,
    )


def _protection_receipt(context: Installation, target: RemoteRef):
    route = sha256(target.model_dump_json().encode()).hexdigest()
    return state_directory(context.repository) / "protection" / f"{route}.json"


def retain_protection(context: Installation, result: ProtectResult) -> None:
    target = protection_target(context)
    if (
        not isinstance(result, ProtectResult)
        or result.target != target
        or result.rules != ProtectionRules()
    ):
        raise ValueError("Branch protection returned evidence for another request.")
    _atomic_write(_protection_receipt(context, target), result.model_dump(mode="json"))


def protection_evidence(result: ProtectResult) -> tuple[str, ...]:
    return (
        f"Retained hosted branch protection status is {result.status}.",
        *result.instructions,
        *result.evidence,
        *((result.settings_url,) if result.settings_url else ()),
    )


def _diagnose_protection(context: Installation) -> tuple[tuple[str, ...], bool]:
    if context.store.planning_remote is None:
        return (
            "Hosted publication and protection are not applicable in local mode.",
            MANUAL_PROTECTION,
        ), False
    target = protection_target(context)
    try:
        result = ProtectResult.model_validate_json(
            _protection_receipt(context, target).read_bytes()
        )
        if result.target != target or result.rules != ProtectionRules():
            raise ValueError("Different target or rules.")
    except (FileNotFoundError, ValueError):
        return (
            "Hosted branch protection requires manual confirmation.",
            MANUAL_PROTECTION,
        ), True
    return protection_evidence(result), result.status not in {
        "applied",
        "already-protected",
    }


def doctor(context: Installation, ports: ServicePorts | None = None) -> ReadinessReport:
    ports = ports or ServicePorts()
    repo = context.repository
    evidence = []
    pending = []
    preflight = preflight_policy(context, cached=True)
    evidence.extend(preflight.evidence)
    if preflight.outcome != LocalOutcome.COMPLETED:
        pending.append("policy")
    tip = preflight.views.planning.observed_commit
    if tip is not None:
        report = validate_history(context.store, tip, repository=repo)
        evidence.append(
            f"Local planning integrity is {report.outcome}. {report.reason or ''}".rstrip()
        )
        if report.outcome != LocalOutcome.COMPLETED:
            pending.append("local-integrity")
    else:
        evidence.append("Local planning history is unavailable.")
        pending.append("local-integrity")
    shared = preflight.views.shared
    if context.store.planning_remote is not None and (
        shared is None or shared.fences_shared
    ):
        pending.append("publication")
    protection, uncertain = _diagnose_protection(context)
    evidence.extend(protection)
    if uncertain:
        pending.append("protection")
    occupied = _worktrees(repo, RefIdentity(context.store.planning_ref))
    if occupied:
        pending.append("checkout")
        evidence.append(
            f"Planning checkout exclusion requires attention at {', '.join(occupied)}."
        )
    else:
        evidence.append("Planning ref is excluded from registered worktrees.")
    hooks = inspect_hooks(repo)
    missing = sorted(set(NAMES) - set(hooks.installed))
    if missing:
        pending.append("hooks")
        evidence.append(
            f"Missing AITM hooks in {hooks.path} include {', '.join(missing)}."
        )
    else:
        evidence.append(f"Validated AITM hook wrappers in {hooks.path}.")
    evidence.extend(f"Chained existing {name} hook." for name in hooks.chained)
    ignore = repo.root / ".gitignore"
    head = repo._run("symbolic-ref", "-q", "HEAD")
    content = None
    if head.stdout.strip() == context.store.code_default_ref.encode():
        if ignore.is_file() and not ignore.is_symlink():
            content = ignore.read_bytes()
    elif preflight.policy is not None:
        content = repo.read_blobs(preflight.policy.tree, (".gitignore",))[".gitignore"]
    patterns = (content or b"").splitlines()
    if ROOT_IGNORE not in patterns:
        pending.append("ignore")
        evidence.append("The root .gitignore requires /.aitm/.")
    if b".aitm/" in patterns:
        evidence.append("The unanchored .aitm/ entry also hides nested fixture paths.")
    lane = getattr(ports.lane_selection, "probe", None)
    if ports.lane_selection is select_lane and preflight.policy is not None:
        assurance = preflight.policy.config.test.assurance
        capability = select_lane(assurance).probe()
        evidence.append(capability.reason)
        if capability.assurance != assurance:
            pending.append("lane-probe")
    elif callable(lane):
        evidence.extend(lane(context))
    else:
        pending.append("lane-probe")
        evidence.append("Lane probe is unavailable.")
    return ReadinessReport(tuple(evidence), tuple(pending))


class InstallationDoctor:
    def check(self, context: Installation) -> tuple[str, ...]:
        return doctor(context, ServicePorts(lane_selection=select_lane)).evidence
