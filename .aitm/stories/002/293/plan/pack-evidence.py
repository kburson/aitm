"""Preserve the original and corrected provider artifacts beyond Actions expiry."""

import json
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from summarize import ORDER

CURRENT = Path(__file__).resolve().parent
ORIGINAL = CURRENT.parent / "delivery-293"


def pack_lane(archive, root, descriptor, case):
    for attempt in sorted(case.glob("attempt-*")):
        provider = json.loads((attempt / "provider.json").read_bytes())
        for lane in ("fast", "full"):
            receipt = provider["jobs"][lane]["artifact"]
            raw = attempt / f"{lane}.zip"
            assert raw.stat().st_size == receipt["size_in_bytes"]
            assert f"sha256:{sha256(raw.read_bytes()).hexdigest()}" == receipt["digest"]
            with ZipFile(raw) as observed:
                assert observed.testzip() is None
        for file in sorted(attempt.iterdir()):
            assert file.is_file()
            mode = ZIP_STORED if file.suffix == ".zip" else ZIP_DEFLATED
            archive.write(
                file, f"{descriptor}/{file.relative_to(root)}", compress_type=mode
            )


with ZipFile(
    CURRENT / "benchmark-evidence.zip", "w", compression=ZIP_DEFLATED
) as archive:
    for descriptor, root in (("original", ORIGINAL), ("corrected", CURRENT)):
        for name in (
            "lab-default-commit",
            "lab-repository.json",
            "lab-rules.json",
            "read-hosted.py",
        ):
            archive.write(root / name, f"{descriptor}/{name}")
        for name in ORDER:
            case = root / "runs" / name
            assert any(case.glob("attempt-*"))
            pack_lane(archive, root, descriptor, case)
            archive.write(case / "pr.txt", f"{descriptor}/runs/{name}/pr.txt")
            verified = case / "verified.json"
            if verified.is_file():
                archive.write(verified, f"{descriptor}/runs/{name}/verified.json")
            else:
                assert descriptor == "original"
        for name in (
            "cases.json",
            "workload.json",
            ".github/workflows/qualification.yml",
            "experiment.py",
        ):
            archive.write(root / "lab" / name, f"{descriptor}/lab/{name}")
    for name in (
        "check-cache.py",
        "check-cache.log",
        "summarize.py",
        "pack-evidence.py",
    ):
        archive.write(CURRENT / name, f"corrected/{name}")

with ZipFile(CURRENT / "benchmark-evidence.zip") as archive:
    assert archive.testzip() is None
    print(
        len(archive.namelist()),
        sha256((CURRENT / "benchmark-evidence.zip").read_bytes()).hexdigest(),
    )
