"""Live AutoCAD backend stub. FAILS CLOSED unless a real IPC channel is configured.

The electrical tool layer works independently of the concrete MCP. When
CAD_BACKEND=autocad_live is selected but no functional File-IPC/AutoCAD
channel exists, every operation FAILS with BACKEND_UNAVAILABLE instead of
silently falling back to ezdxf (spec section 4).
"""
from __future__ import annotations

import os

from ..errors import CadError, BACKEND_UNAVAILABLE
from .base import CadBackend


class AutoCadLiveBackend(CadBackend):
    name = "autocad_live"

    def __init__(self):
        # Explicit channel discovery: only succeed when operator configured one.
        # Supported: AUTOCAD_MCP_IPC marker file/pipe, or CAD_LIVE_ENDPOINT.
        self.endpoint = os.environ.get("CAD_LIVE_ENDPOINT", "").strip()
        self.ipc_marker = os.environ.get("AUTOCAD_MCP_IPC", "").strip()
        available = bool(self.endpoint) or (bool(self.ipc_marker) and os.path.exists(self.ipc_marker))
        if not available:
            raise CadError(BACKEND_UNAVAILABLE,
                           "autocad_live backend selected but no functional AutoCAD IPC channel is configured. "
                           "Set CAD_LIVE_ENDPOINT or AUTOCAD_MCP_IPC to an existing channel, "
                           "or use CAD_BACKEND=file. Refusing silent fallback to ezdxf.",
                           {"endpoint": self.endpoint or None, "ipc": self.ipc_marker or None})

    def _nope(self, op="operation"):
        raise CadError(BACKEND_UNAVAILABLE,
                       f"autocad_live backend channel '{self.endpoint or self.ipc_marker}' has no "
                       f"implemented {op} in this P0 build. See docs/AUTOCAD_MCP_BACKEND_OPTIONS.md.",
                       {})

    def open_identity(self, path: str) -> dict:
        self._nope("open_identity")

    def list_entities(self, path: str, layer: str | None = None) -> list:
        self._nope("list_entities")

    def get_entity(self, path: str, handle: str) -> dict:
        self._nope("get_entity")
