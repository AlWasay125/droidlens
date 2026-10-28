from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Core application configuration."""

    session_dir: str = Field(default="~/.droidlens/sessions")
    work_dir: str | None = None
    default_mode: str = "static"
    default_ai_provider: str = "gemini"
    quiet: bool = False
    no_color: bool = False
    json: bool = False
    debug: bool = False


class ManifestSummary(BaseModel):
    package: str | None = None
    version_name: str | None = None
    version_code: str | None = None
    min_sdk: int | None = None
    target_sdk: int | None = None
    compile_sdk: int | None = None
    permissions: list[str] = Field(default_factory=list)


class SessionRecord(BaseModel):
    id: str
    name: str
    mode: str = "static"
    target_path: str
    target_sha256: str
    package: str | None = None
    version_name: str | None = None
    version_code: str | None = None
    notes: str | None = None
    created_at: str
    updated_at: str


class ArtifactRecord(BaseModel):
    id: int | None = None
    kind: str
    name: str
    path: str
    sha256: str | None = None
    meta_json: dict[str, Any] = Field(default_factory=dict)


class FindingRecord(BaseModel):
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
