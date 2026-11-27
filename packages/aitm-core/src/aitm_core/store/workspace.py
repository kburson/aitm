"""Serialize clone-local worktree bindings and recover exact authored bytes."""

import os
import stat
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Callable, Literal
from uuid import uuid4

from aitm_core.models.attempts import (
    BindingPurpose,
    EvidenceOperation,
    RecoveryAuthority,
    SourceSnapshot,
)
from aitm_core.models.binding import (
    Binding,
    BoundPath,
    EntityRef,
    StoryRef,
    allows_authored,
)
from aitm_core.models.common import LocalOutcome
from aitm_core.models.operations import repository_path, story_event_path
from aitm_core.services import preflight_policy
from aitm_core.setup.journal import state_directory
from aitm_core.store.fetch import _direct_ref, _is_ancestor
from aitm_core.store.gate import (
    RefIdentity,
    RefMutationKind,
    _atomic_write,
    _worktrees,
    ref_gate,
)
from aitm_core.store.installation import Installation
from aitm_core.store.validation import validate_history


class BindingConflict(ValueError):
    """The binding is occupied, stale or tied to other worktree bytes."""


class AuthorityUnavailable(ValueError):
    """No validated authority was supplied for this purpose."""


@dataclass(frozen=True, slots=True)
class AuthorityRef:
    identity: str
    lookup: Callable[[str], RecoveryAuthority | None]


@dataclass(frozen=True, slots=True)
class BindRequest:
    installation: Installation
    scope: StoryRef | EntityRef
    purpose: BindingPurpose
    session: str
    paths: tuple[str, ...] = ()
    attempt: str | None = None
    branch: str | None = None
    source: SourceSnapshot | None = None
    branch_mode: Literal["existing", "create", "scrap", "refactor"] = "existing"
    authority: AuthorityRef | None = None
    capabilities: tuple[EvidenceOperation, ...] = ()


def digest(data: bytes | None) -> str | None:
    return sha256(data).hexdigest() if data is not None else None


@contextmanager
def _parent(root: Path, path: str, create: bool = False):
    parts = PurePosixPath(repository_path(path)).parts
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
    with ExitStack() as stack:
        area = os.open(root, flags)
        stack.callback(os.close, area)
        for part in parts[:-1]:
            if create:
                try:
                    os.mkdir(part, dir_fd=area)
                except FileExistsError:
                    pass
            area = os.open(part, flags, dir_fd=area)
            stack.callback(os.close, area)
        yield area, parts[-1]


def read_workspace(root: Path, path: str) -> bytes | None:
    try:
        with _parent(root, path) as (parent, name):
            descriptor = os.open(
                name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent
            )
            with os.fdopen(descriptor, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise BindingConflict(f"Expected a regular file at {path}.")
                return stream.read()
    except FileNotFoundError:
        return None
    except OSError as error:
        raise BindingConflict(
            f"Cannot read a contained regular file at {path}."
        ) from error


def _materialize(root: Path, path: str, data: bytes, mode: int = 0o644) -> None:
    if read_workspace(root, path) == data:
        return
    with _parent(root, path, create=True) as (parent, name):
        temporary = f".aitm-bind-{uuid4().hex}"
        fd = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            mode,
            dir_fd=parent,
        )
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(
                    temporary,
                    name,
                    src_dir_fd=parent,
                    dst_dir_fd=parent,
                    follow_symlinks=False,
                )
            except FileExistsError as error:
                raise BindingConflict(
                    f"Existing workspace bytes differ at {path}."
                ) from error
        finally:
            os.unlink(temporary, dir_fd=parent)


class Workspace:
    """Binding authority stays in the Git common directory."""

    def __init__(self, installation: Installation):
        self.installation = installation
        self.repo = installation.repository
        self.state = state_directory(self.repo) / "bindings"

    def _key(self, scope: StoryRef | EntityRef) -> str:
        identity = (
            f"story:{scope.story}"
            if isinstance(scope, StoryRef)
            else f"entity:{scope.identity}"
        )
        return sha256(
            f"{self.installation.store.store_uuid}\0{identity}".encode()
        ).hexdigest()

    def _record(self, scope: StoryRef | EntityRef) -> Path:
        return self.state / f"{self._key(scope)}.json"

    @contextmanager
    def lock(self):
        import fcntl

        self.state.mkdir(parents=True, exist_ok=True)
        with (self.state / "authority.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def lookup(self, scope: StoryRef | EntityRef) -> Binding | None:
        try:
            value = Binding.model_validate_json(self._record(scope).read_bytes())
        except FileNotFoundError:
            return None
        if value.scope != scope or value.anchor != self.installation.store:
            raise BindingConflict(
                "Binding authority belongs to another scope or routing anchor."
            )
        return value

    def _coordinates(self) -> tuple[str, str]:
        directory = os.fsdecode(
            self.repo._git("rev-parse", "--absolute-git-dir").removesuffix(b"\n")
        )
        root = os.fsdecode(
            self.repo._git("rev-parse", "--show-toplevel").removesuffix(b"\n")
        )
        return str(Path(root).resolve()), str(Path(directory).resolve())

    def require(
        self, scope: StoryRef | EntityRef, identity: str, generation: int, session: str
    ) -> Binding:
        """Require the current holder and exact worktree identity while holding lock."""
        value = self.lookup(scope)
        root, directory = self._coordinates()
        if (
            value is None
            or not value.active
            or value.identity != identity
            or value.generation != generation
            or value.session != session
            or value.worktree != root
            or value.git_directory != directory
        ):
            raise BindingConflict(
                "The binding receipt is stale or belongs to another holder."
            )
        return value

    def persist(self, binding: Binding) -> None:
        _atomic_write(self._record(binding.scope), binding.model_dump(mode="json"))

    def _branch_claim(self, request: BindRequest, previous: Binding | None) -> str:
        assert request.branch is not None and request.source is not None
        generation = previous.generation + 1 if previous is not None else 1
        identity = "\0".join(
            (
                self._key(request.scope),
                str(generation),
                request.session,
                request.branch,
                request.source.commit,
                request.attempt or "",
            )
        )
        return f"refs/aitm/binding-branches/{sha256(identity.encode()).hexdigest()}"

    def _source(
        self, request: BindRequest, previous: Binding | None, root: str
    ) -> tuple[str | None, SourceSnapshot | None, RecoveryAuthority | None]:
        if request.purpose == BindingPurpose.EVIDENCE:
            if request.paths or request.branch is not None or request.authority is None:
                raise AuthorityUnavailable(
                    "Evidence binding requires existing recovery authority and no authored paths or branch mutation."
                )
            authority = request.authority.lookup(request.authority.identity)
            retired = previous if previous is not None else self.lookup(request.scope)
            if (
                not isinstance(authority, RecoveryAuthority)
                or authority.authority_id != request.authority.identity
                or authority.attempt != request.attempt
                or authority.source != request.source
                or retired is None
                or authority.ended_generation != retired.generation
                or retired.attempt != authority.attempt
                or retired.source != authority.source
                or not set(request.capabilities).issubset(authority.allowed)
            ):
                raise AuthorityUnavailable(
                    "No current validated authority covers this evidence binding."
                )
            return None, authority.source, authority
        if request.authority is not None or request.capabilities:
            raise ValueError("Recovery authority applies only to the evidence purpose.")
        if request.purpose != BindingPurpose.IMPLEMENTATION:
            if request.branch is not None:
                raise ValueError(
                    "Only implementation can select an implementation branch."
                )
            return None, request.source, None
        if (
            not isinstance(request.scope, StoryRef)
            or not request.attempt
            or not request.branch
            or request.source is None
        ):
            raise ValueError(
                "Implementation binding requires a story, attempt, branch and pinned source."
            )
        branch = request.branch
        if not branch.startswith("refs/heads/"):
            raise ValueError("Implementation requires a fully qualified local branch.")
        self.repo._git("check-ref-format", branch)
        if branch in {self.repo.ref, self.installation.store.code_default_ref}:
            raise ValueError(
                "Planning and default branches cannot become implementation branches."
            )
        observed = _direct_ref(self.repo, branch)
        if observed is not None and any(
            Path(path).resolve() != Path(root)
            for path in _worktrees(self.repo, RefIdentity(branch))
        ):
            raise BindingConflict(
                "The implementation branch belongs to another worktree."
            )
        if request.branch_mode == "refactor" and (
            previous is None or previous.branch != branch
        ):
            raise BindingConflict(
                "Refactor must retain the recorded implementation branch."
            )
        if request.branch_mode in {"create", "scrap"}:
            if request.branch_mode == "scrap" and (
                previous is None
                or previous.branch is None
                or previous.branch == branch
                or previous.attempt == request.attempt
            ):
                raise BindingConflict(
                    "Scrap requires a fresh attempt and implementation branch."
                )
            if (
                request.branch_mode == "create"
                and previous is not None
                and previous.branch is not None
            ):
                raise BindingConflict(
                    "Use explicit scrap or refactor for an existing implementation binding."
                )
            if observed is not None and (
                observed != request.source.commit
                or _direct_ref(self.repo, self._branch_claim(request, previous))
                != observed
            ):
                raise BindingConflict(
                    "The new branch name already belongs to another operation."
                )
            admitted = (
                self.installation.validated_code_ref
                or self.installation.store.code_default_ref
            )
            dest = _direct_ref(self.repo, admitted)
            if (
                dest is None
                or _is_ancestor(self.repo, request.source.commit, dest) is not True
            ):
                raise BindingConflict(
                    "The pinned new branch baseline is outside admitted code history."
                )
        elif observed != request.source.commit:
            raise BindingConflict(
                "The existing implementation branch differs from the pinned head."
            )
        if self.repo._git("cat-file", "-t", request.source.commit).strip() != b"commit":
            raise ValueError("Implementation requires a commit object.")
        if self.repo.read_tree(request.source.commit).tree != request.source.tree:
            raise BindingConflict(
                "The implementation tree differs from the pinned source."
            )
        return branch, request.source, None

    def _plan(self, request: BindRequest, previous: Binding | None):
        observation = preflight_policy(self.installation, cached=True)
        if observation.outcome != LocalOutcome.COMPLETED:
            raise BindingConflict(
                observation.reason or "The installed policy is not current."
            )
        revision = observation.views.planning.observed_commit
        if revision is None:
            raise BindingConflict("Planning history is unavailable.")
        tip = self.repo.read_tree(revision)
        anchor = self.installation.store
        if self.installation.validated_code_ref is not None:
            anchor = anchor.model_copy(
                update={"code_default_ref": self.installation.validated_code_ref}
            )
        history = validate_history(anchor, revision, repository=self.repo)
        if history.outcome != LocalOutcome.COMPLETED:
            raise BindingConflict(
                history.reason or "Planning history cannot authorize a binding."
            )
        known = (
            story_event_path(request.scope.story)
            if isinstance(request.scope, StoryRef)
            else request.scope.document
        )
        tree_paths = self.repo._git(
            "ls-tree", "-r", "--full-tree", "--name-only", "-z", tip.tree
        )
        names = tuple(item.decode() for item in tree_paths.split(b"\0") if item)
        if known not in names:
            raise BindingConflict(
                "The binding scope is absent from the pinned planning tree."
            )
        paths = request.paths
        if (
            not paths
            and previous is not None
            and request.purpose != BindingPurpose.EVIDENCE
        ):
            paths = tuple(item.path for item in previous.paths)
        if not paths and request.purpose == BindingPurpose.PLANNING:
            prefix = PurePosixPath(known).parent.as_posix() + "/"
            paths = tuple(
                path
                for path in names
                if path.startswith(prefix) and allows_authored(request.scope, path)
            )
        paths = tuple(sorted(paths))
        if len(paths) != len(set(paths)) or any(
            not allows_authored(request.scope, path) for path in paths
        ):
            raise ValueError(
                "Binding allowlist includes a duplicate or a path outside authored ownership."
            )
        return tip, self.repo.read_blobs(tip.tree, paths)

    def _claim(self, request: BindRequest, previous: Binding | None) -> Binding:
        root, directory = self._coordinates()
        if request.installation != self.installation:
            raise BindingConflict("Request targets a different installation.")
        if not request.session.strip():
            raise ValueError("Binding requires an attributable session.")
        with ref_gate(self.repo, RefIdentity(self.repo.ref), RefMutationKind.PLANNING):
            branch, source, authority = self._source(request, previous, root)
            tip, blobs = self._plan(request, previous)
            if request.purpose != BindingPurpose.EVIDENCE:
                for path, data in blobs.items():
                    if data is not None:
                        _materialize(Path(root), path, data)
                if isinstance(request.scope, StoryRef):
                    preview = str(
                        PurePosixPath(story_event_path(request.scope.story)).with_name(
                            "story.md"
                        )
                    )
                    content = self.repo.read_blobs(tip.tree, (preview,))[preview]
                    if content is not None:
                        _materialize(Path(root), preview, content, mode=0o444)
            if (
                branch is not None
                and request.branch_mode in {"create", "scrap"}
                and _direct_ref(self.repo, branch) is None
            ):
                assert source is not None
                marker = self._branch_claim(request, previous)
                updates = f"create {branch} {source.commit}\ncreate {marker} {source.commit}\n"
                self.repo._git(
                    "update-ref", "--no-deref", "--stdin", data=updates.encode()
                )
            value = Binding(
                identity=previous.identity if previous is not None else uuid4().hex,
                generation=previous.generation + 1 if previous is not None else 1,
                anchor=self.installation.store,
                scope=request.scope,
                purpose=request.purpose,
                session=request.session,
                worktree=root,
                git_directory=directory,
                planning=SourceSnapshot(commit=tip.revision, tree=tip.tree),
                paths=tuple(
                    BoundPath(path=path, digest=digest(data))
                    for path, data in blobs.items()
                ),
                attempt=request.attempt,
                branch=branch,
                source=source,
                recovery_authority=authority.authority_id
                if authority is not None
                else None,
                capabilities=request.capabilities,
            )
            manifest = f".aitm/.state/{value.identity}-{value.generation}.json"
            _materialize(
                Path(root), manifest, (value.model_dump_json() + "\n").encode()
            )
            self.persist(value)
            return value

    def bind(self, request: BindRequest) -> Binding:
        if request.purpose == BindingPurpose.EVIDENCE and request.authority is None:
            raise AuthorityUnavailable(
                "Evidence binding requires existing recovery authority."
            )
        with self.lock():
            previous = self.lookup(request.scope)
            if previous is not None and previous.active:
                raise BindingConflict(
                    f"Binding held by {previous.session} at generation {previous.generation}."
                )
            if isinstance(request.scope, EntityRef):
                for path in self.state.glob("*.json"):
                    existing = Binding.model_validate_json(path.read_bytes())
                    if (
                        existing.active
                        and existing.anchor == self.installation.store
                        and isinstance(existing.scope, EntityRef)
                        and existing.scope.document == request.scope.document
                    ):
                        raise BindingConflict(
                            "The entity document already has an active holder."
                        )
            return self._claim(request, previous)

    def recover_binding(
        self, request: BindRequest, identity: str, expected_generation: int
    ) -> tuple[Binding, Path]:
        if request.purpose == BindingPurpose.EVIDENCE and request.authority is None:
            raise AuthorityUnavailable(
                "Evidence binding requires existing recovery authority."
            )
        with self.lock():
            previous = self.lookup(request.scope)
            if (
                previous is None
                or not previous.active
                or (previous.identity, previous.generation)
                != (identity, expected_generation)
            ):
                raise BindingConflict(
                    "The binding recovery identity or generation is stale."
                )
            root = Path(previous.worktree)
            old = type(self.repo)(root, self.repo.ref)
            actual = Path(
                os.fsdecode(
                    old._git("rev-parse", "--absolute-git-dir").removesuffix(b"\n")
                )
            ).resolve()
            if (
                old.identity != self.repo.identity
                or str(actual) != previous.git_directory
            ):
                raise BindingConflict(
                    "The previous worktree identity cannot be verified."
                )
            export = (
                self.state
                / "recovery"
                / previous.identity
                / str(previous.generation)
                / uuid4().hex
            )
            export.mkdir(parents=True)
            removed = []
            for selected in previous.paths:
                data = read_workspace(root, selected.path)
                if data is None and selected.digest is not None:
                    removed.append(selected.path)
                elif data is not None and digest(data) != selected.digest:
                    _materialize(export, selected.path, data)
            _atomic_write(
                export / "receipt.json",
                {
                    "binding": previous.identity,
                    "generation": previous.generation,
                    "removed": removed,
                },
            )
            return self._claim(request, previous), export
