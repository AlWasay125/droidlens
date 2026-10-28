from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _normalize_class_name(value: str) -> str:
    return value.replace("/", ".").strip("L;")


def _class_names_from_blob(blob: bytes) -> list[str]:
    parts = []
    for match in re.findall(rb"L[A-Za-z0-9_$/]+;", blob):
        text = match.decode("utf-8", errors="replace")
        normalized = _normalize_class_name(text)
        if normalized:
            parts.append(normalized)
    seen: set[str] = set()
    out: list[str] = []
    for name in parts:
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def list_classes(target_path: str | Path) -> list[str]:
    """Best-effort list of classes present in a DEX file or a directory tree."""

    path = Path(target_path)
    if path.is_dir():
        found: list[str] = []
        for file in sorted(path.rglob("*.dex")):
            found.extend(_class_names_from_blob(file.read_bytes()))
        return sorted(set(found))
    if path.is_file() and path.suffix.lower() == ".dex":
        return sorted(set(_class_names_from_blob(path.read_bytes())))
    return []


def list_methods(target_path: str | Path, class_name: str | None = None) -> list[dict[str, str]]:
    """Best-effort extraction of method descriptors from a DEX blob."""

    path = Path(target_path)
    if not path.exists():
        return []

    blob = path.read_bytes()
    methods: list[dict[str, str]] = []
    for match in re.finditer(rb"L([A-Za-z0-9_$/]+);->([A-Za-z0-9_$]+)\(([^)]*)\)([A-Za-z0-9_$/\[\];]*)", blob):
        klass = _normalize_class_name(f"L{match.group(1).decode('utf-8', 'replace')};")
        method = match.group(2).decode("utf-8", errors="replace")
        descriptor = match.group(3).decode("utf-8", errors="replace")
        if class_name and klass != class_name:
            continue
        methods.append({"class": klass, "method": method, "descriptor": descriptor})

    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for m in methods:
        key = (m["class"], m["method"], m["descriptor"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(m)
    return unique


def disassemble(target_path: str | Path, class_name: str | None = None, method_name: str | None = None) -> dict[str, Any]:
    """Return a pseudo-disassembly for DEX methods found in the target."""

    methods = list_methods(target_path, class_name=class_name)
    if method_name:
        methods = [m for m in methods if m["method"] == method_name]
    if not methods:
        return {
            "path": str(target_path),
            "class": class_name,
            "method": method_name,
            "instructions": ["// No DEX method metadata available in this scaffold."],
        }

    instructions: list[str] = []
    for method in methods:
        instructions.append(f".class {method['class']}")
        instructions.append(f".method {method['method']}({method['descriptor']})V")
        instructions.append("  0x00: const/4 v0, 0x0")
        instructions.append("  0x01: move-result v0")
        instructions.append("  0x02: return-void")
        instructions.append(".end method")
    return {
        "path": str(target_path),
        "class": class_name or methods[0]["class"],
        "method": method_name or methods[0]["method"],
        "instructions": instructions,
    }


def decompile(target_path: str | Path, class_name: str | None = None, method_name: str | None = None) -> dict[str, Any]:
    """Best-effort Java-like pseudo-decompilation, with fallback to disassembly when necessary."""

    methods = list_methods(target_path, class_name=class_name)
    if method_name:
        methods = [m for m in methods if m["method"] == method_name]
    if not methods:
        disasm = disassemble(target_path, class_name=class_name, method_name=method_name)
        return {
            "path": str(target_path),
            "class": class_name,
            "method": method_name,
            "source": "// Best-effort decompilation unavailable.\n",
            "fallback": disasm["instructions"],
        }

    method = methods[0]
    source = (
        f"class {method['class']} {{\n"
        f"  // best-effort decompilation for {method['method']}({method['descriptor']})\n"
        "  public void generatedMethod() {\n"
        "    // Exact Java reconstruction is not available in this scaffold.\n"
        "  }\n"
        "}\n"
    )
    return {
        "path": str(target_path),
        "class": method["class"],
        "method": method["method"],
        "source": source,
        "fallback": disassemble(target_path, class_name=class_name, method_name=method_name)["instructions"],
    }


__all__ = ["list_classes", "list_methods", "disassemble", "decompile"]
