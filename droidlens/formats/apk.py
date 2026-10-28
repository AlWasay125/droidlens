from __future__ import annotations

from typing import Any


def inspect_apk(path: str) -> dict[str, Any]:
    return {"path": path, "certs": []}


def list_archive_files(path: str) -> list[str]:
    return []


def extract_strings_from_path(path: str, *, min_len: int = 4) -> list[str]:
    return []


def decode_axml(path: str) -> dict[str, Any]:
    return {"path": path, "decoded": False}


def decode_arsc(path: str) -> dict[str, Any]:
    return {"path": path, "decoded": False}


__all__ = [
    "inspect_apk",
    "list_archive_files",
    "extract_strings_from_path",
    "decode_axml",
    "decode_arsc",
]
