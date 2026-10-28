from __future__ import annotations

import json
from typing import Any


def trace_method(class_name: str, method_name: str, *, include_args: bool = True, include_return: bool = True) -> dict[str, Any]:
    """Represent a tracing spec for a Java method call."""

    return {
        "class_name": class_name,
        "method_name": method_name,
        "include_args": include_args,
        "include_return": include_return,
        "script": (
            "Java.perform(() => {\n"
            "  const cls = Java.use('" + class_name + "');\n"
            "  cls.'" + method_name + "'.overload('*').implementation = function() {\n"
            "    console.log('TRACE', '" + class_name + "', '" + method_name + "');\n"
            "    return this.'" + method_name + "'.apply(this, arguments);\n"
            "  };\n"
            "});\n"
        ),
    }


__all__ = ["trace_method"]
