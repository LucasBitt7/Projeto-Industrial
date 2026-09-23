"""Wall helpers: detection, projection, move/place along wall (deterministic)."""
from __future__ import annotations

import math

import ezdxf

from . import geometry as G
from .drawing import assert_revision
from .entities import get_entity
from .errors import CadError
from .models import OperationResult
from .units import UnitContext

WALL_LAYERS_DEFAULT = ["ARQ", "ARQ-PAREDE", "PAREDE", "A-WALL", "ARCH", "WALL"]


def _wall_segments(doc, wall_layers: list) -> list:
    """Return wall segments as [{handle, p1, p2, length, layer}]. Walls = LINE/LWPOLYLINE on wall layers."""
    segs = []
    for e in doc.modelspace():
        try:
            if str(e.dxf.layer) not in wall_layers:
                continue
            t = e.dxftype()
            h = str(e.dxf.handle)
            if t == "LINE":
                p1 = (float(e.dxf.start.x), float(e.dxf.start.y))
                p2 = (float(e.dxf.end.x), float(e.dxf.end.y))
                segs.append({"handle": h, "p1": list(p1), "p2": list(p2),
                             "length": math.hypot(p2[0] - p1[0], p2[1] - p1[1]),
                             "layer": str(e.dxf.layer)})
            elif t == "LWPOLYLINE":
                pts = [(float(x), float(y)) for x, y, *_ in e.get_points()]
                for i in range(len(pts) - 1):
                    p1, p2 = pts[i], pts[i + 1]
                    segs.append({"handle": h, "p1": list(p1), "p2": list(p2),
                                 "length": math.hypot(p2[0] - p1[0], p2[1] - p1[1]),
                                 "layer": str(e.dxf.layer), "seg_index": i})
        except Exception:
            continue
    return segs


def find_walls(path: str, wall_layers: list | None = None, bbox: list | None = None) -> list:
    doc = ezdxf.readfile(path)
    segs = _wall_segments(doc, wall_layers or WALL_LAYERS_DEFAULT)
    if bbox:
        out = []
        for s in segs:
            mx, my = (s["p1"][0] + s["p2"][0]) / 2, (s["p1"][1] + s["p2"][1]) / 2
            if bbox[0] <= mx <= bbox[2] and bbox[1] <= my <= bbox[3]:
                out.append(s)
        return out
    return segs


def _move_insert_by_handle(doc, handle: str, dx: float, dy: float):
    found = False
    for e in doc.modelspace():
        try:
            if str(e.dxf.handle).upper() == handle.upper():
                t = e.dxftype()
                if t == "INSERT":
                    e.dxf.insert = (float(e.dxf.insert.x) + dx, float(e.dxf.insert.y) + dy)
                elif t == "TEXT":
                    e.dxf.insert = (float(e.dxf.insert.x) + dx, float(e.dxf.insert.y) + dy)
                elif t == "MTEXT":
                    e.dxf.insert = (float(e.dxf.insert.x) + dx, float(e.dxf.insert.y) + dy)
                elif t == "LINE":
                    e.dxf.start = (float(e.dxf.start.x) + dx, float(e.dxf.start.y) + dy)
                    e.dxf.end = (float(e.dxf.end.x) + dx, float(e.dxf.end.y) + dy)
                elif t == "CIRCLE":
                    e.dxf.center = (float(e.dxf.center.x) + dx, float(e.dxf.center.y) + dy)
                else:
                    # generic: try insert/center
                    if hasattr(e.dxf, "insert"):
                        e.dxf.insert = (float(e.dxf.insert.x) + dx, float(e.dxf.insert.y) + dy)
                    else:
                        raise CadError("ENTITY_TYPE_MISMATCH", f"Move not supported for {t}.",
                                       {"handle": handle, "type": t})
                found = True
                break
        except CadError:
            raise
        except Exception:
            continue
    if not found:
        raise CadError("ENTITY_NOT_FOUND", f"Handle {handle} not found for move.", {"handle": handle})
    return True


def move_along_wall(path: str, entity_handle: str, wall_handle: str, displacement: float,
                    unit: str = "mm", direction: int = +1, expected_revision: str | None = None,
                    wall_layers: list | None = None, dry_run: bool = False,
                    out_path: str | None = None) -> dict:
    """Deterministic move of entity anchor along wall vector. Returns OperationResult dict."""
    import uuid
    op_id = uuid.uuid4().hex[:12]
    ident = assert_revision(path, expected_revision)
    doc = ezdxf.readfile(path)
    try:
        insunits = int(doc.header.get("$INSUNITS", 0) or 0)
    except Exception:
        insunits = ident["insunits"] if isinstance(ident, dict) else ident.insunits
    from .config import resolve_unit_context  # config-driven fallback, never guessed
    units = resolve_unit_context(insunits if insunits else (ident["insunits"] if isinstance(ident, dict) else 0))
    dist_du = units.to_drawing_units(displacement, unit) * (1 if direction >= 0 else -1)

    ref = get_entity(path, entity_handle)
    if not ref.get("insertion_point"):
        raise CadError("ENTITY_TYPE_MISMATCH", f"Entity {entity_handle} has no insertion point.",
                       {"handle": entity_handle})
    # resolve wall segment: prefer exact handle match
    segs = _wall_segments(doc, wall_layers or WALL_LAYERS_DEFAULT)
    w = next((s for s in segs if s["handle"].upper() == wall_handle.upper()), None)
    if w is None:
        raise CadError("WALL_NOT_FOUND", f"Wall handle {wall_handle} not found on wall layers.",
                       {"wall_handle": wall_handle})
    import math as _m
    L = w["length"] or 1e-9
    ux, uy = (w["p2"][0] - w["p1"][0]) / L, (w["p2"][1] - w["p1"][1]) / L
    sx, sy = ref["insertion_point"]
    # project anchor onto wall then advance along wall
    proj = G.nearest_point_on_wall(sx, sy, tuple(w["p1"]), tuple(w["p2"]))
    # advance from projection (robust even if entity slightly off wall)
    tx, ty = proj["x"] + ux * dist_du, proj["y"] + uy * dist_du
    # clamp check: must remain on segment (within tolerance)
    t_new = ((tx - w["p1"][0]) * ux + (ty - w["p1"][1]) * uy) / L + 0.0
    # recompute t properly: projection of target
    t_new = ((tx - w["p1"][0]) * (w["p2"][0] - w["p1"][0]) + (ty - w["p1"][1]) * (w["p2"][1] - w["p1"][1])) / (L * L)
    if not (-1e-6 <= t_new <= 1 + 1e-6):
        raise CadError("OUT_OF_SCOPE", f"Move would leave wall segment (t={t_new:.3f}).",
                       {"t": t_new})
    dx, dy = tx - sx, ty - sy
    expected = {"from": [sx, sy], "to": [tx, ty], "displacement_drawing_units": dist_du}
    before = ident if isinstance(ident, dict) else ident.to_dict()
    if dry_run:
        return OperationResult(ok=True, operation_id=op_id, drawing_before=before,
                               drawing_after=before, modified_handles=[entity_handle.upper()],
                               expected_state=expected, actual_state=expected,
                               validations=[{"check": "dry_run", "ok": True}]).to_dict()
    _move_insert_by_handle(doc, entity_handle, dx, dy)
    target = out_path or path
    doc.saveas(target)
    # READBACK
    from .drawing import drawing_identity as _ident
    after = _ident(target).to_dict()
    rb = get_entity(target, entity_handle)
    ax, ay = rb["insertion_point"]
    tol = 1e-4
    ok = abs(ax - tx) <= tol and abs(ay - ty) <= tol
    if not ok:
        raise CadError("READBACK_FAIL", f"Readback mismatch: expected {(tx, ty)}, got {(ax, ay)}.",
                       {"expected": [tx, ty], "actual": [ax, ay]})
    return OperationResult(ok=True, operation_id=op_id, drawing_before=before, drawing_after=after,
                           modified_handles=[entity_handle.upper()],
                           expected_state=expected, actual_state={"at": [ax, ay]},
                           validations=[{"check": "readback_position", "ok": True}]).to_dict()
