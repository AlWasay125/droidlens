from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from droidlens import __version__
from droidlens.core import DroidLens
from droidlens.formats.apk import inspect_apk
from droidlens.session.store import SessionStore

app = typer.Typer(add_completion=False, help="Adaptive Android Reverse-Engineering & Pentest Workbench")
console = Console()


@app.callback()
def callback(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
    session: str | None = typer.Option(None, "--session", help="Session ID or name."),
    work_dir: str | None = typer.Option(None, "--work-dir", help="Path to a working directory."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress nonessential output."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colorized output."),
) -> None:
    """Global options shared by all commands."""

    ctx.obj = {
        "json": json_output,
        "session": session,
        "work_dir": work_dir,
        "quiet": quiet,
        "no_color": no_color,
    }


@app.command()
def version() -> None:
    """Print the package version and authorized-use banner."""

    typer.echo("Authorized use only.")
    typer.echo(f"droidlens v{__version__}")


@app.command("open")
def open_cmd(
    path: str,
    name: str | None = typer.Option(None, "--name", help="Override the session name."),
    mode: str = typer.Option("static", "--mode", help="Execution mode."),
) -> None:
    """Open an APK/DEX/ODEX/dir target and create or resume a session."""

    dl = DroidLens.open(path, session=name)
    payload = dl.info()
    payload["mode"] = mode
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("info")
def info_cmd(
    session: str | None = typer.Option(None, "--session", help="Session name or id."),
) -> None:
    """Print summary information for a target or session."""

    dl = DroidLens.open(".") if session is None else DroidLens.resume(session)
    typer.echo(json.dumps(dl.info(), indent=2, sort_keys=True))


@app.command("manifest")
def manifest_cmd(path: str = typer.Argument(..., help="Path to an APK or directory.")) -> None:
    """Read manifest and package metadata from a target binary."""

    summary = DroidLens.open(path).manifest_summary()
    typer.echo(json.dumps(summary, indent=2, sort_keys=True))


@app.command("resources")
def resources_cmd(
    path: str = typer.Argument(..., help="Path to an APK or data file."),
    type_filter: str | None = typer.Option(None, "--type", help="Resource type filter."),
    grep: str | None = typer.Option(None, "--grep", help="Grep within resource names."),
) -> None:
    """Return best-effort resource metadata for the target."""

    dl = DroidLens.open(path)
    payload = dl.resources(type_filter=type_filter, grep=grep)
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("files")
def files_cmd(
    path: str = typer.Argument(..., help="Path to an APK or directory."),
    so: bool = typer.Option(False, "--so", help="Only list native library files."),
    assets: bool = typer.Option(False, "--assets", help="Only list asset files."),
    limit: int = typer.Option(100, "--limit", help="Maximum number of results."),
    offset: int = typer.Option(0, "--offset", help="Result offset."),
) -> None:
    """List files or subtrees in an archive."""

    payload = DroidLens.open(path).files(so=so, assets=assets, limit=limit, offset=offset)
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("certs")
def certs_cmd(path: str = typer.Argument(..., help="Path to an APK.")) -> None:
    """List signing metadata in the archive."""

    info = inspect_apk(path)
    typer.echo(json.dumps({"path": path, "certs": info["certs"]}, indent=2, sort_keys=True))


@app.command("strings")
def strings_cmd(
    path: str = typer.Argument(..., help="Path to a file or APK."),
    min_len: int = typer.Option(4, "--min-len", help="Minimum string length."),
    entropy: bool = typer.Option(False, "--entropy", help="Toggle entropy-based filtering (no-op in scaffold)."),
) -> None:
    """Extract printable strings from an APK or file."""

    dl = DroidLens.open(path)
    values = dl.strings(min_len=min_len, entropy=entropy)
    typer.echo(json.dumps({"path": path, "strings": values[:100]}, indent=2, sort_keys=True))


@app.command("sessions")
def sessions_cmd() -> None:
    """List all known sessions."""

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
    """Update notes for a session."""

    store = SessionStore("~/.droidlens/sessions")
    record = store.get_session_by_name(session)
    if record is None:
        raise typer.BadParameter(f"Session '{session}' not found")
    store.note_session(record["id"], text)
    typer.echo(f"Updated session '{session}'")


if __name__ == "__main__":
    app()
