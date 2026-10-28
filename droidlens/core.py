from __future__ import annotations

from pathlib import Path
from typing import Any

from droidlens.static.browse import list_files as browse_files


class DroidLens:
    def __init__(self, path: str | Path | None = None, session: str | None = None) -> None:
        self.path = str(path) if path is not None else None
        self.session = session

    @classmethod
    def open(cls, path: str | Path, session: str | None = None) -> "DroidLens":
        return cls(path=path, session=session)

    @classmethod
    def resume(cls, session: str) -> "DroidLens":
        return cls(path=None, session=session)

    def info(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "session": self.session,
        }

    def files(
        self,
        *,
        so: bool = False,
        assets: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        if self.path is None:
            raise ValueError("No artifact path configured")
        return browse_files(self.path, so=so, assets=assets, limit=limit, offset=offset)
