from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application configuration settings."""

    session_dir: str = "~/.droidlens/sessions"
    work_dir: str | None = None
    default_mode: str = "static"
    default_ai_provider: str = "gemini"
    quiet: bool = False
    no_color: bool = False
    json: bool = False
    debug: bool = False


class ManifestSummary(BaseModel):
    """Summary data for a target app manifest."""

    package: str | None = None
    version_name: str | None = None
    version_code: str | None = None
    min_sdk: int | None = None
    target_sdk: int | None = None
    compile_sdk: int | None = None
    permissions: list[str] = Field(default_factory=list)


class SessionRecord(BaseModel):
    """Normalized session metadata."""

    id: str
    name: str
    created_at: str
    updated_at: str
    mode: str = "static"
    target_path: str
    target_sha256: str
    package: str | None = None
    version_name: str | None = None
    version_code: str | None = None
    notes: str | None = None


class ArtifactRecord(BaseModel):
    """Artifact metadata stored in the session database."""

    id: int | None = None
    kind: str
    name: str
    path: str
    sha256: str | None = None
    meta_json: dict[str, Any] = Field(default_factory=dict)


class FindingRecord(BaseModel):
    """A single static/dynamic finding."""

    id: int | None = None
    category: str
    severity: str
    title: str
    evidence: str
    evidence_refs_json: list[str] = Field(default_factory=list)
    masvs_id: str | None = None
    source: str | None = None
    confidence: str = "medium"
    status: str = "open"


__all__ = [
    "AppConfig",
    "ManifestSummary",
    "SessionRecord",
    "ArtifactRecord",
    "FindingRecord",
]
