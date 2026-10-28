from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def decode_arsc(path: str | Path) -> dict[str, Any]:
    """Best-effort resources.arsc decode, returning a compact list of names."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    raw = file_path.read_bytes()
    entries = []
    for match in re.findall(rb"(?:[A-Za-z0-9_./-]+)\\x00", raw[:4096]):
        text = match.decode("utf-8", errors="replace").rstrip("\x00")
        if text:
            entries.append(text)
    return {"path": str(file_path), "decoded": True, "entries": entries[:200]}


__all__ = ["decode_arsc"]
