from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path
from typing import Any


def apk_diff(left: str | Path, right: str | Path) -> dict[str, Any]:
    """Compare two APKs or archives by file list and sha256 digest. This is intentionally lightweight."""

    left_path = Path(left)
    right_path = Path(right)

    def archive_entries(path: Path) -> dict[str, str]:
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {path}")
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as zf:
                return {name: hashlib.sha256(zf.read(name)).hexdigest() for name in zf.namelist()}
        return {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}

    left_entries = archive_entries(left_path)
    right_entries = archive_entries(right_path)

    added = sorted(set(right_entries) - set(left_entries))
    removed = sorted(set(left_entries) - set(right_entries))
    changed = sorted(
        name for name in set(left_entries) & set(right_entries) if left_entries[name] != right_entries[name]
    )

    return {
        "left": str(left_path),
        "right": str(right_path),
        "added": added,
        "removed": removed,
        "changed": changed,
        "left_sha256": hashlib.sha256(left_path.read_bytes()).hexdigest() if left_path.is_file() else None,
        "right_sha256": hashlib.sha256(right_path.read_bytes()).hexdigest() if right_path.is_file() else None,
    }


__all__ = ["apk_diff"]
