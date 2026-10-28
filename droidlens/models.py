from __future__ import annotations


class DroidLensError(RuntimeError):
    """Base exception for droidlens runtime mistakes."""

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


__all__ = [
    "DroidLensError",
    "ConfigurationError",
    "SessionNotFoundError",
    "ArtifactNotFoundError",
    "BackendNotAvailableError",
    "DeviceError",
    "AIError",
]
