from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HookSpec:
    class_name: str
    method_name: str
    pattern: str = "before"
    script: str = ""
    args: dict[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        return (
            f"Java.perform(() => {{\n"
            f"  const cls = Java.use('{self.class_name}');\n"
            f"  cls.{self.method_name}.overload('*').implementation = function() {{\n"
            f"    console.log('hooked', '{self.class_name}', '{self.method_name}');\n"
            f"    return this.{self.method_name}.apply(this, arguments);\n"
            f"  }};\n"
            f"}});\n"
        )


__all__ = ["HookSpec"]
