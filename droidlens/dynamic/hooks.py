from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


def frida_version() -> dict[str, Any]:
    """Query the installed Frida CLI version if present."""

    result = subprocess.run(["frida", "-v"], capture_output=True, text=True)
    return {"returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def list_processes(serial: str | None = None) -> list[str]:
    """List Android processes by invoking frida-ps when available."""

    cmd = ["frida-ps", "-U"] if serial is None else ["frida-ps", "-U", "-S", serial]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def spawn_script(script: str, *, device_serial: str | None = None) -> dict[str, Any]:
    """Create a Frida script launch payload for later execution."""

    bundle = {"device_serial": device_serial, "script": script, "mode": "frida"}
    return {"payload": json.dumps(bundle, sort_keys=True), "script": script}


__all__ = ["frida_version", "list_processes", "spawn_script"]
