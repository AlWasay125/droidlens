from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Future
from queue import Queue
from threading import Thread
from typing import Any, Callable


class AndroguardBackend(ABC):
    """Abstract interface for backend adapters."""

    name: str = "backend"

    @abstractmethod
    def open_apk(self, path: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def open_dex(self, path: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def list_classes(self, apk: Any | None = None) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def list_methods(self, class_name: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_bytecode(self, class_name: str, method: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def disassemble(self, class_name: str, method: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def decompile(self, class_name: str, method: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def xrefs(self, kind: str, ref: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def scan_vulns(self, apk: Any | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def decode_axml(self, path: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def decode_arsc(self, path: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def certs(self, apk: Any | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def native(self, apk: Any | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError


class BackendExecutor:
    """Single-owner executor for thread-affine backend objects."""

    def __init__(self) -> None:
        self._queue: Queue[tuple[Callable[..., Any], tuple[Any, ...], dict[str, Any], Future[Any]]] = Queue()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while True:
            fn, args, kwargs, future = self._queue.get()
            try:
                result = fn(*args, **kwargs)
                future.set_result(result)
            except Exception as exc:  # pragma: no cover - defensive
                future.set_exception(exc)
            finally:
                self._queue.task_done()

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future[Any]:
        future: Future[Any] = Future()
        self._queue.put((fn, args, kwargs, future))
        return future


__all__ = ["AndroguardBackend", "BackendExecutor"]
