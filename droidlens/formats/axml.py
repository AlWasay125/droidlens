from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path
from typing import Any


def inspect_apk(apk_path: str | Path) -> dict[str, Any]:
    """Read a zip-based APK and return the basic manifest and metadata used by M2."""

    apk = Path(apk_path)
    if not apk.exists():
        raise FileNotFoundError(f"APK not found: {apk}")

    with zipfile.ZipFile(apk) as zf:
        names = zf.namelist()
        manifest_name = next((name for name in names if name.lower().endswith("androidmanifest.xml")), None)
        manifest_text = ""
        certs: list[dict[str, Any]] = []
        permissions: list[str] = []
        package: str | None = None
        version_name: str | None = None
        version_code: str | None = None
        min_sdk: str | None = None
        target_sdk: str | None = None
        compile_sdk: str | None = None

        if manifest_name is not None:
            manifest_bytes = zf.read(manifest_name)
            manifest_text = manifest_bytes.decode("utf-8", errors="replace")
            package = re.search(r'package="([^"]+)"', manifest_text)
            if package:
                package = package.group(1)
            version_name = re.search(r'android:versionName="([^"]+)"', manifest_text)
            if version_name:
                version_name = version_name.group(1)
            version_code = re.search(r'android:versionCode="([^"]+)"', manifest_text)
            if version_code:
                version_code = version_code.group(1)
            min_sdk = re.search(r'android:minSdkVersion="([^"]+)"', manifest_text)
            if min_sdk:
                min_sdk = min_sdk.group(1)
            target_sdk = re.search(r'android:targetSdkVersion="([^"]+)"', manifest_text)
            if target_sdk:
                target_sdk = target_sdk.group(1)
            compile_sdk = re.search(r'android:compileSdkVersion="([^"]+)"', manifest_text)
            if compile_sdk:
                compile_sdk = compile_sdk.group(1)
            permissions = re.findall(r'<uses-permission[^>]*android:name="([^"]+)"', manifest_text)

        for info in zf.infolist():
            lower = info.filename.lower()
            if lower.startswith("meta-inf/") and (lower.endswith(".rsa") or lower.endswith(".dsa") or lower.endswith(".ec") or lower.endswith(".mf")):
                data = zf.read(info.filename)
                certs.append({"name": info.filename, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)})

    return {
        "path": str(apk),
        "package": package,
        "version_name": version_name,
        "version_code": version_code,
        "min_sdk": min_sdk,
        "target_sdk": target_sdk,
        "compile_sdk": compile_sdk,
        "permissions": permissions,
        "files": names,
        "dex_count": sum(1 for name in names if name.endswith(".dex")),
        "so_count": sum(1 for name in names if name.endswith(".so")),
        "asset_count": sum(1 for name in names if name.startswith("assets/")),
        "certs": certs,
        "signature_status": "unknown",
    }


def list_archive_files(apk_path: str | Path, *, so: bool = False, assets: bool = False, limit: int = 100, offset: int = 0) -> list[str]:
    """List archive paths, filtering to native libs or assets if requested."""

    apk = Path(apk_path)
    with zipfile.ZipFile(apk) as zf:
        names = zf.namelist()

    filtered: list[str] = []
    for name in names:
        if so and name.endswith(".so"):
            filtered.append(name)
        elif assets and name.startswith("assets/"):
            filtered.append(name)
        elif not so and not assets:
            filtered.append(name)

    return filtered[offset:offset + limit]


def extract_strings_from_path(target_path: str | Path, *, min_len: int = 4, entropy: bool = False) -> list[str]:
    """Best-effort extraction of printable strings from a file or APK."""

    path = Path(target_path)
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if zipfile.is_zipfile(path):
        strings: list[str] = []
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                try:
                    blob = zf.read(name)
                except Exception:
                    continue
                strings.extend(re.findall(rb"[\x20-\x7E]{%d,}" % max(min_len, 4), blob))
        return [s.decode("utf-8", errors="replace") for s in strings if len(s) >= min_len]

    matches = re.findall(rb"[\x20-\x7E]{%d,}" % max(min_len, 4), path.read_bytes())
    values = [m.decode("utf-8", errors="replace") for m in matches]
    if entropy:
        return [v for v in values if len(v) >= min_len]
    return [v for v in values if len(v) >= min_len]


def decode_axml(path: str | Path) -> dict[str, Any]:
    """Decode XML-like files and fall back gracefully when binary XML is encountered."""

    file_path = Path(path)
    data = file_path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return {"path": str(file_path), "decoded": False, "note": "Binary XML or non-UTF8 content."}
    if "<" in text[:256]:
        return {"path": str(file_path), "decoded": True, "content": text[:4000]}
    return {"path": str(file_path), "decoded": False, "note": "No XML payload was detected."}


def decode_arsc(path: str | Path) -> dict[str, Any]:
    """Best-effort ARSC resource decode"""

    file_path = Path(path)
    data = file_path.read_bytes()
    entries: list[str] = []
    for match in re.findall(rb"(?:[A-Za-z0-9_./-]+)\\x00", data[:4096]):
        value = match.decode("utf-8", errors="replace").rstrip("\x00")
        if value:
            entries.append(value)
    return {"path": str(file_path), "decoded": True, "entries": entries[:200]}


__all__ = ["inspect_apk", "list_archive_files", "extract_strings_from_path", "decode_axml", "decode_arsc"]
