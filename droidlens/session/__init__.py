from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from droidlens.adapters.detect import detect_backend
from droidlens.config import load_config
from droidlens.errors import SessionNotFoundError
from droidlens.session.store import SessionStore
from droidlens.models import SessionRecord


class DroidLens:
    """Library-first entry point for opens and sessions."""

    def __init__(
        self,
        target_path: str | Path,
        session_name: str | None = None,
        work_dir: str | None = None,
        session_store: SessionStore | None = None,
        backend: Any | None = None,
    ) -> None:
        self.target_path = Path(target_path).expanduser().resolve()
        self.config = load_config()
        self.session_store = session_store or SessionStore(work_dir or self.config["work_dir"] or self.config["session_dir"])
        self.backend = backend or detect_backend()
        self.session_name = session_name or self.target_path.name
        self.session_id = str(uuid.uuid4())
        self.record: SessionRecord | None = None

    @classmethod
    def open(cls, path: str, session: str | None = None, work_dir: str | None = None) -> "DroidLens":
        """Open a target artifact and create or resume a session."""

        config = load_config()
        resolved_work_dir = work_dir or config["work_dir"] or config["session_dir"]
        store = SessionStore(resolved_work_dir)
        target_path = Path(path).expanduser().resolve()
        target_hash = __import__("droidlens").__dict__["sha256_file"](target_path)
        existing = store.find_by_target_hash(target_hash)
        if existing is not None:
            instance = cls.__new__(cls)
            instance.target_path = target_path
            instance.config = config
            instance.session_store = store
            instance.backend = detect_backend()
            instance.session_name = existing["name"]
            instance.session_id = existing["id"]
            instance.record = SessionRecord(**existing)
            return instance

        session_name = session or f"{target_path.stem}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        session_id = store.create_session(
            name=session_name,
            mode=config["default_mode"],
            target_path=str(target_path),
            target_sha256=target_hash,
            package=None,
            version_name=None,
            version_code=None,
            notes=None,
        )
        instance = cls.__new__(cls)
        instance.target_path = target_path
        instance.config = config
        instance.session_store = store
        instance.backend = detect_backend()
        instance.session_name = session_name
        instance.session_id = session_id
        instance.record = store.get_session(session_id)
        return instance

    @classmethod
    def resume(cls, session_name: str, work_dir: str | None = None) -> "DroidLens":
        """Resume a named session by reading its metadata from SQLite."""

        config = load_config()
        store = SessionStore(work_dir or config["work_dir"] or config["session_dir"])
        existing = store.get_session_by_name(session_name)
        if existing is None:
            raise SessionNotFoundError(f"Session '{session_name}' not found")
        instance = cls.__new__(cls)
        instance.target_path = Path(existing["target_path"])
        instance.config = config
        instance.session_store = store
        instance.backend = detect_backend()
        instance.session_name = existing["name"]
        instance.session_id = existing["id"]
        instance.record = SessionRecord(**existing)
        return instance

    def info(self) -> dict[str, Any]:
        """Return a summary card for the current session."""

        summary = {
            "id": self.session_id,
            "name": self.session_name,
            "mode": self.record.mode if self.record else "static",
            "target": str(self.target_path),
            "package": self.record.package if self.record else None,
            "version_name": self.record.version_name if self.record else None,
            "version_code": self.record.version_code if self.record else None,
            "backend": getattr(self.backend, "name", self.backend.__class__.__name__ if self.backend else "unset"),
        }
        return summary

    def manifest(self) -> dict[str, Any]:
        """Return a minimal manifest summary."""

        return {
            "package": self.record.package if self.record else None,
            "version_name": self.record.version_name if self.record else None,
            "version_code": self.record.version_code if self.record else None,
            "permissions": [],
        }

    def close(self) -> None:
        """Close the session lifetime."""

        return None


# compatibility export for the project
sha256_file = __import__("droidlens").__dict__["sha256_file"]
