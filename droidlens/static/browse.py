from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any


def list_files(
    target_path: str | Path,
    *,
    so: bool = False,
    assets: bool = False,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    path = Path(target_path)

    if path.is_dir():
        files = [str(item.relative_to(path)) for item in sorted(path.rglob("*")) if item.is_file()]
        if so:
            files = [name for name in files if name.endswith(".so")]
        if assets:
            files = [name for name in files if "assets" in name.lower()]
        return {
            "path": str(path),
            "files": files[offset : offset + limit],
            "count": len(files),
        }

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            files = zf.namelist()
        if so:
            files = [name for name in files if name.endswith(".so")]
        if assets:
            files = [name for name in files if name.startswith("assets/")]
        return {
            "path": str(path),
            "files": files[offset : offset + limit],
            "count": len(files),
        }

    return {"path": str(path), "files": [], "count": 0}


__all__ = ["list_files"]
