from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path
from typing import Any


def _extract_manifest_xml(zf: zipfile.ZipFile) -> tuple[str | None, bytes | None]:
    for name in zf.namelist():
        lower = name.lower()
        if lower.endswith("androidmanifest.xml"):
            return name, zf.read(name)
    return None, None


def _safe_text(value: str | bytes | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def inspect_apk(apk_path: str | Path) -> dict[str, Any]:
    """Inspect an APK and return manifest, file metadata, and cert data."""

    apk = Path(apk_path)
    if not apk.exists():
        raise FileNotFoundError(f"APK not found: {apk}")

    entries: list[str] = []
    certs: list[dict[str, Any]] = []
    package: str | None = None
    version_name: str | None = None
    version_code: str | None = None
    min_sdk: str | None = None
    target_sdk: str | None = None
    compile_sdk: str | None = None
    permissions: list[str] = []

    try:
        with zipfile.ZipFile(apk) as zf:
            entries = zf.namelist()
            manifest_name, manifest_bytes = _extract_manifest_xml(zf)
            if manifest_name and manifest_bytes:
                try:
                    manifest_text = manifest_bytes.decode("utf-8", errors="replace")
                    package_match = re.search(r'package="([^"]+)"', manifest_text)
                    if package_match:
                        package = package_match.group(1)
                    version_name_match = re.search(r'android:versionName="([^"]+)"', manifest_text)
                    if version_name_match:
                        version_name = version_name_match.group(1)
                    version_code_match = re.search(r'android:versionCode="([^"]+)"', manifest_text)
                    if version_code_match:
                        version_code = version_code_match.group(1)
                    minsdk_match = re.search(r'android:minSdkVersion="([^"]+)"', manifest_text)
                    if minsdk_match:
                        min_sdk = minsdk_match.group(1)
                    targetsdk_match = re.search(r'android:targetSdkVersion="([^"]+)"', manifest_text)
                    if targetsdk_match:
                        target_sdk = targetsdk_match.group(1)
                    compilesdk_match = re.search(r'android:compileSdkVersion="([^"]+)"', manifest_text)
                    if compilesdk_match:
                        compile_sdk = compilesdk_match.group(1)
                    for perm in re.findall(r'<uses-permission[^>]*android:name="([^"]+)"', manifest_text):
                        permissions.append(perm)
                except Exception:
                    pass

            for info in zf.infolist():
                name = info.filename
                if name.startswith("META-INF/") and (name.endswith(".RSA") or name.endswith(".DSA") or name.endswith(".EC") or name.endswith(".MF")):
                    data = zf.read(info)
                    certs.append(
                        {
                            "name": name,
                            "sha256": hashlib.sha256(data).hexdigest(),
                            "size": len(data),
                        }
                    )
    except zipfile.BadZipFile as exc:
        raise ValueError(f"{apk} is not a valid zip archive: {exc}") from exc

    return {
        "path": str(apk),
        "package": package,
        "version_name": version_name,
        "version_code": version_code,
        "min_sdk": min_sdk,
        "target_sdk": target_sdk,
        "compile_sdk": compile_sdk,
        "permissions": permissions,
        "files": entries,
        "dex_count": sum(1 for name in entries if name.endswith(".dex")),
        "so_count": sum(1 for name in entries if name.endswith(".so")),
        "asset_count": sum(1 for name in entries if name.startswith("assets/")),
        "certs": certs,
        "signature_status": "unknown",
    }


def list_archive_files(apk_path: str | Path, *, so: bool = False, assets: bool = False, limit: int = 100, offset: int = 0) -> list[str]:
    """List files from an APK archive, optionally filtered to shared libraries or assets."""

    apk = Path(apk_path)
    if not apk.exists():
        raise FileNotFoundError(f"APK not found: {apk}")

    with zipfile.ZipFile(apk) as zf:
        names = zf.namelist()
    filtered = []
    for name in names:
        if so and not name.endswith(".so"):
            continue
        if assets and not name.startswith("assets/"):
            continue
        if not so and not assets:
            filtered.append(name)
        elif so and name.endswith(".so"):
            filtered.append(name)
        elif assets and name.startswith("assets/"):
            filtered.append(name)

    slice_start = offset
    slice_end = offset + limit
    return filtered[slice_start:slice_end]


def extract_strings_from_path(target_path: str | Path, *, min_len: int = 4, entropy: bool = False) -> list[str]:
    """Extract printable strings from a file or archive."""

    path = Path(target_path)
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            chunks: list[str] = []
            for name in zf.namelist():
                try:
                    data = zf.read(name)
                except Exception:
                    continue
                if not data:
                    continue
                chunks.extend(re.findall(rb"[\x20-\x7E]{%d,}" % max(4, min_len), data))
            values = [chunk.decode("utf-8", errors="replace") for chunk in chunks]
            return [s for s in values if len(s) >= min_len]

    data = path.read_bytes()
    matches = re.findall(rb"[\x20-\x7E]{%d,}" % max(4, min_len), data)
    values = [m.decode("utf-8", errors="replace") for m in matches]
    if entropy:
        return [v for v in values if len(v) >= min_len]
    return [v for v in values if len(v) >= min_len]


def decode_axml(path: str | Path) -> dict[str, Any]:
    """Best-effort decode of a binary XML or normal XML document."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    data = file_path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    if text.startswith("<?xml") or "<" in text[:256]:
        return {"path": str(file_path), "decoded": True, "content": text[:4000]}
    return {"path": str(file_path), "decoded": False, "note": "Binary XML decoding is not available in the scaffold."}


def decode_arsc(path: str | Path) -> dict[str, Any]:
    """Best-effort decode for Android resources.arsc data."""

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    raw = file_path.read_bytes()
    if not raw:
        return {"path": str(file_path), "decoded": False, "entries": []}
    entries = []
    for match in re.findall(rb"(?:[A-Za-z0-9_./-]+)\\x00", raw[:4096]):
        try:
            value = match.decode("utf-8", errors="replace").rstrip("\x00")
        except Exception:
            continue
        if value:
            entries.append(value)
    return {"path": str(file_path), "decoded": True, "entries": entries[:200]}


__all__ = [
    "inspect_apk",
    "list_archive_files",
    "extract_strings_from_path",
    "decode_axml",
    "decode_arsc",
]
