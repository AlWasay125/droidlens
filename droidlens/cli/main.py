from __future__ import annotations

import importlib.util
from typing import Any

from droidlens.adapters.backend import AndroguardBackend
from droidlens.errors import BackendNotAvailableError


class AgV4Backend(AndroguardBackend):
    """Adapter targeting Androguard 4.1.4."""

    name = "androguard_v4"

    def __init__(self) -> None:
        if importlib.util.find_spec("androguard") is None:
            raise BackendNotAvailableError("androguard is not installed")
        self.capabilities = {
            "v5": False,
            "v4": True,
            "decompile": False,
            "axml": True,
            "arsc": True,
            "native": False,
            "certs": True,
        }

    def open_apk(self, path: str) -> Any:
        return {"path": path, "backend": "v4", "status": "stub"}

    def open_dex(self, path: str) -> Any:
        return {"path": path, "backend": "v4", "status": "stub"}

    def list_classes(self, apk: Any | None = None) -> list[str]:
        return []

    def list_methods(self, class_name: str) -> list[str]:
        return []

    def get_bytecode(self, class_name: str, method: str) -> Any:
        return {}

    def disassemble(self, class_name: str, method: str) -> str:
        return f"// {class_name}::{method} (stubbed disassembly for v4 backend)"

    def decompile(self, class_name: str, method: str) -> str:
        return f"// {class_name}::{method} (decompile unavailable in v4 stub)"

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
