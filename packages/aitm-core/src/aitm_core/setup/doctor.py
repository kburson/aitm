"""Read-only installation diagnostics with independent readiness facets."""

from dataclasses import dataclass

from aitm_core.models.common import LocalOutcome
from aitm_core.services import ServicePorts, preflight_policy
from aitm_core.setup.hooks import NAMES, ROOT_IGNORE, inspect_hooks
from aitm_core.store.gate import RefIdentity, _worktrees
from aitm_core.store.installation import Installation
from aitm_core.store.validation import validate_history


@dataclass(frozen=True, slots=True)
class ReadinessReport:
    evidence: tuple[str, ...]
    pending: tuple[str, ...]


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
    if context.store.planning_remote is not None:
        if shared is None or shared.fences_shared:
            pending.append("publication")
        pending.append("protection")
        evidence.append(
            "Hosted protection requires independent confirmation. Block deletion and force pushes, "
            "require linear history, leave pull requests optional, and disable bypass."
        )
    else:
        evidence.append(
            "Hosted publication and protection are not applicable in local mode."
        )
    occupied = _worktrees(repo, RefIdentity(repo.ref))
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
    if callable(lane):
        evidence.extend(lane(context))
    else:
        pending.append("lane-probe")
        evidence.append("Lane probe is unavailable.")
    return ReadinessReport(tuple(evidence), tuple(pending))


class InstallationDoctor:
    def check(self, context: Installation) -> tuple[str, ...]:
        return doctor(context).evidence
