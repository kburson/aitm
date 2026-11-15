"""Archive the measurements without copying the whole writable test volume."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile

work, destination = map(Path, sys.argv[1:3])
paths = [work / "ancestor-events.jsonl"]
for width in (1, 3):
    for cache in ("cold", "warm"):
        run = work / f"workers-{width}-{cache}"
        paths.extend(run / filename for filename in ("summary.json", "setup.log"))
        for cohort in ("full", "projected"):
            cell = run / cohort
            paths.extend(cell / filename for filename in (
                "coverage.json", "evidence.json", "test.log", "coverage-combine.log", ".coverage",
            ))
            paths.extend(sorted(cell.glob("pytest*.json")))
    control = work / f"child-control-{width}"
    evidence = json.loads((control / "evidence.json").read_bytes())
    paths.extend(control / filename for filename in ("evidence.json", "coverage.json", "test.log"))
    paths.extend(sorted(control.glob("pytest*.json")))
    for child in evidence["children"]:
        native = sorted(control.glob(f".coverage.*.pid{child['pid']}.*"))
        assert native
        paths.extend(native)
with ZipFile(destination, "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
    for path in paths:
        archive.write(path, path.relative_to(work))
with ZipFile(destination) as archive:
    assert archive.testzip() is None
    assert len(archive.namelist()) == len(set(archive.namelist())) == len(paths)
print(sha256(destination.read_bytes()).hexdigest(), len(paths), destination)
