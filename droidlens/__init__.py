from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from droidlens.config import load_config


def sha256_file(path: str | Path) -> str:
    """Compute a sha256 for an artifact path."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True)
