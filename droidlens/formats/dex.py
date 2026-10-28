from __future__ import annotations

from pathlib import Path
from typing import Any

from droidlens.formats.dex import decompile, disassemble, list_classes, list_methods


def code_summary(target_path: str | Path, *, class_name: str | None = None, method_name: str | None = None) -> dict[str, Any]:
    """Return a normalized best-effort view of DEX class/method metadata."""

    classes = list_classes(target_path)
    selected_methods: list[dict[str, str]] = list_methods(target_path, class_name=class_name)
    if method_name:
        selected_methods = [m for m in selected_methods if m["method"] == method_name]
    return {
        "path": str(target_path),
        "classes": classes,
        "methods": selected_methods,
        "disassembly": disassemble(target_path, class_name=class_name, method_name=method_name),
        "decompile": decompile(target_path, class_name=class_name, method_name=method_name),
    }


__all__ = ["code_summary"]
