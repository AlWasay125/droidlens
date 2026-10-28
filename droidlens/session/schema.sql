from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    mode TEXT NOT NULL,
    target_path TEXT NOT NULL,
    target_sha256 TEXT NOT NULL,
    package TEXT,
    version_name TEXT,
    version_code TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    size INTEGER,
    imported_at TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT,
    meta_json TEXT DEFAULT '{}',
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    evidence TEXT NOT NULL,
    evidence_refs_json TEXT DEFAULT '[]',
    masvs_id TEXT,
    source TEXT,
    confidence TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    created_at TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    ts TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT DEFAULT '{}',
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
"""


class SessionStore:
    """Thin SQLite wrapper for droidlens sessions."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_dir / "session.db"
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def create_session(
        self,
        *,
        name: str,
        mode: str,
        target_path: str,
        target_sha256: str,
        package: str | None,
        version_name: str | None,
        version_code: str | None,
        notes: str | None,
    ) -> str:
        import uuid
        from datetime import datetime, timezone

        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT INTO sessions (id, name, created_at, updated_at, mode, target_path, target_sha256, package, version_name, version_code, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                name,
                now,
                now,
                mode,
                target_path,
                target_sha256,
                package,
                version_name,
                version_code,
                notes,
            ),
        )
        self._conn.execute(
            "INSERT INTO events (session_id, ts, actor, action, payload_json) VALUES (?, ?, ?, ?, ?)",
            (session_id, now, "system", "session_created", '{}'),
        )
        self._conn.commit()
        return session_id

    def list_sessions(self) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id, name, created_at, updated_at, mode, target_path, target_sha256, package, version_name, version_code, notes FROM sessions ORDER BY created_at DESC"
        ).fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "mode": row[4],
                "target_path": row[5],
                "target_sha256": row[6],
                "package": row[7],
                "version_name": row[8],
                "version_code": row[9],
                "notes": row[10],
            }
            for row in rows
        ]

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id, name, created_at, updated_at, mode, target_path, target_sha256, package, version_name, version_code, notes FROM sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "created_at": row[2],
            "updated_at": row[3],
            "mode": row[4],
            "target_path": row[5],
            "target_sha256": row[6],
            "package": row[7],
            "version_name": row[8],
            "version_code": row[9],
            "notes": row[10],
        }

    def get_session_by_name(self, name: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id, name, created_at, updated_at, mode, target_path, target_sha256, package, version_name, version_code, notes FROM sessions WHERE name = ?",
            (name,),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "created_at": row[2],
            "updated_at": row[3],
            "mode": row[4],
            "target_path": row[5],
            "target_sha256": row[6],
            "package": row[7],
            "version_name": row[8],
            "version_code": row[9],
            "notes": row[10],
        }

    def find_by_target_hash(self, target_hash: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id, name, created_at, updated_at, mode, target_path, target_sha256, package, version_name, version_code, notes FROM sessions WHERE target_sha256 = ? LIMIT 1",
            (target_hash,),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "created_at": row[2],
            "updated_at": row[3],
            "mode": row[4],
            "target_path": row[5],
            "target_sha256": row[6],
            "package": row[7],
            "version_name": row[8],
            "version_code": row[9],
            "notes": row[10],
        }

    def note_session(self, session_id: str, notes: str) -> None:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "UPDATE sessions SET notes = ?, updated_at = ? WHERE id = ?",
            (notes, now, session_id),
        )
        self._conn.execute(
            "INSERT INTO events (session_id, ts, actor, action, payload_json) VALUES (?, ?, ?, ?, ?)",
            (session_id, now, "system", "note", f'{{"text": {notes!r}}}'),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
