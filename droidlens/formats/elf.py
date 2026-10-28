from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any


def read_elf_info(path: str | Path) -> dict[str, Any]:
    """Best-effort ELF triage: section names, symbol names, imported libraries."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"ELF file not found: {file_path}")

    raw = file_path.read_bytes()
    if not raw.startswith(b"\x7fELF"):
        return {"path": str(file_path), "kind": "not-elf", "sections": [], "imports": [], "symbols": []}

    # Very lightweight parser: grab common ELF section names and imported libs from strings.
    strings = re.findall(rb"[A-Za-z0-9_./+-]{3,}", raw[:65536])
    section_names = [s.decode("utf-8", errors="replace") for s in strings if b"." in s or b"_" in s][:100]
    imports = sorted({s.decode("utf-8", errors="replace") for s in strings if b"lib" in s.lower() or b"android" in s.lower()})
    symbols = sorted({s.decode("utf-8", errors="replace") for s in strings if re.fullmatch(rb"[A-Za-z0-9_]+", s) and len(s) >= 6})[:200]

    return {
        "path": str(file_path),
        "kind": "elf",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size": len(raw),
        "sections": section_names,
        "imports": imports,
        "symbols": symbols,
    }


__all__ = ["read_elf_info"]
