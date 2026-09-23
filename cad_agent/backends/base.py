"""Backend abstraction. Explicit selection, FAIL CLOSED, no silent fallback."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod

from ..errors import CadError, BACKEND_UNAVAILABLE, DRAWING_NOT_FOUND


class CadBackend(ABC):
    name = "base"

    @abstractmethod
    def open_identity(self, path: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_entities(self, path: str, layer: str | None = None) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_entity(self, path: str, handle: str) -> dict:
        raise NotImplementedError


def resolve_backend(name: str | None) -> CadBackend:
    """Resolve backend EXPLICITLY. name must be 'file' or 'autocad_live'.
    Env CAD_BACKEND is used only when name is None, and must still be explicit
    ('file' or 'autocad_live'). 'auto' is REJECTED (spec section 4)."""
    from .ezdxf_backend import FileCadBackend
    raw = (name or os.environ.get("CAD_BACKEND", "")).strip().lower()
    if raw in ("", "auto"):
        raise CadError(BACKEND_UNAVAILABLE if raw == "" else "BACKEND_AMBIGUOUS",
                       f"CAD backend must be explicit ('file' or 'autocad_live'), got '{raw or '<empty>'}'. "
                       f"Refusing silent fallback. Set CAD_BACKEND=file or CAD_BACKEND=autocad_live.",
                       {"requested": raw or None})
    if raw == "file":
        return FileCadBackend()
    if raw in ("autocad_live", "autocad", "live"):
        from .autocad_backend import AutoCadLiveBackend
        return AutoCadLiveBackend()
    raise CadError(BACKEND_UNAVAILABLE, f"Unknown CAD backend '{raw}'. Use 'file' or 'autocad_live'.",
                   {"requested": raw})
