from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _adb_cmd(args: list[str]) -> dict[str, Any]:
    """Run an adb command and return a normalized result."""

    result = subprocess.run(["adb", *args], capture_output=True, text=True)
    return {
        "args": args,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def list_devices() -> list[dict[str, Any]]:
    """List attached Android devices via adb."""

    payload = _adb_cmd(["devices", "-l"])
    if payload["returncode"] != 0:
        return []
    lines = payload["stdout"].splitlines()[1:]
    devices: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append({"serial": parts[0], "state": parts[1], "details": " ".join(parts[2:])})
    return devices


def install_frida_server(device_serial: str | None = None) -> dict[str, Any]:
    """Best-effort Frida server bootstrap helper; returns command output without forcing a failure."""

    serial = device_serial or ""
    cmd = ["adb", "shell", "frida-server", "-h"] if serial == "" else ["adb", "-s", serial, "shell", "frida-server", "-h"]
    return subprocess.run(cmd, capture_output=True, text=True).__dict__


def spawn_app(package: str, *, serial: str | None = None, activity: str | None = None) -> dict[str, Any]:
    """Launch a package on a connected Android device."""

    if serial:
        cmd = ["adb", "-s", serial, "shell", "am", "start", package]
    else:
        cmd = ["adb", "shell", "am", "start", package]
    if activity:
        cmd = ["adb", "-s", serial, "shell", "am", "start", "-n", f"{package}/{activity}"] if serial else ["adb", "shell", "am", "start", "-n", f"{package}/{activity}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {"args": cmd, "returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


__all__ = ["list_devices", "install_frida_server", "spawn_app"]
