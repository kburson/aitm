"""Check maintained files in the Git index and report TypeScript applicability."""

import argparse
import codecs
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from aitm_usage.pricing import RateCard
from aitm_usage.qualification import decode_activation_receipt
from python_gate import _policy_error
from verify_pr import decode_json

FILE_TOOLS = Path("tools/ci/file-lint")
TOOL_MANIFEST = FILE_TOOLS / "package.json"
CI_POLICY = Path("tools/ci/policy.json")
RATE_DIR = Path("packages/aitm-usage/src/aitm_usage/rates")
ACTIVATION_FIXTURE = Path("packages/aitm-usage/tests/fixtures/activation/receipt.json")
MARKDOWN_SUFFIXES = {".md", ".markdown"}
YAML_SUFFIXES = {".yml", ".yaml"}
TYPESCRIPT_SUFFIXES = {".ts", ".tsx", ".mts", ".cts"}
DEPENDENCY_FIELDS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
)


def tracked_files(root):
    location = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree", "--show-prefix"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    )
    if location.stdout != b"true\n\n":
        raise ValueError("--root must be the Git repository root")
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [Path(os.fsdecode(name)) for name in result.stdout.split(b"\0") if name]


def read_json(root, path):
    raw = (root / path).read_bytes()
    # Decode explicitly so the evidence parser cannot auto-detect UTF-16 or UTF-32.
    try:
        document = decode_json(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    schema = document.get("schema") if isinstance(document, dict) else None
    if path == CI_POLICY or schema == "aitm.ci-policy/v1":
        if problem := _policy_error(document):
            raise ValueError(problem)
    if path.parent == RATE_DIR:
        try:
            rate = RateCard.from_json(raw)
        except ValueError as exc:
            raise ValueError(f"invalid rate card: {exc}") from exc
        if rate.version != path.stem:
            raise ValueError("rate card version does not match its filename")
    if path == ACTIVATION_FIXTURE or schema == "aitm-usage-activation/v1":
        try:
            decode_activation_receipt(raw)
        except ValueError as exc:
            raise ValueError(f"invalid activation receipt: {exc}") from exc
    return document


def typescript_manifest(path, document):
    if (
        path == TOOL_MANIFEST
        or path.name != "package.json"
        or not isinstance(document, dict)
    ):
        return False
    if "types" in document or "typings" in document:
        return True
    for field in ("main", "module"):
        entry = document.get(field)
        if isinstance(entry, str) and Path(entry).suffix.lower() in TYPESCRIPT_SUFFIXES:
            return True
    scripts = document.get("scripts")
    typecheck = scripts.get("typecheck") if isinstance(scripts, dict) else None
    if isinstance(typecheck, str) and typecheck.split(maxsplit=1)[:1] == ["tsc"]:
        return True
    for field in DEPENDENCY_FIELDS:
        dependencies = document.get(field)
        if isinstance(dependencies, dict) and "typescript" in dependencies:
            return True
    return False


def lint(root, tool, command, files):
    if not files:
        return []
    try:
        subprocess.run(
            [*command, *files],
            cwd=root,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        return [f"{tool} exited {exc.returncode}"]
    except OSError as exc:
        return [f"could not run {tool}: {exc}"]
    return []


def lint_markdown(root, executable, files):
    if not files:
        return []
    try:
        # The CLI discovers local and nested configs even with --config.
        with TemporaryDirectory(prefix="aitm-markdown-") as directory:
            workspace = Path(directory)
            for path in files:
                copied = workspace / path
                copied.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / path, copied)
            return lint(
                workspace,
                "markdownlint",
                [
                    executable,
                    "--no-globs",
                    "--config",
                    root / FILE_TOOLS / ".markdownlint-cli2.yaml",
                ],
                [f":{path}" for path in files],
            )
    except OSError as exc:
        return [f"could not prepare tracked Markdown: {exc}"]


def yaml_lint_disabled(path):
    raw = path.read_bytes()
    # Match yamllint's YAML encodings, including wide ASCII headers without a BOM.
    if raw.startswith((codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE)):
        encoding = "utf-32"
    elif len(raw) >= 4 and raw.startswith(b"\x00\x00\x00"):
        encoding = "utf-32-be"
    elif raw[1:4] == b"\x00\x00\x00":
        encoding = "utf-32-le"
    elif raw.startswith((codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE)):
        encoding = "utf-16"
    elif len(raw) >= 2 and raw.startswith(b"\x00"):
        encoding = "utf-16-be"
    elif raw[1:2] == b"\x00":
        encoding = "utf-16-le"
    else:
        encoding = "utf-8-sig"
    first_line = raw.decode(encoding).partition("\n")[0]
    return re.fullmatch(r"#\s*yamllint disable-file\s*", first_line) is not None


def check_files(root, markdownlint, yamllint):
    try:
        tracked = tracked_files(root)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        return [f"could not inventory tracked files: {exc}"]

    failures = []
    markdown = []
    yaml = []
    typescript = []
    for path in tracked:
        suffix = path.suffix.lower()
        if suffix in TYPESCRIPT_SUFFIXES or (
            suffix == ".json" and path.name.startswith(("tsconfig.", "tsconfig-"))
        ):
            typescript.append(path)

        if suffix not in MARKDOWN_SUFFIXES | YAML_SUFFIXES | {".json"}:
            continue
        full_path = root / path
        if full_path.is_symlink() or not full_path.is_file():
            failures.append(f"{path}: expected a regular tracked file")
            continue
        try:
            if suffix in MARKDOWN_SUFFIXES:
                markdown.append(path)
            elif suffix in YAML_SUFFIXES:
                if yaml_lint_disabled(full_path):
                    raise ValueError("yamllint disable-file would skip this file")
                yaml.append(f"./{path}")
            elif typescript_manifest(path, read_json(root, path)):
                typescript.append(path)
        except (OSError, ValueError, RecursionError) as exc:
            failures.append(f"{path}: {exc}")

    if typescript:
        candidates = ", ".join(str(path) for path in typescript)
        failures.append(f"TypeScript: detected {candidates}; required lane is inactive")
    else:
        print("TypeScript: not applicable (no tracked product TypeScript detected)")

    failures.extend(lint_markdown(root, markdownlint, markdown))
    failures.extend(
        lint(
            root,
            "yamllint",
            [yamllint, "--strict", "--config-file", FILE_TOOLS / "yamllint.yaml"],
            yaml,
        )
    )
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--markdownlint", type=Path, required=True)
    parser.add_argument("--yamllint", type=Path, required=True)
    args = parser.parse_args(argv)
    failures = check_files(
        args.root.resolve(), args.markdownlint.resolve(), args.yamllint.resolve()
    )
    for failure in failures:
        print(f"File checks: {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
