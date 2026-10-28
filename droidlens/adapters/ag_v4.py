from __future__ import annotations

import importlib.util
from typing import Any

from droidlens.adapters.backend import AndroguardBackend
from droidlens.errors import BackendNotAvailableError


class AgV5Backend(AndroguardBackend):
    """Adapter targeting Androguard v5 / current API."""

    name = "androguard_v5"

    def __init__(self) -> None:
        if importlib.util.find_spec("androguard") is None:
            raise BackendNotAvailableError("androguard is not installed")
        self.capabilities = {
            "v5": True,
            "v4": False,
            "decompile": importlib.util.find_spec("androguard.decompiler") is not None,
            "axml": True,
            "arsc": True,
            "native": False,
            "certs": True,
        }

    def open_apk(self, path: str) -> Any:
        return {"path": path, "backend": "v5", "status": "stub"}

    def open_dex(self, path: str) -> Any:
        return {"path": path, "backend": "v5", "status": "stub"}

    def list_classes(self, apk: Any | None = None) -> list[str]:
        return []

    def list_methods(self, class_name: str) -> list[str]:
        return []

    def get_bytecode(self, class_name: str, method: str) -> Any:
        return {}

    def disassemble(self, class_name: str, method: str) -> str:
        return f"// {class_name}::{method} (stubbed disassembly for v5 backend)"

    def decompile(self, class_name: str, method: str) -> str:
        return f"// {class_name}::{method} (decompile unavailable in stub backend)"

    def xrefs(self, kind: str, ref: str) -> list[str]:
        return []

    def scan_vulns(self, apk: Any | None = None) -> list[dict[str, Any]]:
        return []

    def decode_axml(self, path: str) -> dict[str, Any]:
        return {"path": path, "xml": "<stub />"}

    def decode_arsc(self, path: str) -> dict[str, Any]:
        return {"path": path, "resources": []}

    def certs(self, apk: Any | None = None) -> list[dict[str, Any]]:
        return []

    def native(self, apk: Any | None = None) -> list[dict[str, Any]]:
        return []
