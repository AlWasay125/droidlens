from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from droidlens import __version__
from droidlens.core import DroidLens
from droidlens.errors import DroidLensError
from droidlens.session.store import SessionStore

app = typer.Typer(add_completion=False, help="Adaptive Android Reverse-Engineering & Pentest Workbench")
console = Console()


@app.callback()
def callback(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON output."),
    session: str | None = typer.Option(None, "--session", help="Select a session by id or name."),
    work_dir: str | None = typer.Option(None, "--work-dir", help="Override the work directory."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress nonessential output."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI colors."),
) -> None:
    """Global options."""

    ctx.obj = {
        "json": json_output,
        "session": session,
        "work_dir": work_dir,
        "quiet": quiet,
        "no_color": no_color,
    }


@app.command()
def version() -> None:
    """Print the droidlens version and authorized-use banner."""

    typer.echo("Authorized use only.")
    typer.echo(f"droidlens v{__version__}")


@app.command("open")
def open_cmd(
    path: str,
    name: str | None = typer.Option(None, "--name", help="Session name."),
    mode: str = typer.Option("static", "--mode", help="Execution mode."),
) -> None:
    """Open a target artifact and create or resume a session."""

    try:
        dl = DroidLens.open(path, session=name, work_dir=None)
        info = dl.info()
        if typer.get_app_dir("droidlens"):
            pass
        if name:
            print(f"Session: {name}")
        print(f"Target: {path}")
        print(f"Mode: {mode}")
        print(f"Session ID: {dl.session_id}")
        print(f"Package: {info.get('package') or 'unknown'}")
        print(f"Version: {info.get('version_name') or 'unknown'}")
    except Exception as exc:  # pragma: no cover - defensive CLI surface
        raise typer.Exit(code=1) from exc


@app.command("info")
def info_cmd(
    session: str | None = typer.Option(None, "--session", help="Session name or id."),
) -> None:
    """Print the current session information."""

    if session is None:
        session = "default"
    dl = DroidLens.resume(session)
    typer.echo(json.dumps(dl.info(), indent=2, sort_keys=True))


@app.command("sessions")
def sessions_cmd() -> None:
    """List known sessions."""

    store = SessionStore("~/.droidlens/sessions")
    rows = store.list_sessions()
    if not rows:
        typer.echo("No sessions found.")
        return
    table = Table(title="Sessions")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Mode")
    table.add_column("Target")
    for row in rows:
        table.add_row(row["id"], row["name"], row["mode"], row["target_path"])
    console.print(table)


@app.command("resume")
def resume_cmd(session: str) -> None:
    """Resume a session by name."""

    dl = DroidLens.resume(session)
    typer.echo(json.dumps(dl.info(), indent=2, sort_keys=True))


@app.command("note")
def note_cmd(session: str, text: str) -> None:
    """Add notes to a session."""

    store = SessionStore("~/.droidlens/sessions")
    record = store.get_session_by_name(session)
    if record is None:
        raise typer.BadParameter(f"Session '{session}' not found")
    store.note_session(record["id"], text)
    typer.echo(f"Updated session '{session}'")


if __name__ == "__main__":
    app()
