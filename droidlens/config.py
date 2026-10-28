from __future__ import annotations

import importlib.util
from typing import Any

from droidlens.adapters.ag_v4 import AgV4Backend
from droidlens.adapters.ag_v5 import AgV5Backend


def detect_backend() -> Any:
    """Prefer the newest Androguard backend that is available."""

    if importlib.util.find_spec("androguard") is None:
        return None

    try:
        return AgV5Backend()
    except Exception:
        try:
            return AgV4Backend()
        except Exception:
            return None
