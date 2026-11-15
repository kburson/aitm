"""Exercise the exact source-bound nested pytest that invalidated the first matrix."""

import os
import subprocess
import sys
import tarfile
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
from lab.experiment import PRODUCT, git, line, pytest, verify_archive

CASES = (
    "tools/ci/tests/test_pytest_evidence.py"
    "::test_candidate_records_both_normally_exiting_subprocesses"
)


def rejects(source, tree, cache_target=None):
    try:
        verify_archive(source, tree, cache_target)
    except ValueError as error:
        print(error)
    else:
        raise AssertionError("expected archive verification to reject the changed copy")


with TemporaryDirectory(
    prefix="aitm293-cache-", dir=Path.home() / "Library/Caches"
) as scratch:
    work = Path(scratch)
    tree = line("rev-parse", "HEAD:source")
    source, temporary, home, evidence = (
        work / name for name in ("source", "temp", "home", "evidence")
    )
    for directory in (source, temporary, home, evidence):
        directory.mkdir()
    with tarfile.open(fileobj=BytesIO(git("archive", tree))) as archive:
        archive.extractall(source, filter="data")
    verify_archive(source, tree)
    env = {
        "PATH": os.environ["PATH"],
        "HOME": str(home),
        "TMPDIR": str(temporary),
        "UV_PROJECT_ENVIRONMENT": str(work / "venv"),
        "UV_PYTHON_INSTALL_DIR": str(Path.home() / ".local/share/uv/python"),
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": f"{source / 'tools/ci'}:{source / PRODUCT / 'src'}",
        "AITM_CI_CHILD_EVIDENCE": "1",
    }
    subprocess.run(
        [
            "uv",
            "sync",
            "--locked",
            "--no-config",
            "--python",
            "3.13.9",
            "--project",
            str(source / PRODUCT),
        ],
        env=env,
        cwd=source,
        check=True,
    )
    python = work / "venv/bin/python"
    ids = [f"{CASES}[{mode}]" for mode in ("serial", "parallel")]
    pytest(source, temporary, evidence, python, env, "before", ids, 1)
    assert (source / ".pytest_cache/v/cache/nodeids").is_file()
    rejects(source, tree)
    cache = work / "nested-pytest-cache"
    (source / ".pytest_cache").rename(cache)
    (cache / "v/cache/nodeids").unlink()
    path = source / ".pytest_cache"
    target = os.path.relpath(cache, source)
    path.symlink_to(target, target_is_directory=True)
    verify_archive(source, tree, target)
    pytest(source, temporary, evidence, python, env, "after", ids, 1)
    assert (cache / "v/cache/nodeids").is_file()
    verify_archive(source, tree, target)
    extra = source / "unexpected.txt"
    extra.write_text("unexpected")
    rejects(source, tree, target)
    extra.unlink()
    tracked = source / "README.md"
    original = tracked.read_bytes()
    tracked.write_bytes(original + b"\nqualification negative control\n")
    rejects(source, tree, target)
    tracked.write_bytes(original)
    path.unlink()
    path.symlink_to("..", target_is_directory=True)
    rejects(source, tree, target)
    path.unlink()
    path.symlink_to(target, target_is_directory=True)
    verify_archive(source, tree, target)
    print(
        "Both source-bound nested test variants passed. Cache escaped source, and verifier rejected extra file, changed tracked bytes and changed sealed link."
    )
