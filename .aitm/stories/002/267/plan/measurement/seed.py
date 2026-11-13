"""Apply one predeclared disposable change and restore only files it owns."""
import subprocess
import sys
from pathlib import Path

BASE = "766504a02aaeb9dda339d588172dd7d5bdbd2b3f"
CLI = "packages/aitm-usage/src/aitm_usage/cli.py"
README = "README.md"
GROK = "packages/aitm-usage/tests/fixtures/grok/headless.json"


def main():
    source = Path(sys.argv[1]).resolve()
    seed = sys.argv[2]
    if seed not in {"baseline", "cli", "non-code", "uncertain", "unavailable"}:
        raise ValueError(seed)
    git = ["git", "-C", str(source)]
    if subprocess.check_output([*git, "rev-parse", "HEAD"], text=True).strip() != BASE:
        raise ValueError("fixture must use the pinned revision")
    for name in (CLI, README, GROK):
        baseline = subprocess.check_output([*git, "show", f"{BASE}:{name}"])
        data = baseline
        if name == CLI and seed in {"cli", "unavailable"}:
            old = b'prog="aitm-usage"'
            assert baseline.count(old) == 1
            data = baseline.replace(old, b'prog="aitm-267-usage"')
        if name == README and seed == "non-code":
            data += b"\n#267 local advisory measurement documentation seed.\n"
        if name == GROK and seed == "uncertain":
            old = b"20000000-0000-4000-8000-000000000001"
            assert baseline.count(old) == 1
            data = baseline.replace(old, b"20000000-0000-4000-8000-000000000099")
        path = source / name
        if path.read_bytes() != data:
            path.write_bytes(data)
    print(subprocess.check_output([*git, "status", "--porcelain", "--untracked-files=all"], text=True), end="")


if __name__ == "__main__":
    main()
