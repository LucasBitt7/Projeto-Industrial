"""File backend over ezdxf. Operates on explicit DXF paths only."""
from __future__ import annotations

import hashlib
import os

import ezdxf

from ..errors import CadError, DRAWING_NOT_FOUND, ENTITY_NOT_FOUND
from .base import CadBackend


def _entity_bbox(doc, e) -> list:
    try:
        from ezdxf import bbox as _bbox
        ext = _bbox.extents([e])
        if ext.has_data:
            return [float(ext.extmin.x), float(ext.extmin.y), float(ext.extmax.x), float(ext.extmax.y)]
    except Exception:
        pass
    # fallback per type
    try:
        t = e.dxftype()
        if t == "INSERT":
            x, y = float(e.dxf.insert.x), float(e.dxf.insert.y)
            return [x, y, x, y]
        if t in ("TEXT", "MTEXT"):
            p = e.dxf.insert if t == "TEXT" else e.dxf.insert
            x, y = float(p.x), float(p.y)
            return [x, y, x, y]
        if t == "LINE":
            xs = [float(e.dxf.start.x), float(e.dxf.end.x)]
            ys = [float(e.dxf.start.y), float(e.dxf.end.y)]
            return [min(xs), min(ys), max(xs), max(ys)]
        if t == "CIRCLE":
            x, y, r = float(e.dxf.center.x), float(e.dxf.center.y), float(e.dxf.radius)
            return [x - r, y - r, x + r, y + r]
        if t == "LWPOLYLINE":
            pts = [(float(x), float(y)) for x, y, *_ in e.get_points()]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            return [min(xs), min(ys), max(xs), max(ys)]
        if t == "HATCH":
            xs, ys = [], []
            try:
                for path in e.paths:
                    try:
                        cname = type(path).__name__
                        verts = getattr(path, "vertices", None)
                        if "Polyline" in cname and verts:
                            for v in verts:
                                xs.append(float(v[0])); ys.append(float(v[1]))
                        elif "Edge" in cname:
                            for edge in getattr(path, "edges", []):
                                et = getattr(edge, "EDGE_TYPE", "")
                                if et == "LineEdge":
                                    xs += [float(edge.start.x), float(edge.end.x)]
                                    ys += [float(edge.start.y), float(edge.end.y)]
                                elif et == "ArcEdge":
                                    cx, cy, r = float(edge.center.x), float(edge.center.y), float(edge.radius)
                                    xs += [cx - r, cx + r]; ys += [cy - r, cy + r]
                    except Exception:
                        continue
            except Exception:
                pass
            if xs and ys:
                return [min(xs), min(ys), max(xs), max(ys)]
    except Exception:
        pass
    return [0.0, 0.0, 0.0, 0.0]


def entity_to_ref(doc, e) -> dict:
    t = e.dxftype()
    layer = str(e.dxf.layer) if hasattr(e.dxf, "layer") else "0"
    handle = str(e.dxf.handle)
    ins, rot, blk, attrs, text = None, 0.0, None, {}, None
    try:
        if t == "INSERT":
            ins = [float(e.dxf.insert.x), float(e.dxf.insert.y)]
            rot = float(getattr(e.dxf, "rotation", 0.0) or 0.0)
            blk = str(e.dxf.name)
            for a in getattr(e, "attribs", []):
                try:
                    attrs[str(a.dxf.tag)] = str(a.dxf.text)
                except Exception:
                    pass
        elif t == "TEXT":
            ins = [float(e.dxf.insert.x), float(e.dxf.insert.y)]
            rot = float(getattr(e.dxf, "rotation", 0.0) or 0.0)
            text = str(e.dxf.text)
        elif t == "MTEXT":
            ins = [float(e.dxf.insert.x), float(e.dxf.insert.y)]
            rot = float(getattr(e.dxf, "rotation", 0.0) or 0.0)
            text = str(e.text)[:500]
    except Exception:
        pass
    return {"handle": handle, "type": t, "layer": layer, "bbox": _entity_bbox(doc, e),
            "insertion_point": ins, "rotation": rot, "block_name": blk,
            "attributes": attrs, "text": text}


class FileCadBackend(CadBackend):
    name = "file"

    def _load(self, path: str):
        if not os.path.isfile(path):
            raise CadError(DRAWING_NOT_FOUND, f"Drawing not found: {path}", {"path": path})
        try:
            return ezdxf.readfile(path)
        except Exception as ex:
            raise CadError(DRAWING_NOT_FOUND, f"Cannot read DXF: {path}: {ex}", {"path": path})

    def open_identity(self, path: str) -> dict:
        from ..drawing import drawing_identity
        return drawing_identity(path).to_dict()

    def list_entities(self, path: str, layer: str | None = None) -> list:
        doc = self._load(path)
        out = []
        for e in doc.modelspace():
            try:
                if layer and str(e.dxf.layer) != layer:
                    continue
                out.append(entity_to_ref(doc, e))
            except Exception:
                continue
        return out

    def get_entity(self, path: str, handle: str) -> dict:
        doc = self._load(path)
        try:
            e = doc.entitydb.get(handle.upper())
        except Exception:
            e = None
        if e is None:
            # fallback linear scan
            for cand in doc.modelspace():
                try:
                    if str(cand.dxf.handle).upper() == handle.upper():
                        e = cand
                        break
                except Exception:
                    continue
        if e is None:
            raise CadError(ENTITY_NOT_FOUND, f"Entity handle {handle} not found in {path}",
                           {"handle": handle, "path": path})
        return entity_to_ref(doc, e)
