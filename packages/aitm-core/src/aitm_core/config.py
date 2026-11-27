"""Read committed policy from one previously validated code-default observation."""

import tomllib
from dataclasses import dataclass
from hashlib import sha256

from pydantic import ValidationError

from aitm_core.models.common import RefreshResult, StoreAnchor
from aitm_core.models.config import BacklogIssuer, CommittedConfig, Routing
from aitm_core.models.operations import repository_path
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError, Repository

CONFIG_PATH = ".aitm.toml"


class PolicyUnavailable(ValueError):
    """The committed configuration cannot establish usable policy."""


@dataclass(frozen=True, slots=True)
class CommittedFile:
    path: str
    content: bytes

    @property
    def digest(self) -> str:
        return sha256(self.content).hexdigest()


@dataclass(frozen=True, slots=True)
class PolicySnapshot:
    revision: str
    tree: str
    source: CommittedFile
    workflow: CommittedFile
    config: CommittedConfig
    routing: Routing
    proposed_routing: Routing

    @property
    def adoption_pending(self) -> bool:
        return self.routing != self.proposed_routing

    @property
    def writes_fenced(self) -> bool:
        return self.adoption_pending


@dataclass(frozen=True, slots=True)
class PolicyChange:
    requires_reconfigure: bool
    tip_effective: bool


def _committed_file(repository: Repository, tree: str, path: str) -> CommittedFile:
    path = repository_path(path)
    entry = repository._git("--literal-pathspecs", "ls-tree", "-z", tree, "--", path)
    if not entry.startswith((b"100644 blob ", b"100755 blob ")):
        raise PolicyUnavailable(f"policy commit lacks a regular file at {path}")
    content = repository.read_blobs(tree, (path,))[path]
    if content is None:
        raise PolicyUnavailable(f"policy commit lacks file contents at {path}")
    return CommittedFile(path, content)


def _proposed_routing(installation: Installation, config: CommittedConfig) -> Routing:
    settings = config.store
    repo = installation.repository
    root = repo._oid(settings.root_commit)
    target = f"refs/heads/{settings.branch}"
    repo._git("check-ref-format", target)
    repo._git("check-ref-format", f"refs/heads/{settings.trunk}")
    if settings.remote is not None:
        repo._git("check-ref-format", f"refs/remotes/{settings.remote}/HEAD")
    if settings.legacy_root is not None:
        repo._oid(settings.legacy_root.approved_tip)
        if settings.legacy_root.root_commit != root:
            raise PolicyUnavailable(
                "legacy declaration must name the committed store root"
            )
    return Routing(
        store=StoreAnchor(
            store_uuid=settings.uuid,
            code_default_ref=installation.store.code_default_ref,
            planning_ref=target,
            planning_remote=settings.remote,
            root_commit=root,
        ),
        code_repository=settings.code_repository,
        planning_repository=settings.repository,
        trunk=settings.trunk,
        issuer=BacklogIssuer(
            backlog=config.providers.backlog,
            backlog_repository=config.providers.backlog_repository,
            numbering_namespace=config.providers.numbering_namespace,
        ),
        legacy_root=settings.legacy_root,
    )


def resolve_policy(anchor: Installation, refresh: RefreshResult) -> PolicySnapshot:
    """Use one admitted local snapshot. Candidate adoption belongs to refresh."""
    local = refresh.local
    revision = local.observed_commit
    target = anchor.policy_ref(local)
    if target is None or revision is None:
        raise PolicyUnavailable(
            "policy needs an anchored local or validated hosted observation"
        )

    repository = anchor.repository
    try:
        revision = repository._oid(revision)
        symbolic = repository._run("symbolic-ref", "-q", target)
        if symbolic.returncode != 1:
            raise PolicyUnavailable("policy needs a direct anchored code-default ref")
        tip = repository._git("show-ref", "--verify", "--hash", target)
        tip_oid = repository._oid(tip.strip().decode("ascii"))
        if repository._git("cat-file", "-t", revision).strip() != b"commit":
            raise PolicyUnavailable("code-default observation does not name a commit")
        if repository._run("merge-base", "--is-ancestor", revision, tip_oid).returncode:
            raise PolicyUnavailable(
                "observation is outside anchored code-default history"
            )
        snapshot = repository.read_tree(revision)
        source = _committed_file(repository, snapshot.tree, CONFIG_PATH)
        config = CommittedConfig.model_validate(
            tomllib.loads(source.content.decode("utf-8"))
        )
        workflow = _committed_file(repository, snapshot.tree, config.workflow.file)
        proposed = _proposed_routing(anchor, config)
        routing = anchor.routing
    except PolicyUnavailable:
        raise
    except ValidationError as error:
        fields = ", ".join(
            ".".join(map(str, item["loc"]))
            for item in error.errors(include_input=False, include_context=False)
        )
        raise PolicyUnavailable(
            f"unsupported committed policy fields: {fields}"
        ) from error
    except (ValueError, GitCommandError) as error:
        raise PolicyUnavailable(
            f"committed policy is unavailable at {revision}"
        ) from error

    return PolicySnapshot(
        revision, snapshot.tree, source, workflow, config, routing, proposed
    )


def classify_change(old: PolicySnapshot, new: PolicySnapshot) -> PolicyChange:
    """Classify proposed routing changes separately from effective settings."""
    excluded = {
        "store": True,
        "providers": {"backlog", "backlog_repository", "numbering_namespace"},
    }
    return PolicyChange(
        requires_reconfigure=(
            new.adoption_pending or old.proposed_routing != new.proposed_routing
        ),
        tip_effective=(
            old.config.model_dump(exclude=excluded)
            != new.config.model_dump(exclude=excluded)
            or old.workflow != new.workflow
        ),
    )
