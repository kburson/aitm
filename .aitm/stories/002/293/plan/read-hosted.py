"""Independently bind GitHub attempts and reconcile complete candidate outcomes."""

import json
import stat
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from urllib.parse import quote
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent
LAB = ROOT / "lab"
sys.path[:0] = [str(LAB), str(LAB / "source/tools/ci")]
from ci_advisory import authenticate_job
from experiment import BASE_REF, CLI, collection, git, line, read, reconcile
from verify_pr import GitHub, timestamp

REPO = "kburson/aitm-fast-validation-293"
PATH = ".github/workflows/qualification.yml"
ARTIFACT_LIMIT = 6 * 1024 * 1024


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def resource():
    github = GitHub(REPO)
    repository = read(ROOT / "lab-repository.json")
    assert github.document("")["id"] == repository["id"]
    branch = github.document(f"branches/{BASE_REF}")
    base = (ROOT / "lab-default-commit").read_text().strip()
    assert branch["protected"] and branch["commit"]["sha"] == base
    workflow = github.document("actions/workflows/qualification.yml")
    assert workflow["state"] == "active" and workflow["path"] == PATH
    assert (
        line("rev-parse", f"{base}:source") == read(LAB / "cases.json")["source_tree"]
    )
    assert git("show", f"{base}:{PATH}") == (LAB / PATH).read_bytes()
    assert git("show", f"{base}:experiment.py") == (LAB / "experiment.py").read_bytes()
    return github, repository["id"], base, workflow["id"]


def artifacts(github, repo_id, row, attempt, job, destination):
    run_id = row["id"]
    candidates = github.pages(
        f"actions/runs/{run_id}/artifacts?per_page=100", "artifacts"
    )
    match = [
        item
        for item in candidates
        if item["name"] == f"comparison-{job['name']}-a{attempt}"
    ]
    if not match:
        return None
    (item,) = match
    binding = item["workflow_run"]
    assert not item["expired"] and binding["id"] == run_id
    assert binding["repository_id"] == binding["head_repository_id"] == repo_id
    assert (
        binding["head_sha"] == row["head_sha"]
        and binding["head_branch"] == row["head_branch"]
    )
    assert (
        timestamp(job["started_at"])
        <= timestamp(item["created_at"])
        <= timestamp(job["completed_at"])
    )
    raw = github.api(f"actions/artifacts/{item['id']}/zip", limit=ARTIFACT_LIMIT)
    assert (
        item["size_in_bytes"] == len(raw)
        and item["digest"] == "sha256:" + sha256(raw).hexdigest()
    )
    (destination / f"{job['name']}.zip").write_bytes(raw)
    return item


def unpack(job, expected_mode, target, workload, spec, case, lane):
    with ZipFile(job) as archive, TemporaryDirectory() as scratch:
        files = archive.infolist()
        names = [f.orig_filename for f in files]
        assert (
            len(set(names)) == len(names)
            and sum(f.file_size for f in files) <= 16 * 1024 * 1024
        )
        for item in files:
            name = PurePosixPath(item.orig_filename)
            assert (
                not name.is_absolute()
                and ".." not in name.parts
                and len(name.parts) <= 2
            )
            assert not stat.S_ISLNK(item.external_attr >> 16)
            assert name.suffix in {".txt", ".log", ".json"} or item.is_dir()
        archive.extractall(scratch)
        folder = Path(scratch)
        evidence = read(folder / "result.json")
        assert evidence["schema"] == "aitm.qualification-293/v1"
        assert evidence["subject"] == target and evidence["lane"] == lane
        assert evidence["mode"] == expected_mode
        assert (
            evidence["catalog_sha256"]
            == sha256((LAB / "cases.json").read_bytes()).hexdigest()
        )
        assert (
            evidence["model_sha256"]
            == sha256((LAB / "workload.json").read_bytes()).hexdigest()
        )
        if lane == "fast" and expected_mode == "full-required":
            assert not evidence["cohorts"] and set(names) == {
                "start.json",
                "result.json",
            }
            return evidence
        policy = read(LAB / "source/tools/ci/policy.json")
        mandatory = set(policy["required_tests"]) | {CLI}
        inventory = collection(read(folder / "collection/pytest.json"))
        assert [n for n in inventory if n not in spec["new_ids"]] == workload[
            "cohorts"
        ]["full"]
        assert set(inventory) - set(workload["cohorts"]["full"]) == set(spec["new_ids"])
        assert set(evidence["cohorts"]) == {"full", "projected"} and evidence[
            "inventory_size"
        ] == len(inventory)
        for cohort, result in evidence["cohorts"].items():
            expected = inventory if cohort == "full" else workload["cohorts"][cohort]
            assert mandatory <= set(expected)
            if lane == "fast":
                expected = [
                    n
                    for n in expected
                    if n in mandatory
                    or (
                        target["source_path"] == case["fixture_path"]
                        and n.partition("::")[0] == case["fixture_consumer"]
                    )
                ]
            assert result["assigned"] == expected
            assert (
                folder / cohort / "assigned.txt"
            ).read_text().splitlines() == expected
            observed = reconcile(
                folder / cohort,
                expected,
                1 if lane == "fast" else 3,
                policy["optional_skips"],
                policy["required_children"],
            )
            assert all(result[k] == v for k, v in observed.items())
        return evidence


def candidate(github, repo_id, base, kind, catalog):
    directory = ROOT / "runs" / kind
    number = int((directory / "pr.txt").read_text().strip().rsplit("/", 1)[1])
    pull = github.document(f"pulls/{number}")
    assert (
        pull["state"] == "open"
        and pull["base"]["sha"] == base
        and pull["base"]["ref"] == BASE_REF
    )
    assert pull["base"]["repo"]["id"] == pull["head"]["repo"]["id"] == repo_id
    head, tested = pull["head"]["sha"], pull["merge_commit_sha"]
    git("fetch", "--no-tags", "origin", f"refs/pull/{number}/merge")
    assert line("rev-parse", "FETCH_HEAD") == tested
    assert line("show", "-s", "--format=%P", tested).split() == [base, head]
    spec = catalog["cases"][kind]
    assert git("diff", "--name-only", "-z", base, tested).split(b"\0") == [
        f"source/{spec['path']}".encode(),
        b"",
    ]
    assert line("rev-parse", f"{tested}:source/{spec['path']}") == spec["after"]
    result = {
        "repository": REPO,
        "repository_id": repo_id,
        "pull": number,
        "base": base,
        "head": head,
        "tested": tested,
        "tree": line("rev-parse", f"{tested}^{{tree}}"),
        "source_tree": line("rev-parse", f"{tested}:source"),
        "source_baseline": catalog["source_sha"],
        "case": kind,
        "source_path": spec["path"],
        "source_blob": spec["after"],
        "edit_frozen_at": line("show", "-s", "--format=%cI", head),
    }
    return result, pull["head"]["ref"], directory, pull["created_at"]


def compare(full, fast, spec):
    qualification, problems = {}, []
    control_fails = set(spec["known_failures"])
    for cohort, full_row in full["cohorts"].items():
        reference = full_row["outcomes"]
        fast_row = fast["cohorts"][cohort] if fast["mode"] == "selected" else full_row
        effective = fast_row["outcomes"]
        chosen = set(fast_row["assigned"])
        red = {n for n, v in reference.items() if v in {"failed", "setup-error"}}
        observed_red = {
            n for n, v in effective.items() if v in {"failed", "setup-error"}
        }
        if control_fails != red:
            problems.append(
                f"{cohort}: full result fails the preregistered witness expectations"
            )
        if "setup-error" in reference.values() or "setup-error" in effective.values():
            problems.append(f"{cohort}: unexpected setup failure")
        if red != observed_red:
            problems.append(f"{cohort}: effective verdict misses or adds failures")
        if any(effective[n] != reference.get(n) for n in chosen):
            problems.append(f"{cohort}: common assignment outcomes differ")
        qualification[cohort] = {
            "full_assignments": len(reference),
            "effective_assignments": len(effective),
            "full_failures": sorted(red),
            "effective_failures": sorted(observed_red),
            "missed_failures": sorted(red - observed_red),
            "extra_failures": sorted(observed_red - red),
            "omitted_assignments": sorted(set(reference) - chosen),
            "extra_assignments": sorted(chosen - set(reference)),
        }
    return qualification, problems


def main(kind):
    catalog, workload = read(LAB / "cases.json"), read(LAB / "workload.json")
    github, repo_id, base, workflow = resource()
    subject, head_ref, destination, opened_at = candidate(
        github, repo_id, base, kind, catalog
    )
    rows = github.pages(
        f"actions/workflows/{workflow}/runs?event=pull_request&branch={quote(head_ref, safe='')}&per_page=100",
        "workflow_runs",
    )
    (row,) = [row for row in rows if row["head_sha"] == subject["head"]]
    assert (
        row["event"] == "pull_request"
        and row["path"] == PATH
        and row["workflow_id"] == workflow
    )
    assert row["repository"]["id"] == row["head_repository"]["id"] == repo_id
    assert row["status"] == "completed", f"{kind} run {row['id']} still {row['status']}"
    suite = github.document(f"check-suites/{row['check_suite_id']}")
    assert (
        suite["head_sha"] == row["head_sha"]
        and suite["app"]["slug"] == "github-actions"
    )
    attempt = row["run_attempt"]
    binding = github.document(f"actions/runs/{row['id']}/attempts/{attempt}")
    assert (
        binding["id"] == row["id"]
        and binding["run_attempt"] == attempt
        and binding["head_sha"] == row["head_sha"]
    )
    jobs = github.pages(
        f"actions/runs/{row['id']}/attempts/{attempt}/jobs?per_page=100", "jobs"
    )
    assert sorted(j["name"] for j in jobs) == ["fast", "full"]
    attempt_dir = destination / f"attempt-{attempt}"
    attempt_dir.mkdir(exist_ok=True)
    (attempt_dir / "tested-commit.txt").write_bytes(
        git("cat-file", "commit", subject["tested"])
    )
    save(attempt_dir / "subject.json", subject)
    provider_evidence = {
        "run": row["id"],
        "attempt": attempt,
        "workflow_id": workflow,
        "pull_opened_at": opened_at,
        "registered_at": row["created_at"],
        "jobs": {},
    }
    for job in jobs:
        authenticate_job(github, job, row, suite, Counter(j["id"] for j in jobs))
        meta = artifacts(github, repo_id, row, attempt, job, attempt_dir)
        provider_evidence["jobs"][job["name"]] = {
            **{
                k: job[k]
                for k in ("id", "status", "conclusion", "started_at", "completed_at")
            },
            "artifact": None
            if meta is None
            else {k: meta[k] for k in ("id", "digest", "size_in_bytes")},
        }
    save(attempt_dir / "provider.json", provider_evidence)
    assert row["conclusion"] == "success" and all(
        j["conclusion"] == "success" for j in jobs
    ), provider_evidence
    spec = catalog["cases"][kind]
    fast, full = [
        unpack(
            attempt_dir / f"{lane}.zip",
            spec["mode"],
            subject,
            workload,
            spec,
            catalog,
            lane,
        )
        for lane in ("fast", "full")
    ]
    assert (
        (fast["run"], fast["attempt"])
        == (full["run"], full["attempt"])
        == (row["id"], attempt)
    )
    compared, problems = compare(full, fast, spec)
    jobs_by_name = {j["name"]: j for j in jobs}
    duration = lambda end, start: (timestamp(end) - timestamp(start)).total_seconds()
    ends = {k: j["completed_at"] for k, j in jobs_by_name.items()}
    effective = (
        ends["fast"]
        if fast["mode"] == "selected"
        else max(ends.values(), key=timestamp)
    )
    assert candidate(github, repo_id, base, kind, catalog)[0] == subject
    assert github.document(f"actions/runs/{row['id']}")["run_attempt"] == attempt
    outcome = {
        "subject": subject,
        "mode": fast["mode"],
        "problems": problems,
        "comparison": compared,
        "provider": provider_evidence,
        "timing": {
            "first_trigger_to_effective": duration(effective, opened_at),
            "registration_to_effective": duration(effective, row["created_at"]),
            "registration_delay": duration(row["created_at"], opened_at),
            "edit_commit_to_effective": duration(effective, subject["edit_frozen_at"]),
            "first_trigger_to_full_reference": duration(ends["full"], opened_at),
            "queues": {
                k: duration(j["started_at"], row["created_at"])
                for k, j in jobs_by_name.items()
            },
            "job_seconds": {
                k: duration(j["completed_at"], j["started_at"])
                for k, j in jobs_by_name.items()
            },
            "pytest_seconds": {
                "fast": {k: v["seconds"] for k, v in fast["cohorts"].items()},
                "full": {k: v["seconds"] for k, v in full["cohorts"].items()},
            },
        },
    }
    save(destination / "verified.json", outcome)
    print(kind, attempt, outcome["mode"], outcome["timing"], problems)


if __name__ == "__main__":
    main(sys.argv[1])
