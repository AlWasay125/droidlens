from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import tomllib
from platformdirs import user_config_dir

DEFAULT_CONFIG: dict[str, Any] = {
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
    """Load layered configuration from config files and environment variables."""

    config: dict[str, Any] = dict(DEFAULT_CONFIG)
    file_path = Path(config_path).expanduser() if config_path else Path(user_config_dir("droidlens")) / "config.toml"
    if file_path.exists():
        try:
            with file_path.open("rb") as handle:
                loaded = tomllib.load(handle)
            if isinstance(loaded, dict):
                config.update(loaded)
        except Exception:
            pass

    for env_name, key in {
        "DROIDLENS_SESSION_DIR": "session_dir",
        "DROIDLENS_WORK_DIR": "work_dir",
        "DROIDLENS_DEFAULT_MODE": "default_mode",
        "DROIDLENS_DEFAULT_AI_PROVIDER": "default_ai_provider",
    }.items():
        value = os.getenv(env_name)
        if value is not None:
            config[key] = value

    config["session_dir"] = _expand_path(config.get("session_dir")) or str(Path.home() / ".droidlens" / "sessions")
    if config.get("work_dir"):
        config["work_dir"] = _expand_path(config["work_dir"])
    return config


def write_default_config(path: str | None = None) -> Path:
    """Persist a default config file if one does not already exist."""

    target_dir = Path(path).expanduser() if path else Path(user_config_dir("droidlens"))
    target_dir.mkdir(parents=True, exist_ok=True)
    config_path = target_dir / "config.toml"
    if not config_path.exists():
        config_path.write_text(
            "[ai]\ndefault = \"gemini\"\n\n[ai.providers.gemini]\nkind = \"gemini\"\nmodel = \"gemini-2.5-pro\"\napi_key_env = \"GEMINI_API_KEY\"\n",
            encoding="utf-8",
        )
    return config_path
