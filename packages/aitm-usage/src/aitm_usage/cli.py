import argparse
from importlib.metadata import version
from pathlib import Path
from uuid import UUID


def default_project_root(project_id: UUID) -> Path:
    return (
        Path.home() / "Library" / "Application Support" / "aitm-usage" / str(project_id)
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="aitm-usage", description="Private local AITM usage"
    )
    parser.add_argument("--project", type=Path, metavar="STATE_DIR")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('aitm-usage')}"
    )
    parser.parse_args()
    parser.print_help()
    return 0
