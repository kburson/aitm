"""Fetch literal remote refs and admit only pinned evidence under the clone gate."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, fields, replace
from enum import StrEnum
from hashlib import new as new_hash
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from aitm_core.config import PolicyUnavailable, resolve_policy
from aitm_core.models.common import LocalOutcome, RefObservation, RefreshResult
from aitm_core.store.continuity import (
    ContinuityAnchor,
    ContinuityStatus,
    SharedFrontier,
    observe_shared,
    unavailable_shared,
)
from aitm_core.store.gate import (
    Gate,
    RefIdentity,
    RefMutationKind,
    _receipt_path,
    ref_gate,
)
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.validation import (
    ForwardRepairVerifier,
    ValidationReport,
    validate_history,
)


class Freshness(StrEnum):
    LOCAL_ONLY = "local-only"
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"
    FENCED = "fenced"


@dataclass(frozen=True, slots=True)
class RefreshPolicy:
    installation: Installation
    trusted_checkpoint: str | None = None
    forward_repair_verifier: ForwardRepairVerifier | None = None


class RefreshedViews(RefreshResult):
    planning: RefObservation
    shared: SharedFrontier | None
    code_freshness: Freshness
    code_reason: str | None = None


@dataclass(frozen=True, slots=True)
class _CandidateInstallation(Installation):
    candidate_ref: str = ""

    @property
    def validated_code_ref(self) -> str | None:
        return self.candidate_ref


@dataclass(frozen=True, slots=True)
class _Fetched:
    observation: RefObservation | None = None
    ref: str | None = None
    reason: str | None = None
    invalid: bool = False


@dataclass(frozen=True, slots=True)
class _Code:
    observation: RefObservation
    freshness: Freshness
    reason: str | None = None


class _JournalEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    route: str
    previous: str | None
    frontier: SharedFrontier
    writer_before: str | None
    writer_after: str | None
    code: str
    recovery_ref: str | None = None
    transport_ref: str | None = None


@dataclass(frozen=True, slots=True)
class _Journal:
    accepted: _JournalEntry | None
    pending: _JournalEntry | None
    marker: str | None
    pending_marker: str | None


def _direct_ref(repository: Repository, name: str) -> str | None:
    symbolic = repository._run("symbolic-ref", "-q", name)
    if symbolic.returncode == 0:
        raise ValidationRejected(f"refresh ref must be direct: {name}")
    if symbolic.returncode != 1:
        raise GitCommandError("symbolic-ref", symbolic.stderr)
    result = repository._run("rev-parse", "--verify", "--quiet", name)
    if result.returncode == 1:
        return None
    if result.returncode:
        raise GitCommandError("rev-parse", result.stderr)
    return repository._oid(result.stdout.strip().decode("ascii"))


def _is_ancestor(repository: Repository, old: str, new: str) -> bool | None:
    result = repository._run(
        "merge-base", "--is-ancestor", repository._oid(old), repository._oid(new)
    )
    return {0: True, 1: False}.get(result.returncode)


def _fetch(repository: Repository, route: str, target: str, lane: str) -> _Fetched:
    repository._git("check-ref-format", f"refs/remotes/{route}/HEAD")
    repository._git("check-ref-format", target)
    endpoint = repository._run("remote", "get-url", "--", route)
    if endpoint.returncode:
        return _Fetched(reason=f"configured {lane} remote is unavailable")
    url = os.fsdecode(endpoint.stdout.removesuffix(b"\n"))
    observation = repository._run(
        "ls-remote", "--refs", "--exit-code", "--", url, target
    )
    if observation.returncode == 2:
        return _Fetched(RefObservation(ref=target, remote=route, observed_commit=None))
    if observation.returncode:
        return _Fetched(reason=f"cannot observe anchored {lane} remote")
    try:
        (line,) = observation.stdout.decode("utf-8").splitlines()
        revision, witnessed_ref = line.split("\t")
        if witnessed_ref != target:
            raise ValueError("ref mismatch")
        repository._oid(revision)
    except ValueError:
        return _Fetched(
            reason=f"ambiguous anchored {lane} remote observation", invalid=True
        )

    candidate_ref = f"refs/aitm/candidates/{lane}-{uuid4().hex}"
    fetched = repository._run(
        "-c",
        "fetch.prune=false",
        "-c",
        "fetch.pruneTags=false",
        "fetch",
        "--no-tags",
        "--no-recurse-submodules",
        "--no-write-fetch-head",
        "--no-auto-maintenance",
        "--refmap=",
        "--",
        url,
        f"+{target}:{candidate_ref}",
    )
    if fetched.returncode or _direct_ref(repository, candidate_ref) != revision:
        return _Fetched(
            ref=candidate_ref,
            reason=f"anchored {lane} ref changed or could not be fetched",
        )
    return _Fetched(
        RefObservation(ref=target, remote=route, observed_commit=revision),
        candidate_ref,
    )


def _write_ref(
    repository: Repository, name: str, value: str, previous: str | None
) -> None:
    repository._git(
        "update-ref", "--no-deref", name, value, previous or "0" * repository.oid_length
    )


def _keep(repository: Repository, name: str, revision: str) -> None:
    before = _direct_ref(repository, name)
    if before is None:
        _write_ref(repository, name, revision, None)
    elif before != revision:
        raise ValidationRejected(f"retained refresh pin moved: {name}")


def _code_pin(repository: Repository, revision: str) -> str:
    return f"refs/aitm/code-pins/{repository._oid(revision)}"


def _drop_candidate(repository: Repository, fetched: _Fetched) -> None:
    if fetched.ref is not None:
        revision = _direct_ref(repository, fetched.ref)
        if revision is not None:
            repository._git("update-ref", "--no-deref", "-d", fetched.ref, revision)


def _read_code(installation: Installation) -> _Code:
    repository = installation.repository
    target = installation.validated_code_ref or installation.store.code_default_ref
    observation = RefObservation(
        ref=installation.code_remote_ref or installation.store.code_default_ref,
        remote=installation.code_remote,
        observed_commit=_direct_ref(repository, target),
    )
    if observation.observed_commit is None:
        return _Code(
            observation,
            Freshness.UNKNOWN,
            "there is no admitted code-default observation",
        )
    if installation.code_remote is not None:
        baseline = _direct_ref(repository, installation.store.code_default_ref)
        if (
            baseline is None
            or _is_ancestor(repository, baseline, observation.observed_commit)
            is not True
        ):
            return _Code(
                observation,
                Freshness.FENCED,
                "cached code pin disagrees with anchored code-default history",
            )
    try:
        pinned = resolve_policy(installation, RefreshResult(local=observation))
    except PolicyUnavailable as error:
        return _Code(observation, Freshness.FENCED, str(error))
    if pinned.writes_fenced:
        return _Code(
            observation,
            Freshness.FENCED,
            "committed routing requires explicit reconfiguration",
        )
    if installation.code_remote is not None:
        return _Code(
            observation,
            Freshness.STALE,
            "using the last validated code-default observation",
        )
    return _Code(observation, Freshness.LOCAL_ONLY)


def _admit_code(installation: Installation, cached: _Code, fetched: _Fetched) -> _Code:
    if installation.code_remote is None:
        return cached
    repository = installation.repository
    candidate = fetched.observation
    if candidate is None:
        return replace(
            cached,
            freshness=Freshness.FENCED if fetched.invalid else cached.freshness,
            reason=fetched.reason or cached.reason,
        )
    revision = candidate.observed_commit
    if revision is None:
        return replace(
            cached,
            freshness=Freshness.FENCED,
            reason="the anchored code-default ref is absent",
        )
    baseline = _direct_ref(repository, installation.store.code_default_ref)
    prior = cached.observation.observed_commit
    if (
        baseline is None
        or _is_ancestor(repository, baseline, revision) is not True
        or prior is not None
        and _is_ancestor(repository, prior, revision) is not True
    ):
        return replace(
            cached,
            freshness=Freshness.FENCED,
            reason="cannot prove anchored code-default continuity",
        )

    assert fetched.ref is not None
    candidate_installation = _CandidateInstallation(
        **{
            field.name: getattr(installation, field.name)
            for field in fields(Installation)
        },
        candidate_ref=fetched.ref,
    )
    try:
        settings = resolve_policy(
            candidate_installation, RefreshResult(local=candidate)
        )
    except PolicyUnavailable as error:
        return replace(cached, freshness=Freshness.FENCED, reason=str(error))
    if settings.writes_fenced:
        return replace(
            cached,
            freshness=Freshness.FENCED,
            reason="committed routing requires explicit reconfiguration",
        )
    target = installation.validated_code_ref
    assert target is not None
    if revision != cached.observation.observed_commit:
        _write_ref(repository, target, revision, cached.observation.observed_commit)
    return _Code(candidate, Freshness.FRESH)


class _ContinuityStore:
    def __init__(self, policy: RefreshPolicy):
        self.policy = policy
        self.installation = policy.installation
        self.repository = self.installation.repository
        self.store = self.installation.store
        self.route = sha256(
            "\0".join(
                (
                    self.store.store_uuid,
                    self.installation.planning_repository,
                    self.store.planning_ref,
                    self.store.planning_remote or "",
                    self.store.root_commit,
                )
            ).encode()
        ).hexdigest()
        directory = self.repository._git(
            "rev-parse", "--path-format=absolute", "--git-common-dir"
        )
        self.state = Path(os.fsdecode(directory.removesuffix(b"\n"))) / "aitm"
        self.journal = self.state / "continuity" / f"{self.route}.jsonl"
        prefix = f"refs/aitm/planning/{self.route}"
        self.marker_ref = f"{prefix}/journal"
        self.checkpoint_ref = f"{prefix}/checkpoint"
        self.valid_ref = f"{prefix}/valid"

    def writer(self) -> RefObservation:
        return RefObservation(
            ref=self.store.planning_ref,
            observed_commit=_direct_ref(self.repository, self.store.planning_ref),
        )

    def _oid(self, raw: bytes) -> str:
        algorithm = {40: "sha1", 64: "sha256"}[self.repository.oid_length]
        return new_hash(algorithm, f"blob {len(raw)}\0".encode() + raw).hexdigest()

    def _entry(self, line: bytes, previous: str | None) -> _JournalEntry:
        entry = _JournalEntry.model_validate_json(line)
        if entry.route != self.route or entry.previous != previous:
            raise ValueError("continuity journal identity or append order disagrees")
        frontier = entry.frontier
        remote = frontier.observation
        if remote is None or (remote.ref, remote.remote) != (
            self.store.planning_ref,
            self.store.planning_remote,
        ):
            raise ValueError(
                "continuity journal observation is outside the anchored route"
            )
        if frontier.status in {
            ContinuityStatus.LOCAL_ONLY,
            ContinuityStatus.STALE,
            ContinuityStatus.UNKNOWN,
            ContinuityStatus.ROUTE_MISMATCH,
        }:
            raise ValueError(
                "continuity journal contains no established remote decision"
            )
        candidate = remote.observed_commit
        if (frontier.status is ContinuityStatus.DELETED) != (candidate is None):
            raise ValueError("continuity journal deletion and observation disagree")
        if (
            frontier.status in {ContinuityStatus.VERIFIED, ContinuityStatus.QUARANTINED}
            and frontier.checkpoint != candidate
            or frontier.status is ContinuityStatus.VERIFIED
            and frontier.valid_tip != candidate
        ):
            raise ValueError(
                "continuity journal frontier does not bind the exact observation"
            )
        if entry.transport_ref is not None and (
            candidate is None
            or re.fullmatch(
                r"refs/aitm/candidates/planning-[0-9a-f]{32}", entry.transport_ref
            )
            is None
        ):
            raise ValueError(
                "continuity journal does not name a private planning candidate ref"
            )
        for revision in (
            entry.writer_before,
            entry.writer_after,
            entry.code,
            frontier.checkpoint,
            frontier.valid_tip,
            remote.observed_commit,
        ):
            if revision is not None:
                self.repository._oid(revision)
        if entry.writer_after != entry.writer_before and (
            frontier.fences_shared
            or frontier.local_diverged
            or entry.writer_after != frontier.valid_tip
        ):
            raise ValueError(
                "continuity journal describes an unapproved writer transition"
            )
        return entry

    def read(self) -> _Journal:
        repository = self.repository
        marker = _direct_ref(repository, self.marker_ref)
        checkpoint = _direct_ref(repository, self.checkpoint_ref)
        valid = _direct_ref(repository, self.valid_ref)
        try:
            payload = self.journal.read_bytes()
        except FileNotFoundError:
            if marker is not None or checkpoint is not None or valid is not None:
                raise ValueError(
                    "continuity journal is missing while retained refs exist"
                ) from None
            return _Journal(None, None, None, None)
        if not payload.endswith(b"\n"):
            raise ValueError("continuity journal is empty or has a partial record")

        entries = []
        latest = None
        for line in payload.splitlines(keepends=True):
            entry = self._entry(line, latest)
            latest = self._oid(line)
            entries.append((latest, entry))

        pending = None
        pending_marker = None
        if latest != marker:
            pending_marker, pending = entries.pop()
            if (entries[-1][0] if entries else None) != marker:
                raise ValueError(
                    "continuity journal marker disagrees with its append history"
                )
        accepted = entries[-1][1] if entries else None
        if (checkpoint, valid) != (
            (accepted.frontier.checkpoint, accepted.frontier.valid_tip)
            if accepted
            else (None, None)
        ):
            raise ValueError("continuity journal and retained frontier refs disagree")
        return _Journal(accepted, pending, marker, pending_marker)

    def _ancestry(self, old: str, new: str) -> bool | None:
        return _is_ancestor(self.repository, old, new)

    def anchor(
        self,
        accepted: _JournalEntry | None,
        writer: RefObservation,
        code: str | None = None,
    ) -> ContinuityAnchor:
        checkpoint = self.policy.trusted_checkpoint or self.store.root_commit
        self.repository._oid(checkpoint)
        if accepted is not None:
            established = accepted.frontier.checkpoint
            if (
                self.policy.trusted_checkpoint is not None
                and self._ancestry(checkpoint, established) is not True
            ):
                raise ValueError(
                    "trusted checkpoint disagrees with the established continuity journal"
                )
            checkpoint = established
        return ContinuityAnchor(
            self.store,
            checkpoint,
            accepted.frontier if accepted else None,
            self._ancestry,
            lambda tip: self.validate(tip, code),
            writer.observed_commit,
        )

    def validate(self, tip: str, code: str | None) -> ValidationReport:
        if code is None:
            return ValidationReport(
                LocalOutcome.UNAVAILABLE, tip, "no independently admitted code pin"
            )
        pin = _code_pin(self.repository, code)
        if _direct_ref(self.repository, pin) != code:
            return ValidationReport(
                LocalOutcome.UNAVAILABLE, tip, "admitted code pin could not be verified"
            )
        anchor = self.store.model_copy(update={"code_default_ref": pin})
        verifier = self.policy.forward_repair_verifier

        def verify(_pinned_anchor, diagnosis, candidate):
            assert verifier is not None
            return verifier(self.store, diagnosis, candidate)

        return validate_history(
            anchor,
            tip,
            repository=self.repository,
            forward_repair_verifier=verify if verifier is not None else None,
        )

    def append(self, entry: _JournalEntry) -> str:
        raw = entry.model_dump_json().encode() + b"\n"
        marker = (
            self.repository._git("hash-object", "-w", "--stdin", data=raw)
            .strip()
            .decode("ascii")
        )
        if marker != self._oid(raw):
            raise ValueError(
                "continuity journal marker does not identify its exact bytes"
            )
        self.journal.parent.mkdir(parents=True, exist_ok=True)
        new = not self.journal.exists()
        with self.journal.open("ab") as writer:
            writer.write(raw)
            writer.flush()
            os.fsync(writer.fileno())
        if new:
            directory = os.open(self.journal.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        return marker

    def publish(
        self,
        journal: _Journal,
        entry: _JournalEntry,
        marker: str,
        writer: RefObservation,
        gate: Gate,
    ) -> None:
        repository = self.repository
        if writer.observed_commit != entry.writer_before:
            raise ValidationRejected(
                "pending continuity journal disagrees with the exact local writer ref"
            )
        if entry.writer_after != entry.writer_before:
            assert entry.writer_after is not None
            before = repository.read_tree(entry.writer_before or self.store.root_commit)
            candidate = repository.read_tree(entry.writer_after)
            # The C06 gate validates the exact candidate against the retained
            # code pin and checks the literal planning worktree.
            gate.planning_validation = lambda tip: self.validate(tip, entry.code)
            gate(before, candidate)

        old = journal.accepted.frontier if journal.accepted else None
        changes = (
            (
                self.checkpoint_ref,
                old.checkpoint if old else None,
                entry.frontier.checkpoint,
            ),
            (self.valid_ref, old.valid_tip if old else None, entry.frontier.valid_tip),
            (self.store.planning_ref, entry.writer_before, entry.writer_after),
            (self.marker_ref, journal.marker, marker),
        )
        zero = "0" * repository.oid_length
        commands = ["start"]
        for ref, prior, current in changes:
            commands.append("option no-deref")
            if prior == current:
                commands.append(f"verify {ref} {prior or zero}")
            elif current is None:
                commands.append(f"delete {ref} {prior}")
            else:
                commands.append(f"update {ref} {current} {prior or zero}")
        commands.extend(("prepare", "commit", ""))
        gate.assert_excluded()
        repository._git(
            "update-ref", "--stdin", data="\n".join(commands).encode("utf-8")
        )

    def recover(
        self, journal: _Journal, writer: RefObservation, gate: Gate
    ) -> str | None:
        entry, marker = journal.pending, journal.pending_marker
        assert entry is not None and marker is not None
        observation = entry.frontier.observation
        assert observation is not None
        if observation.observed_commit is not None and (
            entry.transport_ref is None
            or _direct_ref(self.repository, entry.transport_ref)
            != observation.observed_commit
        ):
            raise ValidationRejected(
                "pending continuity observation has no exact retained fetch ref"
            )
        anchor = self.anchor(journal.accepted, writer, entry.code)
        if observe_shared(anchor, observation) != entry.frontier:
            raise ValidationRejected(
                "pending continuity decision disagrees with independent retained evidence"
            )
        self.publish(journal, entry, marker, writer, gate)
        return entry.transport_ref

    def blocked(
        self, reason: str, accepted: _JournalEntry | None = None
    ) -> SharedFrontier:
        known = accepted.frontier if accepted else None
        return SharedFrontier(
            ContinuityStatus.UNPROVABLE,
            known.checkpoint
            if known
            else self.policy.trusted_checkpoint or self.store.root_commit,
            known.valid_tip if known else None,
            known.observation if known else None,
            known.first_observation_limit
            if known
            else self.policy.trusted_checkpoint is None,
            local_diverged=known.local_diverged if known else False,
            reason=reason,
        )

    def _recovery(self, observation: RefObservation) -> str | None:
        revision = observation.observed_commit
        if revision is None:
            return None
        name = f"refs/aitm/recovery/c08-{self.route}/{revision}"
        _keep(self.repository, name, revision)
        return name

    def admit(
        self,
        journal: _Journal,
        writer: RefObservation,
        code: _Code,
        fetched: _Fetched,
        gate: Gate,
    ) -> tuple[SharedFrontier, str | None]:
        observation = fetched.observation
        revision = code.observation.observed_commit
        anchor = self.anchor(journal.accepted, writer, revision)
        cached = journal.accepted
        if observation is None:
            reason = fetched.reason or "shared planning observation is unavailable"
            if fetched.invalid:
                return self.blocked(
                    reason, cached
                ), cached.recovery_ref if cached else None
            previous = cached.frontier if cached else None
            if previous is not None and previous.fences_shared:
                return previous, cached.recovery_ref
            return unavailable_shared(
                anchor, reason
            ), cached.recovery_ref if cached else None
        if revision is None or code.freshness is Freshness.FENCED:
            return self.blocked(
                "cannot admit shared planning while committed code policy is unavailable",
                cached,
            ), self._recovery(observation)

        frontier = observe_shared(anchor, observation)
        after = writer.observed_commit
        if (
            frontier.status is ContinuityStatus.VERIFIED
            and not frontier.local_diverged
            and code.freshness in {Freshness.FRESH, Freshness.LOCAL_ONLY}
        ):
            after = frontier.valid_tip
        recovery_ref = self._recovery(observation) if frontier.fences_shared else None
        if (
            cached is not None
            and frontier == cached.frontier
            and after == writer.observed_commit
            and recovery_ref == cached.recovery_ref
        ):
            return frontier, recovery_ref
        entry = _JournalEntry(
            route=self.route,
            previous=journal.marker,
            frontier=frontier,
            writer_before=writer.observed_commit,
            writer_after=after,
            code=revision,
            recovery_ref=recovery_ref,
            transport_ref=fetched.ref,
        )
        marker = self.append(entry)
        self.publish(journal, entry, marker, writer, gate)
        return frontier, recovery_ref


def _view(
    writer: RefObservation,
    code: _Code,
    shared: SharedFrontier | None,
    candidate: RefObservation | None = None,
    recovery: str | None = None,
) -> RefreshedViews:
    return RefreshedViews(
        local=code.observation,
        candidate=candidate,
        recovery_ref=recovery,
        planning=writer,
        shared=shared,
        code_freshness=code.freshness,
        code_reason=code.reason,
    )


def _unreadable(policy: RefreshPolicy, reason: str) -> RefreshedViews:
    installation = policy.installation
    store = installation.store
    code = RefObservation(
        ref=installation.code_remote_ref or store.code_default_ref,
        observed_commit=None,
        remote=installation.code_remote,
    )
    writer = RefObservation(ref=store.planning_ref, observed_commit=None)
    shared = SharedFrontier(
        ContinuityStatus.UNPROVABLE,
        policy.trusted_checkpoint or store.root_commit,
        None,
        None,
        store.planning_remote is not None and policy.trusted_checkpoint is None,
        reason=reason,
    )
    return _view(writer, _Code(code, Freshness.FENCED, reason), shared)


def cached_refs(policy: RefreshPolicy) -> RefreshedViews:
    """Inspect cached views without network, lock acquisition or ref movement."""
    try:
        state = _ContinuityStore(policy)
        writer = state.writer()
    except (GitCommandError, OSError, ValueError) as error:
        return _unreadable(policy, str(error))
    try:
        code = _read_code(state.installation)
    except (GitCommandError, OSError, ValueError) as error:
        code = _Code(
            _unreadable(policy, str(error)).local, Freshness.FENCED, str(error)
        )
    persisted = None
    try:
        if state.store.planning_remote is None:
            return _view(
                writer,
                code,
                unavailable_shared(state.anchor(None, writer), "local-only"),
            )
        current = state.read()
        persisted = current.accepted
        target = RefIdentity(state.store.planning_ref)
        if _receipt_path(state.state, target).exists():
            raise ValidationRejected(
                "planning ref is fenced pending explicit checkout reconciliation"
            )
        if current.pending is not None:
            raise ValidationRejected(
                "pending continuity journal requires explicit refresh recovery"
            )
        anchor = state.anchor(persisted, writer, code.observation.observed_commit)
        shared = unavailable_shared(anchor, "no fresh shared observation")
    except (GitCommandError, OSError, ValueError) as error:
        shared = state.blocked(str(error), persisted)
    return _view(
        writer, code, shared, recovery=persisted.recovery_ref if persisted else None
    )


def _cleanup(repository: Repository, candidates: list[_Fetched]) -> str | None:
    try:
        for candidate in candidates:
            _drop_candidate(repository, candidate)
    except (GitCommandError, OSError, ValueError):
        return "a private refresh candidate could not be released"
    return None


def _cleanup_fence(
    state: _ContinuityStore, current: RefreshedViews, reason: str
) -> RefreshedViews:
    # Preserve established refusal evidence and fence either lane that could
    # otherwise treat a partial refresh as usable.
    shared = current.shared
    if shared is None:
        shared = state.blocked(reason)
    elif not shared.fences_shared:
        shared = replace(shared, status=ContinuityStatus.UNPROVABLE, reason=reason)
    return current.model_copy(
        update={
            "shared": shared,
            "code_freshness": Freshness.FENCED,
            "code_reason": f"{current.code_reason}. {reason}"
            if current.code_reason
            else reason,
        }
    )


def refresh_refs(policy: RefreshPolicy) -> RefreshedViews:
    """Fetch private candidates, then recover and admit them under the clone gate."""
    try:
        state = _ContinuityStore(policy)
    except (GitCommandError, OSError, ValueError) as error:
        return _unreadable(policy, str(error))
    repository = state.repository
    installation = state.installation
    target = RefIdentity(state.store.planning_ref)

    for _ in range(3):
        cached = cached_refs(policy)
        before = None
        code_fetch = planning_fetch = _Fetched()
        result = None
        recovered_ref = None
        try:
            if state.store.planning_remote is not None:
                before = state.read()
            initial_code = _read_code(installation)
            if installation.code_remote is not None:
                assert installation.code_remote_ref is not None
                code_fetch = _fetch(
                    repository,
                    installation.code_remote,
                    installation.code_remote_ref,
                    "code",
                )
            if state.store.planning_remote is not None:
                planning_fetch = _fetch(
                    repository,
                    state.store.planning_remote,
                    state.store.planning_ref,
                    "planning",
                )
            if state.store.planning_remote is None and installation.code_remote is None:
                return cached
            lock_target = target
            if (
                state.store.planning_remote is None
                and installation.validated_code_ref is not None
            ):
                lock_target = RefIdentity(installation.validated_code_ref)
            with ref_gate(repository, lock_target, RefMutationKind.PLANNING) as gate:
                writer = state.writer()
                journal = (
                    state.read() if state.store.planning_remote is not None else None
                )
                code = _read_code(installation)
                if (
                    before == journal
                    and writer == cached.planning
                    and code == initial_code
                ):
                    if journal is not None and journal.pending is not None:
                        recovered_ref = state.recover(journal, writer, gate)
                    else:
                        code = _admit_code(installation, code, code_fetch)
                        revision = code.observation.observed_commit
                        if (
                            revision is not None
                            and code.freshness is not Freshness.FENCED
                        ):
                            _keep(repository, _code_pin(repository, revision), revision)
                        if journal is None:
                            result = _view(
                                writer,
                                code,
                                unavailable_shared(
                                    state.anchor(None, writer), "local-only"
                                ),
                            )
                        else:
                            shared, recovery = state.admit(
                                journal, writer, code, planning_fetch, gate
                            )
                            result = _view(
                                state.writer(),
                                code,
                                shared,
                                planning_fetch.observation,
                                recovery,
                            )
        except (GitCommandError, OSError, ValueError) as error:
            current = cached_refs(policy)
            previous = before.accepted if before else None
            # Aborted adoption leaves any fetched refs reachable, both for
            # diagnosis and for replay of the pending durable journal.
            return current.model_copy(
                update={
                    "candidate": planning_fetch.observation,
                    "shared": state.blocked(str(error), previous),
                    "recovery_ref": planning_fetch.ref or current.recovery_ref,
                }
            )

        disposables = [planning_fetch, _Fetched(ref=recovered_ref)]
        if result is None or result.code_freshness is not Freshness.FENCED:
            disposables.append(code_fetch)
        failure = _cleanup(repository, disposables)
        if failure is not None:
            return _cleanup_fence(state, result or cached_refs(policy), failure)
        if result is not None:
            return result

    current = cached_refs(policy)
    return current.model_copy(
        update={
            "shared": state.blocked(
                "refresh state changed repeatedly while the remote observation was in flight"
            )
        }
    )
