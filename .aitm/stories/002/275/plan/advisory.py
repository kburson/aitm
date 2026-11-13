"""Read-only #275 experiment. No notification, merge, or pause mutations."""

from dataclasses import dataclass, field, replace
from datetime import datetime
import re

REPOSITORY = 1450406435
REPO = "kburson/aitm"
WORKFLOW = 412848571
PATH = ".github/workflows/ci.yml"
TARGET = "trunk"
REQUIRED = ("collect-evidence", "file-checks", "python", "quality")
RED = {"failure", "timed_out", "action_required"}
SHA = re.compile(r"[0-9a-f]{40}")


def time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class Attempt:
    run: int
    attempt: int
    sequence: int
    sha: str
    started: str
    status: str
    failures: tuple = ()
    gaps: tuple = ()

    @property
    def key(self):
        return f"{REPOSITORY}/{WORKFLOW}/{TARGET}/{self.sha}/{self.run}/{self.attempt}"

    @property
    def order(self):
        return self.sequence, self.attempt


def identify(run, current_sha):
    """Read GitHub attempt metadata from an authenticated, controller-owned readback."""
    if not SHA.fullmatch(current_sha):
        raise ValueError("invalid live target SHA")
    if (
        run["repository"]["id"] != REPOSITORY
        or run["head_repository"]["id"] != REPOSITORY
        or run["workflow_id"] != WORKFLOW
        or run["path"] != PATH
        or run["event"] != "push"
        or run["head_branch"] != TARGET
        or run["head_sha"] != current_sha
        or any(type(run[key]) is not int or run[key] <= 0
               for key in ("id", "run_attempt", "run_number"))
    ):
        raise ValueError("run is not canonical full CI for the current trunk SHA")
    time(run["run_started_at"])


def assess(run, jobs, current_sha, latest, artifact_verified):
    """Construct an advisory verdict after exact latest-run and artifact verification."""
    identify(run, current_sha)
    if (run["id"], run["run_attempt"]) != latest:
        raise ValueError("run or attempt is no longer the current latest")
    failures = []
    gaps = []
    for name in REQUIRED:
        candidates = [job for job in jobs if job["name"] == name]
        if len(candidates) != 1:
            gaps.append(f"{name}:missing-or-duplicate")
            continue
        [job] = candidates
        if (job["run_id"], job["run_attempt"], job["head_sha"]) != (
            run["id"], run["run_attempt"], current_sha,
        ):
            gaps.append(f"{name}:identity-mismatch")
        elif job["status"] != "completed":
            gaps.append(f"{name}:incomplete")
        elif job["conclusion"] in RED:
            failures.append(f"{name}:{job['conclusion']}")
        elif job["conclusion"] != "success":
            gaps.append(f"{name}:{job['conclusion']}")
    status = "pending"
    if failures:
        status = "red"
    elif run["status"] == "completed":
        if run["conclusion"] in RED:
            failures.append(f"workflow:{run['conclusion']}")
            status = "red"
        else:
            if run["conclusion"] != "success":
                gaps.append(f"workflow:{run['conclusion']}")
            if not artifact_verified:
                gaps.append("python-artifact:unverified")
            status = "incomplete" if gaps else "green"
    return Attempt(run["id"], run["run_attempt"], run["run_number"], current_sha,
                   run["run_started_at"], status, tuple(failures), tuple(gaps))


@dataclass
class Incident:
    """One in-memory advisory incident per protected target."""

    latest: tuple = (0, 0)
    seen: dict = field(default_factory=dict)
    active: bool = False
    version: int = 0
    failing: Attempt | None = None
    repair: tuple | None = None
    recovery: Attempt | None = None
    infrastructure_ready: tuple | None = None

    def observe(self, attempt):
        if attempt.order < self.latest:
            return "stale"
        self.latest = attempt.order
        if attempt.status == "pending":
            return "pending"
        prior = self.seen.get(attempt.key)
        if prior is not None:
            if prior == attempt or (
                prior.status == attempt.status and prior.gaps == attempt.gaps
                and set(attempt.failures) <= set(prior.failures)
            ):
                return "duplicate"
            if prior.status == "red" and attempt.status != "red":
                return "red-evidence-retained"
            if attempt.status in {"red", "incomplete"} and self.active and self.failing.key == attempt.key:
                merged = replace(attempt, failures=tuple(sorted(set(prior.failures) | set(attempt.failures))))
                self.failing = merged
                self.seen[attempt.key] = merged
                if prior.status != "red" and merged.status == "red":
                    self.infrastructure_ready = None
                    self.recovery = None
                return "same-attempt-evidence-updated"
        self.seen[attempt.key] = attempt
        if attempt.status in {"red", "incomplete"}:
            self.active = True
            self.version += 1
            self.failing = attempt
            self.repair = None
            self.recovery = None
            self.infrastructure_ready = None
            return "manual-stop-requested"
        if not self.active:
            return "green"
        if self.repair is not None:
            _, _, landed_sha, landed_at = self.repair
        elif self.infrastructure_ready is not None:
            landed_sha, landed_at = self.infrastructure_ready
        else:
            return "green-without-repair"
        if attempt.sha != landed_sha or time(attempt.started) <= time(landed_at):
            return "recovery-not-fresh"
        self.recovery = attempt
        return "manual-resume-available"

    def record_landed_repair(self, owner, pr, landed_sha, landed_at, current_sha):
        if not self.active or self.repair is not None or self.failing is None:
            raise ValueError("requires an active incident with no nominated repair")
        if (
            not owner or type(pr) is not int or pr <= 0
            or not SHA.fullmatch(landed_sha) or landed_sha != current_sha
            or landed_sha == self.failing.sha
            or time(landed_at) <= time(self.failing.started)
        ):
            raise ValueError("repair identity is not a fresh current-trunk result")
        self.repair = owner, pr, landed_sha, landed_at
        self.infrastructure_ready = None

    def confirm_infrastructure_recovered(self, incident_version, current_sha, ready_at):
        if (
            not self.active or self.failing is None or self.failing.status != "incomplete"
            or self.repair is not None or self.version != incident_version
            or self.failing.sha != current_sha or time(ready_at) <= time(self.failing.started)
        ):
            raise ValueError("requires confirmed infrastructure-only resolution for the current incident")
        self.infrastructure_ready = current_sha, ready_at

    def acknowledge_resume(self, version, recovery_key, current_sha):
        if (
            not self.active or self.recovery is None or self.version != version
            or self.recovery.key != recovery_key or self.recovery.sha != current_sha
            or self.recovery.order != self.latest
        ):
            raise ValueError("stale manual resume")
        self.active = False
        return "manually-resumed"
