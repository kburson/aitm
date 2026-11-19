"""Plan advisory test selection for an exact Git index, HEAD, or PR-tested tree."""

import argparse
import json
import tempfile
from pathlib import Path

from .local import (
    Refusal,
    _capabilities,
    _plan,
    _recheck,
    _scratch_root,
    _unavailable,
)
from .snapshot import ProbeRequest, SnapshotUncertain, resolve

_SCHEMA = "aitm.tia-advisory-probe/v1"


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Refusal("invalid-arguments")


def _request(args):
    pr = (args.pr_head, args.tested_commit, args.tested_tree)
    if args.input == "pr":
        if not all(pr):
            raise Refusal(
                "invalid-arguments: PR requires head, tested commit, and tree"
            )
    elif any(value is not None for value in pr):
        raise Refusal("invalid-arguments: PR identities require PR input")
    return ProbeRequest("local/checkout", args.input, args.parent, *pr)


def main(argv=None):
    parser = _Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repo", required=True, type=Path, metavar="CHECKOUT")
    parser.add_argument("--parent", required=True, metavar="FULL_COMMIT")
    parser.add_argument("--input", required=True, choices=("index", "head", "pr"))
    parser.add_argument("--pr-head", metavar="FULL_COMMIT")
    parser.add_argument("--tested-commit", metavar="FULL_COMMIT")
    parser.add_argument("--tested-tree", metavar="FULL_TREE")
    try:
        args = parser.parse_args(argv)
        request = _request(args)
        repo = args.repo.resolve(strict=True)
        before, after = resolve(repo, request)
        with tempfile.TemporaryDirectory(
            prefix="aitm-tia-probe-", dir=_scratch_root(repo)
        ) as directory:
            private = Path(directory)
            _capabilities(private)
            plan, _ = _plan(before, after, private, inspected_checkout=repo)
            _recheck(repo, request, (before.digest, after.digest))
    except (Refusal, SnapshotUncertain, OSError, ValueError) as error:
        plan = _unavailable(error)
    print(json.dumps({"schema": _SCHEMA, "provenance": "local_advisory", "plan": plan}))
    return 2 if plan["mode"] == "unavailable" else 0


if __name__ == "__main__":
    raise SystemExit(main())
