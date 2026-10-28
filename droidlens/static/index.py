from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def index_strings(target_path: str | Path, *, min_len: int = 4) -> list[str]:
    """Index printable strings from a file or APK archive."""

    path = Path(target_path)
    if not path.exists():
        return []

    if path.is_dir():
        text: list[str] = []
        for file in sorted(path.rglob("*")):
            if file.is_file() and file.suffix.lower() in {".smali", ".java", ".xml", ".txt", ".log"}:
                try:
                    text.extend(re.findall(rb"[\x20-\x7E]{%d,}" % max(min_len, 4), file.read_bytes()))
                except Exception:
                    continue
        return sorted({m.decode("utf-8", errors="replace") for m in text if len(m) >= min_len})

    data = path.read_bytes()
    matches = re.findall(rb"[\x20-\x7E]{%d,}" % max(min_len, 4), data)
    values = {m.decode("utf-8", errors="replace") for m in matches}
    return sorted(v for v in values if len(v) >= min_len)


def match_refs(target_path: str | Path, needle: str) -> list[str]:
    """Search indexed strings for a given token or literal."""

    strings = index_strings(target_path)
    return [value for value in strings if needle.lower() in value.lower()]


def find_secrets(target_path: str | Path) -> list[dict[str, Any]]:
    """Best-effort secret and high-entropy candidate detection."""

    results: list[dict[str, Any]] = []
    for value in index_strings(target_path):
        if any(token in value.lower() for token in ["api_key", "secret", "token", "password", "private_key", "bearer", "authorization"]):
            results.append({"type": "keyword", "value": value})
        if len(value) >= 20 and sum(1 for ch in value if ch.isalnum()) / max(len(value), 1) > 0.7:
            results.append({"type": "entropy-like", "value": value})
    return results


def xref_index(target_path: str | Path) -> dict[str, list[str]]:
    """Create a minimal reverse lookup from strings to references."""

    strings = index_strings(target_path)
    index: dict[str, list[str]] = {}
    for value in strings:
        index[value] = [str(target_path)]
    return index


def vuln_checks(target_path: str | Path) -> list[dict[str, Any]]:
    """Check for common Android static issues from strings and metadata."""

    findings: list[dict[str, Any]] = []
    strings = index_strings(target_path)
    lower = {s.lower() for s in strings}
    if "android.permission.internet" in lower:
        findings.append({"id": "MSTG-PLATFORM-1", "title": "Internet permission present", "severity": "info", "evidence": "android.permission.INTERNET"})
    if any("http://" in s.lower() or "https://" in s.lower() for s in strings):
        findings.append({"id": "MSTG-PLATFORM-3", "title": "Network endpoints referenced", "severity": "info", "evidence": "HTTP(S) endpoint present"})
    if "allowbackup" in " ".join(strings).lower():
        findings.append({"id": "MSTG-PLATFORM-6", "title": "Backup configuration referenced", "severity": "low", "evidence": "allowBackup is present"})
    return findings


__all__ = ["index_strings", "match_refs", "find_secrets", "xref_index", "vuln_checks"]
