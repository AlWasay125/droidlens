from __future__ import annotations

from pathlib import Path
from typing import Any

from droidlens.formats.apk import inspect_apk


def manifest_summary(apk_path: str | Path) -> dict[str, Any]:
    """Return a normalized summary of the app manifest and permission set."""

    info = inspect_apk(apk_path)
    return {
        "path": info["path"],
        "package": info["package"],
        "version_name": info["version_name"],
        "version_code": info["version_code"],
        "min_sdk": info["min_sdk"],
        "target_sdk": info["target_sdk"],
        "compile_sdk": info["compile_sdk"],
        "permissions": info["permissions"],
        "dex_count": info["dex_count"],
        "so_count": info["so_count"],
        "asset_count": info["asset_count"],
        "signature_status": info["signature_status"],
    }


__all__ = ["manifest_summary"]
