from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import tomllib
from platformdirs import user_config_dir

DEFAULT_CONFIG = {
    "session_dir": "~/.droidlens/sessions",
    "work_dir": None,
    "default_mode": "static",
    "default_ai_provider": "gemini",
    "quiet": False,
    "no_color": False,
    "json": False,
    "debug": False,
}


def _expand_path(value: str | None) -> str | None:
    if value is None:
        return None
    return str(Path(value).expanduser())


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """Load layered configuration from env and user config."""

    config: dict[str, Any] = dict(DEFAULT_CONFIG)
    file_path = Path(config_path).expanduser() if config_path else Path(user_config_dir("droidlens")) / "config.toml"
    if file_path.exists():
        with file_path.open("rb") as fh:
            loaded = tomllib.load(fh)
        if isinstance(loaded, dict):
            config.update(loaded)

    for key in ("SESSION_DIR", "WORK_DIR", "DEFAULT_MODE", "DEFAULT_AI_PROVIDER"):
        env_key = f"DROIDLENS_{key}"
        value = os.getenv(env_key)
        if value is None:
            continue
        if key == "SESSION_DIR":
            config["session_dir"] = value
        elif key == "WORK_DIR":
            config["work_dir"] = value
        elif key == "DEFAULT_MODE":
            config["default_mode"] = value
        elif key == "DEFAULT_AI_PROVIDER":
            config["default_ai_provider"] = value

    config["session_dir"] = _expand_path(config["session_dir"]) or str(Path.home() / ".droidlens" / "sessions")
    if config.get("work_dir"):
        config["work_dir"] = _expand_path(config["work_dir"])
    return config


def write_default_config(path: str | None = None) -> Path:
    """Write a default droidlens config file if none exists."""

    config_dir = Path(path).expanduser() if path else Path(user_config_dir("droidlens"))
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.toml"
    if not config_path.exists():
        config_path.write_text(
            "[ai]\ndefault = \"gemini\"\n\n[ai.providers.gemini]\nkind = \"gemini\"\nmodel = \"gemini-2.5-pro\"\napi_key_env = \"GEMINI_API_KEY\"\n",
            encoding="utf-8",
        )
    return config_path
