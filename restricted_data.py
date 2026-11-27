"""Restricted data: the files that produce the results but cannot be published.

Every phase keeps them in its own folder `restricted-data/` (never committed; see .gitignore):
original survey exports, pseudonym maps, team spreadsheets with item texts of copyrighted
questionnaires or free-text answers, and similar records. They are the primary records of the
project: without them the anonymised files in `data/raw/` cannot be rebuilt.

What *is* committed is `restricted-data/MANIFEST.csv`, one row per file:

    file         path inside restricted-data/ (forward slashes)
    description  what the file is
    origin       where it comes from (LimeSurvey survey ID, Google Drive file ID, ...)
    obtained     date the file was exported or downloaded (YYYY-MM-DD)
    used_by      scripts that read it
    bytes        size of the file
    sha256       SHA-256 checksum of the file

The scripts call `require()` for each file they read: it stops with a clear message when the file
is missing and warns when its checksum differs from the manifest (the results may then differ from
the published ones).

Command line, from the repository root:

    python restricted_data.py verify                     # check every phase
    python restricted_data.py verify phase1-item-development
    python restricted_data.py update phase1-item-development   # refresh bytes and sha256 after
                                                              # deliberately replacing a file
"""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

FOLDER = "restricted-data"
MANIFEST = "MANIFEST.csv"
COLUMNS = ["file", "description", "origin", "obtained", "used_by", "bytes", "sha256"]
ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def folder(phase_dir: Path) -> Path:
    return Path(phase_dir) / FOLDER


def read_manifest(phase_dir: Path) -> list[dict]:
    path = folder(phase_dir) / MANIFEST
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_manifest(phase_dir: Path, rows: list[dict]) -> None:
    path = folder(phase_dir) / MANIFEST
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in sorted(rows, key=lambda r: r["file"]):
            w.writerow({c: r.get(c, "") for c in COLUMNS})


def require(phase_dir: Path, rel: str) -> Path:
    """Path of a restricted file; exits if it is missing, warns if its checksum changed."""
    path = folder(phase_dir) / rel
    if not path.exists():
        sys.exit(f"Missing restricted file: {path}\n"
                 f"See {folder(phase_dir) / 'README.md'} for where to obtain it.")
    entry = next((r for r in read_manifest(phase_dir) if r["file"] == rel), None)
    if entry is None:
        print(f"WARNING: {rel} is not listed in {FOLDER}/{MANIFEST}.")
    elif entry.get("sha256") and sha256(path) != entry["sha256"]:
        print(f"WARNING: {rel} differs from the version recorded in {FOLDER}/{MANIFEST} "
              f"(checksum changed); results may differ from the published ones.")
    return path


def verify(phase_dir: Path) -> bool:
    rows = read_manifest(phase_dir)
    if not rows:
        print(f"{phase_dir.name}: no {FOLDER}/{MANIFEST}")
        return True
    ok = True
    for r in rows:
        path = folder(phase_dir) / r["file"]
        if not path.exists():
            status, ok = "MISSING", False
        elif not r.get("sha256"):
            status = "present (no checksum recorded)"
        elif sha256(path) == r["sha256"]:
            status = "ok"
        else:
            status, ok = "CHANGED", False
        print(f"{phase_dir.name}: {status:8} {r['file']}")
    extra = {p.relative_to(folder(phase_dir)).as_posix() for p in folder(phase_dir).rglob("*")
             if p.is_file() and p.name not in (MANIFEST, "README.md")} - {r["file"] for r in rows}
    for e in sorted(extra):
        print(f"{phase_dir.name}: NOT IN MANIFEST {e}")
    return ok


def update(phase_dir: Path) -> None:
    rows = read_manifest(phase_dir)
    for r in rows:
        path = folder(phase_dir) / r["file"]
        if path.exists():
            r["bytes"], r["sha256"] = str(path.stat().st_size), sha256(path)
    write_manifest(phase_dir, rows)
    print(f"Updated {folder(phase_dir) / MANIFEST}")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("verify", "update"):
        sys.exit(__doc__)
    phases = [ROOT / p for p in sys.argv[2:]] or sorted(p for p in ROOT.iterdir() if (p / FOLDER).is_dir())
    if sys.argv[1] == "update":
        for p in phases:
            update(p)
        return
    ok = all([verify(p) for p in phases])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
