"""Hash the measurement files retained in private scratch and the publication set."""

import hashlib
import sys
from pathlib import Path

PUBLICATION = (
    "2026-11-13-267-measurement-plan.md",
    "benchmark-notes.md",
    "evidence.json",
    "manifest.py",
    "measure_diagnostics.py",
    "measure_testmon.py",
    "prepare.sh",
    "raw-manifest.sha256",
    "recipe.md",
    "recheck-baseline.sh",
    "report.md",
    "report.py",
    "run-matrix.sh",
    "run-profile.sh",
    "seed.py",
    "summarize.py",
)
RETAINED_NAMES = {
    "ancestor-ctimes.jsonl",
    "diagnostics.jsonl",
    "exit",
    "exit-source",
    "matrix.log",
    "pytest-evidence.json",
    "report.json",
    "seed.patch",
    "stderr.log",
    "stdout.log",
    "testmon-evidence.json",
    "testmon.sqlite",
}


def write_manifest(root, items, destination):
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root).as_posix()}\n"
        for path in sorted(items)
    ]
    destination.write_text("".join(lines))


def main():
    private, output = (Path(value).resolve() for value in sys.argv[1:])
    items = []
    for folder in ("logs", "observer", "history"):
        for path in (private / folder).rglob("*"):
            relative = path.relative_to(private)
            if "fixtures" in relative.parts or "__pycache__" in relative.parts:
                continue
            if path.is_file() and (
                path.name in RETAINED_NAMES or path.suffix in {".status", ".sqlite"}
            ):
                items.append(path)
    write_manifest(private, items, output / "raw-manifest.sha256")
    write_manifest(
        output, (output / name for name in PUBLICATION), output / "publication.sha256"
    )


if __name__ == "__main__":
    main()
