from __future__ import annotations

from pathlib import Path
from typing import Any


def decode_axml(path: str | Path) -> dict[str, Any]:
    """Best-effort decode of Android XML or binary XML resources."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = file_path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return {"path": str(file_path), "decoded": False, "note": "Binary XML is not decoded in this scaffold."}

    if "<" in text[:400]:
        return {"path": str(file_path), "decoded": True, "content": text[:4000]}
    return {"path": str(file_path), "decoded": False, "note": "No XML payload detected."}


__all__ = ["decode_axml"]
