"""Drawing identity, revision tokens, geometric fingerprints."""
from __future__ import annotations

import hashlib
import json
import os

import ezdxf

from .errors import CadError, DRAWING_NOT_FOUND
from .models import DrawingIdentity


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_entity(e) -> dict:
    """Canonical subset used for fingerprints/hashes."""
    try:
        t = e.dxftype()
    except Exception:
        return {}
    d: dict = {"type": t}
    try:
        dxf = e.dxf
        if hasattr(dxf, "layer"):
            d["layer"] = str(dxf.layer)
        if hasattr(dxf, "handle"):
            d["handle"] = str(dxf.handle).upper()
        for attr in ("insert", "center", "start", "end"):
            if hasattr(dxf, attr):
                try:
                    v = getattr(dxf, attr)
                    d[attr] = [round(float(v.x), 6), round(float(v.y), 6)]
                except Exception:
                    pass
        for attr in ("rotation", "radius", "text", "name"):
            if hasattr(dxf, attr):
                try:
                    v = getattr(dxf, attr)
                    d[attr] = round(float(v), 6) if isinstance(v, (int, float)) else str(v)
                except Exception:
                    pass
        if t == "LWPOLYLINE":
            try:
                d["points"] = [[round(float(x), 6), round(float(y), 6)] for x, y, *_ in e.get_points()]
            except Exception:
                pass
        if t == "INSERT":
            try:
                d["attribs"] = {str(a.dxf.tag): str(a.dxf.text) for a in getattr(e, "attribs", [])}
            except Exception:
                pass
        if t in ("TEXT", "MTEXT"):
            try:
                d["content"] = str(e.dxf.text) if t == "TEXT" else str(e.text)
            except Exception:
                pass
    except Exception:
        pass
    return d


def drawing_fingerprint(path: str) -> dict:
    """Read drawing from disk and return canonical fingerprint + revision token."""
    if not os.path.isfile(path):
        raise CadError(DRAWING_NOT_FOUND, f"Drawing not found: {path}", {"path": path})
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    canon = []
    for e in msp:
        try:
            canon.append(_canonical_entity(e))
        except Exception:
            continue
    canon.sort(key=lambda d: (d.get("type", ""), d.get("handle", "")))
    raw = json.dumps(canon, sort_keys=True, ensure_ascii=False)
    token = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return {"entities": canon, "revision_token": token, "entity_count": len(canon)}


def entity_fingerprint(ent: dict) -> str:
    raw = json.dumps(ent, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def scope_fingerprint(entities: list) -> str:
    canon = sorted([json.dumps(e, sort_keys=True) for e in entities])
    return hashlib.sha256("\n".join(canon).encode("utf-8")).hexdigest()


def drawing_identity(path: str) -> DrawingIdentity:
    apath = os.path.abspath(path)
    if not os.path.isfile(apath):
        raise CadError(DRAWING_NOT_FOUND, f"Drawing not found: {apath}", {"path": path})
    st = os.stat(apath)
    fsha = sha256_file(apath)
    doc = ezdxf.readfile(apath)
    try:
        insunits = int(doc.header.get("$INSUNITS", 0) or 0)
    except Exception:
        insunits = 0
    try:
        from ezdxf import bbox as _bbox
        ext = _bbox.extents(doc.modelspace())
        extents = [float(ext.extmin.x), float(ext.extmin.y), float(ext.extmax.x), float(ext.extmax.y)] \
            if ext.has_data else [0, 0, 0, 0]
    except Exception:
        extents = [0, 0, 0, 0]
    try:
        count = len(list(doc.modelspace()))
    except Exception:
        count = 0
    fp = drawing_fingerprint(apath)
    return DrawingIdentity(
        absolute_path=apath, basename=os.path.basename(apath), sha256=fsha,
        size_bytes=st.st_size, mtime=st.st_mtime, insunits=insunits,
        extents=extents, entity_count=count, revision_token=fp["revision_token"],
    )


def assert_revision(path: str, expected_revision: str | None):
    """Refuse to write when the drawing changed since inspection."""
    if not expected_revision:
        return drawing_identity(path)
    ident = drawing_identity(path)
    if ident.revision_token != expected_revision:
        raise CadError("DRAWING_REVISION_MISMATCH",
                       f"Drawing changed since inspection. expected={expected_revision[:12]}… "
                       f"actual={ident.revision_token[:12]}…. Re-inspect before writing.",
                       {"expected": expected_revision, "actual": ident.revision_token,
                        "path": ident.absolute_path})
    return ident
