from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


class DroidLensError(RuntimeError):
    """Root exception for droidlens runtime failures."""

    code = "droidlens_error"


class ConfigurationError(DroidLensError):
    code = "config_error"


class SessionNotFoundError(DroidLensError):
    code = "session_not_found"


class ArtifactNotFoundError(DroidLensError):
    code = "artifact_not_found"


class BackendNotAvailableError(DroidLensError):
    code = "backend_unavailable"


class DeviceError(DroidLensError):
    code = "device_error"


class AIError(DroidLensError):
    code = "ai_error"


@dataclass(frozen=True)
class CapabilityFlags:
    v5: bool = False
    v4: bool = False
    decompile: bool = False
    axml: bool = True
    arsc: bool = True
    native: bool = False
    certs: bool = True


@dataclass
class SessionContext:
    session_id: str
    name: str
    mode: str
    work_dir: Path
    target_path: Path
    target_sha256: str
    package: str | None = None
    version_name: str | None = None
    version_code: str | None = None
    notes: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)
