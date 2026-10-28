from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def index_strings(target_path: str | Path, *, min_len: int = 4) -> list[str]:
    """Index printable strings from a file or APK-like target."""

    path = Path(target_path)
    if not path.exists():
        return []

    data = path.read_bytes() if path.is_file() else b""
    matches = re.findall(rb"[\x20-\x7E]{%d,}" % max(min_len, 4), data)
    values = {m.decode("utf-8", errors="replace") for m in matches}
    return sorted(v for v in values if len(v) >= min_len)


def match_refs(target_path: str | Path, needle: str) -> list[str]:
    return [value for value in index_strings(target_path) if needle.lower() in value.lower()]


def find_secrets(target_path: str | Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for value in index_strings(target_path):
        lowered = value.lower()
        if any(token in lowered for token in ["key", "secret", "token", "password", "authorization", "bearer"]):
            findings.append({"type": "keyword", "value": value})
    return findings


def xref_index(target_path: str | Path) -> dict[str, list[str]]:
    strings = index_strings(target_path)
    return {value: [str(target_path)] for value in strings}


def vuln_checks(target_path: str | Path) -> list[dict[str, Any]]:
    strings = index_strings(target_path)
    lower = " ".join(strings).lower()
    findings: list[dict[str, Any]] = []
    if "android.permission.internet" in lower:
        findings.append({"id": "MSTG-PLATFORM-1", "title": "Internet permission present", "severity": "info", "evidence": "android.permission.INTERNET"})
    if "http://" in lower or "https://" in lower:
        findings.append({"id": "MSTG-PLATFORM-3", "title": "Network endpoints referenced", "severity": "info", "evidence": "HTTP(S) endpoint present"})
    if "allowbackup" in lower:
        findings.append({"id": "MSTG-PLATFORM-6", "title": "Backup configuration referenced", "severity": "low", "evidence": "allowBackup is present"})
    return findings


__all__ = ["index_strings", "match_refs", "find_secrets", "xref_index", "vuln_checks"]
