"""Validated installation coordinates supplied by bootstrap or adoption."""

from dataclasses import dataclass

from aitm_core.models.common import StoreAnchor
from aitm_core.models.config import BacklogIssuer, LegacyRoot, Routing
from aitm_core.store.objects import Repository


@dataclass(frozen=True, slots=True)
class Installation:
    """Clone-local routing facts and their provenance, without policy settings."""

    repository: Repository
    store: StoreAnchor
    code_repository: str
    planning_repository: str
    issuer: BacklogIssuer
    bootstrap_source: str
    code_remote: str | None = None
    code_remote_ref: str | None = None
    legacy_root: LegacyRoot | None = None

    def __post_init__(self) -> None:
        default = self.store.code_default_ref
        if (
            self.repository.ref != self.store.planning_ref
            or default == self.repository.ref
        ):
            raise ValueError(
                "installation requires distinct anchored code and planning refs"
            )
        self._check_branch(default)
        if (self.code_remote is None) != (self.code_remote_ref is None):
            raise ValueError("installation requires a complete code remote/ref pair")
        if self.code_remote_ref is not None:
            self._check_branch(self.code_remote_ref)
        if not self.bootstrap_source.strip():
            raise ValueError("installation requires recorded bootstrap provenance")
        self.repository._oid(self.store.root_commit)
        if (
            self.legacy_root is not None
            and self.legacy_root.root_commit != self.store.root_commit
        ):
            raise ValueError(
                "installation legacy declaration must name the anchored root"
            )

    def _check_branch(self, ref: str) -> None:
        if not ref.startswith("refs/heads/"):
            raise ValueError("installation requires fully qualified branch refs")
        self.repository._git("check-ref-format", ref)

    @property
    def routing(self) -> Routing:
        default = self.code_remote_ref or self.store.code_default_ref
        branch = default.removeprefix("refs/heads/")
        trunk = f"{self.code_remote}/{branch}" if self.code_remote else branch
        return Routing(
            store=self.store,
            code_repository=self.code_repository,
            planning_repository=self.planning_repository,
            trunk=trunk,
            issuer=self.issuer,
            legacy_root=self.legacy_root,
        )
