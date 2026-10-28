# DroidLens

Adaptive Android Reverse-Engineering & Pentest Workbench

Built by Abdul Wasay Khan

DroidLens is a Python 3.11+ toolkit for authorized Android reverse engineering and pentesting. It is designed as a library-first analyst workbench for inspecting Android application artifacts, decoding resources, disassembling code, browsing app structure, and optionally driving Frida-based instrumentation in a resumable session workflow.

This project is intentionally designed for meaningful security analysis work, not for malware sandboxing or unsafe automation. It assumes authorized use and emphasizes transparency, deterministic behavior, and a clean analyst workflow.

## Project goals

- Open APK, DEX, ODEX, OAT, and VDEX-style artifacts
- Decode Android binary XML (AXML) and resources tables
- Disassemble Dalvik bytecode and provide best-effort decompilation
- Browse files, classes, methods, strings, and references
- Drive instrumentation via Frida when live analysis is required
- Persist analysis in sessions so work can be resumed later
- Optionally use AI providers for summarization and triage

## Repository structure

```text
droidlens/
├── __init__.py
├── config.py
├── core.py
├── errors.py
├── models.py
├── adapters/
├── formats/
├── static/
├── dynamic/
├── session/
├── cli/
├── docs/
├── README.md
├── pyproject.toml
├── requirements.txt
└── tests/
```

## Quick start

### 1) Create a virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 3) Verify the CLI works

```bash
droidlens --version
```

### 4) Open an APK or artifact

```bash
droidlens open /path/to/app.apk --name demo
```

### 5) View sessions

```bash
droidlens sessions
```

## Example API usage

```python
from droidlens import DroidLens

app = DroidLens.open("/path/to/app.apk", session="demo")
summary = app.info()
print(summary)
```

## Configuration

DroidLens loads layered config from the environment and a user config file, using a default session directory under the user profile. You can override settings through environment variables such as:

- DROIDLENS_SESSION_DIR
- DROIDLENS_WORK_DIR
- DROIDLENS_DEFAULT_MODE
- DROIDLENS_DEFAULT_AI_PROVIDER

## Notes

- Network access is only touched for AI providers and Frida device bridge workflows.
- The project follows a library-first design: every CLI action is a thin wrapper over an explicit API call.
- All third-party parsing is kept behind the adapter layer.
- Analysis artifacts are written to a work directory rather than mutating the source APK.

## Security and legal note

This project is intended for authorized security testing and internal research only. It must be used only in environments where you have explicit permission to analyze the target application.

## Watermark / attribution

DroidLens is developed and maintained by Abdul Wasay Khan.

Copyright (c) 2026 Abdul Wasay Khan

---

"Adaptive Android Reverse-Engineering & Pentest Workbench"
