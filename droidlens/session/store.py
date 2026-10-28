from __future__ import annotations

from pathlib import Path
from typing import Any


class SessionStore:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir).expanduser()

    def list_sessions(self) -> list[dict[str, Any]]:
        return []

    def get_session_by_name(self, session: str) -> dict[str, Any] | None:
        return None

    def note_session(self, session_id: str, text: str) -> None:
        return None
