"""Entity discovery helpers. Visual description only for discovery; handles afterwards."""
from __future__ import annotations

import re

import ezdxf

from .backends.ezdxf_backend import FileCadBackend
from .errors import CadError, ENTITY_NOT_FOUND

_backend = FileCadBackend()


def find_entities(path: str, layer: str | None = None, etype: str | None = None,
                  block_name: str | None = None, text_regex: str | None = None,
                  bbox: list | None = None, limit: int = 500) -> list:
    refs = _backend.list_entities(path, layer=layer)
    rx = re.compile(text_regex) if text_regex else None
    out = []
    for r in refs:
        if etype and r["type"] != etype:
            continue
        if block_name and (r.get("block_name") or "") != block_name:
            continue
        if rx:
            hay = " ".join([str(r.get("text") or "")] + [f"{k}={v}" for k, v in (r.get("attributes") or {}).items()])
            if not rx.search(hay):
                continue
        if bbox:
            b = r["bbox"]
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            if not (bbox[0] <= cx <= bbox[2] and bbox[1] <= cy <= bbox[3]):
                continue
        out.append(r)
        if len(out) >= limit:
            break
    return out


def get_entity(path: str, handle: str) -> dict:
    return _backend.get_entity(path, handle)


def require_entity(path: str, handle: str, allowed_types: list | None = None) -> dict:
    ref = get_entity(path, handle)
    if allowed_types and ref["type"] not in allowed_types:
        raise CadError("ENTITY_TYPE_MISMATCH",
                       f"Handle {handle} is {ref['type']}, expected one of {allowed_types}.",
                       {"handle": handle, "actual": ref["type"]})
    return ref


def find_blocks(path: str, name_regex: str | None = None, bbox: list | None = None, limit: int = 500) -> list:
    refs = find_entities(path, etype="INSERT", bbox=bbox, limit=limit * 2)
    if name_regex:
        rx = re.compile(name_regex)
        refs = [r for r in refs if rx.search(r.get("block_name") or "")]
    return refs[:limit]


def room_entities(path: str, bbox: list) -> list:
    return find_entities(path, bbox=bbox, limit=5000)
