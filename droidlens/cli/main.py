from __future__ import annotations

import json

import typer

from droidlens import __version__
from droidlens.core import DroidLens
from droidlens.formats.apk import inspect_apk


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def version() -> None:
    typer.echo(f"droidlens v{__version__}")


@app.command("open")
def open_cmd(
    path: str,
    name: str | None = typer.Option(None, "--name"),
    mode: str = typer.Option("static", "--mode"),
) -> None:
    dl = DroidLens.open(path, session=name)
    payload = dl.info()
    payload["mode"] = mode
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("files")
def files_cmd(
    path: str,
    so: bool = typer.Option(False, "--so"),
    assets: bool = typer.Option(False, "--assets"),
    limit: int = typer.Option(100, "--limit"),
    offset: int = typer.Option(0, "--offset"),
) -> None:
    payload = DroidLens.open(path).files(so=so, assets=assets, limit=limit, offset=offset)
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command("certs")
def certs_cmd(path: str) -> None:
    info = inspect_apk(path)
    typer.echo(json.dumps({"path": path, "certs": info["certs"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    app()
