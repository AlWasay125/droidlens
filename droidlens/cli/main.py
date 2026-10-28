from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from droidlens.adapters.detect import detect_backend
from droidlens.config import load_config
from droidlens.errors import SessionNotFoundError
from droidlens.formats.apk import decode_arsc, decode_axml, extract_strings_from_path, inspect_apk, list_archive_files
from droidlens.session.store import SessionStore
from droidlens.static.browse import list_files
from droidlens.static.manifest import manifest_summary


def sha256_file(path: str | Path) -> str:
    """Hash a file on disk using SHA-256."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


class DroidLens:
    """Library-first app session object for static and dynamic analysis."""

    def __init__(
        self,
        target_path: str | Path,
        session_name: str | None = None,
        work_dir: str | None = None,
        session_store: SessionStore | None = None,
        backend: Any | None = None,
    ) -> None:
        self.config = load_config()
        self.target_path = Path(target_path).expanduser().resolve()
        self.session_store = session_store or SessionStore(work_dir or self.config["work_dir"] or self.config["session_dir"])
        self.backend = backend or detect_backend()
        self.session_name = session_name or self.target_path.stem
        self.session_id = ""

    @classmethod
    def open(cls, path: str, session: str | None = None, work_dir: str | None = None) -> "DroidLens":
        """Open a target artifact and create or resume a session."""

        config = load_config()
        resolved_work_dir = work_dir or config["work_dir"] or config["session_dir"]
        store = SessionStore(resolved_work_dir)
        target_path = Path(path).expanduser().resolve()
        target_hash = sha256_file(target_path)

        existing = store.find_by_target_hash(target_hash)
        if existing is not None:
            instance = cls(target_path, session_name=existing["name"], work_dir=resolved_work_dir)
            instance.session_id = existing["id"]
            instance.session_name = existing["name"]
            instance.config = config
            return instance

        created_name = session or f"{target_path.stem}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        session_id = store.create_session(
            name=created_name,
            mode=config["default_mode"],
            target_path=str(target_path),
            target_sha256=target_hash,
            package=None,
            version_name=None,
            version_code=None,
            notes=None,
        )
        instance = cls(target_path, session_name=created_name, work_dir=resolved_work_dir)
        instance.session_id = session_id
        return instance

    @classmethod
    def resume(cls, session_name: str, work_dir: str | None = None) -> "DroidLens":
        """Resume a known session by name."""

        config = load_config()
        resolved_work_dir = work_dir or config["work_dir"] or config["session_dir"]
        store = SessionStore(resolved_work_dir)
        record = store.get_session_by_name(session_name)
        if record is None:
            raise SessionNotFoundError(f"Session '{session_name}' was not found")

        instance = cls(record["target_path"], session_name=record["name"], work_dir=resolved_work_dir)
        instance.session_id = record["id"]
        return instance

    def info(self) -> dict[str, Any]:
        """Return a minimal summary for the active target and session."""

        backend_name = getattr(self.backend, "name", self.backend.__class__.__name__ if self.backend is not None else "unset")
        manifest = self.manifest_summary()
        return {
            "id": self.session_id,
            "name": self.session_name,
            "target": str(self.target_path),
            "backend": backend_name,
            "package": manifest.get("package"),
            "version_name": manifest.get("version_name"),
            "version_code": manifest.get("version_code"),
            "permissions": manifest.get("permissions", []),
        }

    def manifest_summary(self) -> dict[str, Any]:
        """Return manifest and package metadata for the opened target."""

        return manifest_summary(self.target_path)

    def files(self, *, so: bool = False, assets: bool = False, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        """List files in the APK or directory target."""

        return list_files(self.target_path, so=so, assets=assets, limit=limit, offset=offset)

    def certs(self) -> list[dict[str, Any]]:
        """Return the certificate metadata found in META-INF blocks."""

        return inspect_apk(self.target_path)["certs"]

    def strings(self, *, min_len: int = 4, entropy: bool = False) -> list[str]:
        """Return printable strings found in the target artifact."""

        return extract_strings_from_path(self.target_path, min_len=min_len, entropy=entropy)

    def resources(self, *, type_filter: str | None = None, grep: str | None = None) -> dict[str, Any]:
        """Return a best-effort decode of resource data."""

        info = inspect_apk(self.target_path)
        payload: dict[str, Any] = {"path": str(self.target_path), "resources": []}
        for entry in info["files"]:
            lower = entry.lower()
            if lower.endswith("resources.arsc"):
                with Path(self.target_path).open("rb") as handle:
                    data = handle.read() if Path(self.target_path).is_file() else b""
                if not data:
                    continue
                decoded = decode_arsc(Path(self.target_path))
                payload["resources"] = decoded.get("entries", [])
        if grep:
            payload["resources"] = [item for item in payload["resources"] if grep.lower() in str(item).lower()]
        if type_filter:
            payload["type_filter"] = type_filter
        return payload

    def axml(self, path: str | Path) -> dict[str, Any]:
        """Decode XML data from a path, if present."""

        return decode_axml(path)

    def manifest(self) -> dict[str, Any]:
        """Compatibility wrapper for manifest summary."""

        return self.manifest_summary()

    def close(self) -> None:
        """Close the session object; no-op for this scaffold."""

        return None


__all__ = ["DroidLens", "sha256_file"]
