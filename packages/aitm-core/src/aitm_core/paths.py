"""Canonical display paths for unnumbered planning entities."""

import re
from collections.abc import Collection
from datetime import UTC, datetime
from itertools import count
from unicodedata import normalize


def intake_slug(title: str) -> str:
    ascii_title = normalize("NFKD", title).encode("ascii", "ignore").decode()
    return (
        re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")[:40].rstrip("-")
        or "untitled"
    )


def intake_location(stamp: datetime, slug: str) -> tuple[str, str]:
    if stamp.utcoffset() is None:
        raise ValueError("intake requires a timezone-aware timestamp")
    utc = stamp.astimezone(UTC)
    return utc.strftime("%Y-%m"), f"{utc:%Y%m%d-%H%M}-{intake_slug(slug)}"


def vacant_path(root: str, stem: str, extension: str, occupied: Collection[str]) -> str:
    for number in count(1):
        suffix = "" if number == 1 else f"-{number}"
        path = f"{root}/{stem}{suffix}{extension}"
        if path not in occupied and not any(
            existing.startswith(path + "/") for existing in occupied
        ):
            return path
    raise AssertionError("unreachable")
