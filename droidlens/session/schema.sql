from __future__ import annotations

from pathlib import Path

from droidlens import DroidLens
from droidlens.adapters.backend import BackendExecutor
from droidlens.session.store import SessionStore


def test_session_store_round_trip(tmp_path: Path) -> None:
    store = SessionStore(tmp_path)
    session_id = store.create_session(
        name="demo-session",
        mode="static",
        target_path="/tmp/demo.apk",
        target_sha256="abc123",
        package="com.example.app",
        version_name="1.0",
        version_code="1",
        notes="demo",
    )
    record = store.get_session(session_id)
    assert record is not None
    assert record["name"] == "demo-session"
    assert record["package"] == "com.example.app"


def test_open_and_resume_basic(tmp_path: Path) -> None:
    app_path = tmp_path / "sample.apk"
    app_path.write_bytes(b"dummy")
    session = DroidLens.open(str(app_path), session="demo", work_dir=str(tmp_path))
    assert session.session_name == "demo"
    assert session.info()["target"] == str(app_path.resolve())

    resumed = DroidLens.resume("demo", work_dir=str(tmp_path))
    assert resumed.session_name == "demo"


def test_backend_executor_simple_submit() -> None:
    executor = BackendExecutor()
    future = executor.submit(lambda x, y: x + y, 2, 3)
    assert future.result(timeout=5) == 5

