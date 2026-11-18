"""Run the pinned pre-commit obligations and emit an advisory JSON receipt."""

import json
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

from . import working_tree_report
from .local import Refusal, _capabilities, _checked, _prepare
from .snapshot import SnapshotUncertain

_PHASES = ("setup", "call", "teardown")


def _validate(invocation, nodes):
    receipt = invocation.receipt()
    _checked(
        set(receipt["collected"]) == set(nodes), "pytest collection differs from report"
    )
    reports = {node: [] for node in nodes}
    failed = False
    for phase in receipt["reports"]:
        _checked(isinstance(phase, dict), "invalid pytest phase")
        node = phase.get("nodeid")
        outcome = phase.get("outcome")
        _checked(
            isinstance(node, str)
            and node in reports
            and phase.get("when") in _PHASES
            and outcome in ("passed", "failed")
            and phase.get("wasxfail") is False,
            "unexpected pytest node, phase or outcome",
        )
        reports[node].append((phase["when"], outcome))
        failed |= outcome == "failed"

    for phases in reports.values():
        expected = (
            ("setup", "teardown") if phases[:1] == [("setup", "failed")] else _PHASES
        )
        _checked(
            tuple(phase for phase, _ in phases) == expected,
            "incomplete or unordered pytest phases",
        )

    _checked(
        invocation.returncode == int(failed),
        "pytest exit disagrees with phase outcomes",
    )
    return receipt


def run(repo: Path, base_commit: str) -> dict:
    report, snapshot = working_tree_report._report_with_snapshot(repo, base_commit)
    result = {
        "schema": "aitm.tia-working-tree-run/v1",
        "provenance": "local_advisory",
        "status": "unavailable",
        "exit_code": 2,
        "report": report,
        "invocation_id": None,
        "pytest_returncode": None,
        "worker_receipt": None,
    }
    if snapshot is None:
        return result | {"reason": report["reason"]}

    def recheck():
        current, _ = working_tree_report._report_with_snapshot(repo, base_commit)
        _checked(current == report, "snapshot-drift: checkout changed after admission")

    try:
        # As in the stock local runner, keep native fixture ancestors stable
        # and put all runtime writes outside the inspected checkout.
        cache = Path.home() / "Library/Caches"
        temp_root = (cache if cache.is_dir() else Path(tempfile.gettempdir())).resolve()
        _checked(
            not temp_root.is_relative_to(repo.resolve()),
            "scratch must be outside the checkout",
        )
        invocation_id = uuid4().hex
        with tempfile.TemporaryDirectory(
            prefix=f"aitm-tia-{invocation_id}-", dir=temp_root
        ) as directory:
            private = Path(directory)
            _capabilities(private)
            runtime = _prepare(snapshot, private / "runtime")
            recheck()
            result["invocation_id"] = invocation_id
            child = runtime.pytest("pinned", report["node_ids"], collect=False)
            result.update(
                pytest_returncode=child.returncode, pytest_seconds=child.seconds
            )
            if child.returncode:
                print(child.diagnostic, file=sys.stderr)
            result["worker_receipt"] = _validate(child, report["node_ids"])
            runtime.verify()
            recheck()
        return result | {
            "status": "failed" if child.returncode else "passed",
            "exit_code": child.returncode,
        }
    except (Refusal, SnapshotUncertain, OSError, ValueError) as error:
        return result | {"reason": str(error)}


def main(argv: list[str] | None = None) -> int:
    parser = working_tree_report._Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", required=True, type=Path, metavar="CHECKOUT")
    parser.add_argument("--base", required=True, metavar="COMMIT")
    try:
        args = parser.parse_args(argv)
    except working_tree_report._Unavailable:
        result = {
            "schema": "aitm.tia-working-tree-run/v1",
            "provenance": "local_advisory",
            "status": "unavailable",
            "exit_code": 2,
            "reason": "invalid-arguments",
        }
    else:
        result = run(args.repo, args.base)
    print(json.dumps(result, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
