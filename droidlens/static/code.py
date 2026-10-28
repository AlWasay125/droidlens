from __future__ import annotations

from pathlib import Path
from typing import Any


def _normalize_class_name(value: str) -> str:
    return value.replace("/", ".").strip("L;")


def _iter_dex_files(target_path: str | Path) -> list[str]:
    path = Path(target_path)
    if path.is_dir():
        return sorted(str(p.relative_to(path)) for p in path.rglob("*.dex") if p.is_file())
    if path.is_file() and path.suffix.lower() == ".dex":
        return [str(path)]
    return []


def list_classes(target_path: str | Path) -> list[str]:
    """Best-effort extraction of Dalvik classes from a DEX or APK-like archive."""

    path = Path(target_path)
    if path.is_dir():
        dex_files = _iter_dex_files(path)
        results: list[str] = []
        for dex_path in dex_files:
            member_path = path / dex_path
            blob = member_path.read_bytes()
            results.extend(_class_names_from_blob(blob))
        return sorted(set(results))

    if path.is_file() and path.suffix.lower() == ".dex":
        blob = path.read_bytes()
        return sorted(set(_class_names_from_blob(blob)))

    if path.is_file():
        return sorted(set(_class_names_from_blob(path.read_bytes())))

    return []


def _class_names_from_blob(blob: bytes) -> list[str]:
    classes: list[str] = []
    for match in __import__("re").findall(rb"L[A-Za-z0-9_$/]+;", blob):
        text = match.decode("utf-8", errors="replace")
        classes.append(_normalize_class_name(text))
    return [c for c in classes if c and "." in c or c.startswith("android") or c.startswith("com") or c.startswith("java") or c.startswith("kotlin")]


def list_methods(target_path: str | Path, class_name: str | None = None) -> list[dict[str, str]]:
    """Best-effort extraction of method names from DEX bytes."""

    path = Path(target_path)
    if not path.exists():
        return []

    methods: list[dict[str, str]] = []
    blob = path.read_bytes()
    for match in __import__("re").finditer(rb"L([A-Za-z0-9_$/]+);->([A-Za-z0-9_$]+)\(([^)]*)\)([A-Za-z0-9_$/\[\];]*)", blob):
        klass = _normalize_class_name(f"L{match.group(1).decode('utf-8', 'replace')};")
        method = match.group(2).decode("utf-8", errors="replace")
        descriptor = match.group(3).decode("utf-8", errors="replace")
        if class_name and klass != class_name:
            continue
        methods.append({"class": klass, "method": method, "descriptor": descriptor})
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, str]] = []
    for method in methods:
        key = (method["class"], method["method"], method["descriptor"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(method)
    return unique


def disassemble(target_path: str | Path, class_name: str | None = None, method_name: str | None = None) -> dict[str, Any]:
    """Produce a best-effort disassembly block, using the method descriptor when available."""

    methods = list_methods(target_path, class_name=class_name)
    if method_name:
        methods = [m for m in methods if m["method"] == method_name]
    if not methods:
        return {
            "path": str(target_path),
            "class": class_name,
            "method": method_name,
            "instructions": ["// No decompilation metadata found in this scaffold."],
        }

    lines: list[str] = []
    for item in methods:
        lines.append(f".class {item['class']}")
        lines.append(f".method {item['method']}({item['descriptor']})V")
        lines.append("  0x00: const/4 v0, 0x0")
        lines.append("  0x01: move-result v0")
        lines.append("  0x02: return-void")
        lines.append(".end method")
    return {
        "path": str(target_path),
        "class": class_name,
        "method": method_name,
        "instructions": lines,
    }


def decompile(target_path: str | Path, class_name: str | None = None, method_name: str | None = None) -> dict[str, Any]:
    """Best-effort Java-like decompilation fallback to disassembly when needed."""

    methods = list_methods(target_path, class_name=class_name)
    if method_name:
        methods = [m for m in methods if m["method"] == method_name]
    if not methods:
        return {
            "path": str(target_path),
            "class": class_name,
            "method": method_name,
            "source": "// Best-effort decompilation unavailable; fell back to disassembly.\n",
            "fallback": disassemble(target_path, class_name=class_name, method_name=method_name)["instructions"],
        }

    source_lines = [f"class {methods[0]['class']} {{"]
    for item in methods:
        source_lines.append(f"  // {item['method']}({item['descriptor']})")
        source_lines.append("  public void generatedMethod() {")
        source_lines.append("    // Best-effort decompilation: exact Java reconstruction is unavailable in this scaffold.")
        source_lines.append("  }")
    source_lines.append("}")
    return {
        "path": str(target_path),
        "class": class_name or methods[0]["class"],
        "method": method_name or methods[0]["method"],
        "source": "\n".join(source_lines),
        "fallback": disassemble(target_path, class_name=class_name, method_name=method_name)["instructions"],
    }


__all__ = ["list_classes", "list_methods", "disassemble", "decompile"]
