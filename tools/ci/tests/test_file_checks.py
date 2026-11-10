import shlex
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parents[1]
SOURCE_ROOT = CI_DIR.parents[1]
RATE_DIR = "packages/aitm-usage/src/aitm_usage/rates"
RECEIPT = "packages/aitm-usage/tests/fixtures/activation/receipt.json"
TOOL_MANIFEST = "tools/ci/file-lint/package.json"


class Checkout:
    def __init__(self, directory):
        self.root = directory / "checkout"
        self.root.mkdir()
        self.git("init", "-q")
        self.tools = directory / "test tools"
        self.tools.mkdir()
        self.executable("markdownlint")
        self.executable("yamllint")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True)

    def write(self, name, data, *, tracked=True):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
        if tracked:
            self.git("add", "--", f":(literal){name}")
        return path

    def executable(self, tool, exit_code=0):
        path = self.tools / tool
        path.write_text(
            "#!/bin/sh\n"
            f'printf "%s\\n" "$@" > {shlex.quote(str(self.tools / (tool + ".argv")))}\n'
            f"find . -type f | LC_ALL=C sort > {shlex.quote(str(self.tools / (tool + '.files')))}\n"
            f'echo "ran {tool}"\n'
            f"exit {exit_code}\n",
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def check(self, root=None):
        return subprocess.run(
            [
                sys.executable,
                str(CI_DIR / "file_checks.py"),
                "--root",
                str(root or self.root),
                "--markdownlint",
                str(self.tools / "markdownlint"),
                "--yamllint",
                str(self.tools / "yamllint"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )


@pytest.fixture
def checkout(tmp_path):
    return Checkout(tmp_path)


def test_checks_only_tracked_files_and_reports_typescript_not_applicable(checkout):
    checkout.write("product.json", '{"value": 1}')
    checkout.write(
        "tools/ci/tests/fixtures/verify-pr/records.jsonl",
        '{"record": 1}\n{"record": 2}\n',
    )
    checkout.write("untracked.json", "{", tracked=False)
    checkout.write("untracked.ts", "", tracked=False)
    checkout.write("untracked.md", "bad", tracked=False)
    checkout.write(".gitignore", "generated/\n")
    checkout.write("generated/ignored.yaml", "broken: [", tracked=False)
    checkout.write("docs/reference [v1].MD", "# Reference\n")
    checkout.write("docs/reference v.md", "# Untracked glob neighbor\n", tracked=False)
    checkout.write("docs/reference.markdown", "# Another reference\n")
    checkout.write(
        ".markdownlint-cli2.yaml", "config: {default: false}\n", tracked=False
    )
    checkout.write("docs/.markdownlint.yaml", "default: false\n")
    checkout.write(".github/workflows/ci.yml", "name: CI\n")
    checkout.write("-settings.yaml", "setting: true\n")
    checkout.write(TOOL_MANIFEST, '{"devDependencies": {"typescript": "5"}}')
    checkout.write("package.json", '{"scripts": {"test": "node --test"}}')

    result = checkout.check()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "typescript: not applicable" in result.stdout.lower()
    assert (checkout.tools / "markdownlint.argv").read_text().splitlines() == [
        "--no-globs",
        "--config",
        str(checkout.root / "tools/ci/file-lint/.markdownlint-cli2.yaml"),
        ":docs/reference [v1].MD",
        ":docs/reference.markdown",
    ]
    assert (checkout.tools / "markdownlint.files").read_text().splitlines() == [
        "./docs/reference [v1].MD",
        "./docs/reference.markdown",
    ]
    assert (checkout.tools / "yamllint.argv").read_text().splitlines() == [
        "--strict",
        "--config-file",
        "tools/ci/file-lint/yamllint.yaml",
        "./-settings.yaml",
        "./.github/workflows/ci.yml",
        "./docs/.markdownlint.yaml",
    ]


@pytest.mark.parametrize(
    ("data", "reason"),
    [
        (b'{"nested": {"a": 1, "a": 2}}', "duplicate"),
        (b'{"a": [NaN]}', "nonfinite"),
        (b'{"a": Infinity}', "nonfinite"),
        (b'{"a": -Infinity}', "nonfinite"),
        (b'{"a": "\xff"}', "utf-8"),
        ('{"a": 1}'.encode("utf-16"), "utf-8"),
        (b'{"a": 1,}', "invalid json"),
    ],
)
def test_refuses_new_malformed_tracked_json_even_in_fixture_directory(
    checkout, data, reason
):
    path = "tools/ci/tests/fixtures/verify-pr/new.json"
    checkout.write(path, data)

    result = checkout.check()

    assert result.returncode == 1
    assert path in result.stderr
    assert reason in result.stderr.lower()


def test_tooling_manifest_still_requires_strict_json(checkout):
    checkout.write(TOOL_MANIFEST, "{")

    result = checkout.check()

    assert result.returncode == 1
    assert TOOL_MANIFEST in result.stderr


@pytest.mark.parametrize(
    ("name", "value", "reason"),
    [
        ("tools/ci/policy.json", "{}", "policy"),
        ("data/copied-policy.json", '{"schema": "aitm.ci-policy/v1"}', "policy"),
        (f"{RATE_DIR}/2026-11-09.json", "{}", "rate card"),
        (RECEIPT, "{}", "activation receipt"),
        (
            "data/copied-receipt.json",
            '{"schema": "aitm-usage-activation/v1"}',
            "activation receipt",
        ),
    ],
)
def test_refuses_json_that_disagrees_with_its_schema(checkout, name, value, reason):
    checkout.write(name, value)

    result = checkout.check()

    assert result.returncode == 1
    assert name in result.stderr
    assert reason in result.stderr.lower()


def test_accepts_current_schema_documents(checkout):
    for name in ("tools/ci/policy.json", f"{RATE_DIR}/2026-11-09.json", RECEIPT):
        checkout.write(name, (SOURCE_ROOT / name).read_bytes())

    result = checkout.check()

    assert result.returncode == 0, result.stdout + result.stderr


def test_refuses_rate_card_version_that_disagrees_with_its_filename(checkout):
    old = SOURCE_ROOT / RATE_DIR / "2026-11-09.json"
    path = f"{RATE_DIR}/2026-11-10.json"
    checkout.write(path, old.read_bytes())

    result = checkout.check()

    assert result.returncode == 1
    assert path in result.stderr
    assert "version" in result.stderr


@pytest.mark.parametrize(
    ("name", "contents"),
    [
        ("packages/web/src/index.ts", "export const answer = 42;"),
        ("packages/web/src/index.tsx", "export const answer = 42;"),
        ("packages/web/src/index.mts", "export const answer = 42;"),
        ("packages/web/src/index.cts", "export const answer = 42;"),
        ("packages/web/tsconfig.json", "{}"),
        ("packages/web/tsconfig.build.json", "{}"),
        ("packages/web/package.json", '{"devDependencies": {"typescript": "5"}}'),
        ("packages/web/package.json", '{"typings": "dist/index.d.ts"}'),
        ("packages/web/package.json", '{"main": "./src/index.ts"}'),
        ("packages/web/package.json", '{"module": "./src/index.tsx"}'),
        ("packages/web/package.json", '{"scripts": {"typecheck": "tsc --noEmit"}}'),
        (
            "tools/ci/file-lint/unrelated/package.json",
            '{"peerDependencies": {"typescript": "*"}}',
        ),
    ],
)
def test_holds_for_product_typescript_without_a_required_lane(checkout, name, contents):
    checkout.write(name, contents)

    result = checkout.check()

    assert result.returncode == 1
    assert "typescript: detected" in result.stderr.lower()
    assert "lane" in result.stderr.lower()
    assert name in result.stderr
    assert "typescript: not applicable" not in result.stdout.lower()


def test_reports_typescript_detection_even_when_config_json_is_invalid(checkout):
    path = "packages/web/tsconfig.json"
    checkout.write(path, "{")

    result = checkout.check()

    assert result.returncode == 1
    assert "typescript: detected" in result.stderr.lower()
    assert "invalid json" in result.stderr.lower()
    assert path in result.stderr


@pytest.mark.parametrize(
    ("tool", "path"),
    [("markdownlint", "doc.md"), ("yamllint", ".github/workflows/broken.yaml")],
)
def test_refuses_nonzero_linter_result_and_surfaces_diagnostics(checkout, tool, path):
    checkout.write(path, "data")
    checkout.executable(tool, 17)

    result = checkout.check()

    assert result.returncode == 1
    assert f"ran {tool}" in result.stdout
    assert tool in result.stderr
    assert "17" in result.stderr


def test_missing_linter_fails_when_files_are_applicable(checkout):
    checkout.write("docs/reference.md", "# Reference")
    (checkout.tools / "markdownlint").unlink()

    result = checkout.check()

    assert result.returncode == 1
    assert "markdownlint" in result.stderr
    assert "file" in result.stderr.lower()


def test_missing_tracked_file_cannot_be_silently_skipped(checkout):
    checkout.write("docs/reference.md", "# Reference").unlink()

    result = checkout.check()

    assert result.returncode == 1
    assert "docs/reference.md" in result.stderr


def test_non_git_root_fails_closed(checkout):
    (checkout.root / ".git").rename(checkout.root / ".not-git")

    result = checkout.check()

    assert result.returncode == 1
    assert "tracked" in result.stderr.lower()


def test_git_subdirectory_cannot_narrow_tracked_scope(checkout):
    checkout.write("bad.json", "{")
    subdirectory = checkout.write("nested/good.json", "{}").parent

    result = checkout.check(root=subdirectory)

    assert result.returncode == 1
    assert "repository root" in result.stderr.lower()


@pytest.mark.parametrize(
    "encoding",
    [
        "utf-8",
        "utf-8-sig",
        "utf-16",
        "utf-32",
        "utf-16-le",
        "utf-16-be",
        "utf-32-le",
        "utf-32-be",
    ],
)
def test_yaml_file_wide_disable_cannot_skip_invalid_yaml(checkout, encoding):
    path = ".github/workflows/broken.yaml"
    checkout.write(path, "#  yamllint disable-file\r\nbroken: [\n".encode(encoding))

    result = checkout.check()

    assert result.returncode == 1
    assert path in result.stderr
    assert "disable-file" in result.stderr


def test_yaml_directive_shaped_block_content_is_left_to_yamllint(checkout):
    checkout.write(
        "example.yaml",
        "message: |\n  # yamllint disable-file\n  # yamllint disable-line\n",
    )

    result = checkout.check()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ran yamllint" in result.stdout
