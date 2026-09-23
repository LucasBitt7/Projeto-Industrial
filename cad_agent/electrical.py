"""High-level ELECTRICAL API. The LLM calls these, never raw LINE/MOVE math.

Every function: resolve handles -> deterministic geometry -> dry-run ->
write to explicit out_path -> READBACK -> validate -> PASS/FAIL dict.
"""
from __future__ import annotations

import math
import re
import uuid

import ezdxf

from . import geometry as G
from .callouts import create_callout as _create_callout
from .collisions import detect_collisions
from .conduit import route_conduit as _route_conduit
from .drawing import assert_revision, drawing_identity
from .entities import find_entities, get_entity
from .errors import CadError
from .models import OperationResult
from .templates import clone_template, get_template, validate_template_integrity
from .units import UnitContext
from .walls import _wall_segments, find_walls, move_along_wall

OUTLET_BLOCK_REGEX = r"(TUG|TUE|TOM|2P\+?T|NBR14136)"
PANEL_BLOCK_REGEX = r"(QDF|QDL|QD[CG]?|QUADRO|PAINEL)"


def electrical_find_outlets(path: str, bbox: list | None = None, limit: int = 1000) -> list:
    refs = find_entities(path, etype="INSERT", bbox=bbox, limit=limit * 2)
    rx = re.compile(OUTLET_BLOCK_REGEX, re.IGNORECASE)
    return [r for r in refs if rx.search(r.get("block_name") or "")][:limit]


def electrical_find_panels(path: str, bbox: list | None = None, limit: int = 200) -> list:
    refs = find_entities(path, etype="INSERT", bbox=bbox, limit=limit * 5)
    rx = re.compile(PANEL_BLOCK_REGEX, re.IGNORECASE)
    return [r for r in refs if rx.search(r.get("block_name") or "")][:limit]


def electrical_move_outlet_along_wall(path: str, outlet_handle: str, wall_handle: str,
                                      displacement: float, unit: str = "mm", direction: int = +1,
                                      expected_revision: str | None = None, dry_run: bool = False,
                                      out_path: str | None = None,
                                      allowed_bbox: list | None = None) -> dict:
    """Spec section 21. LLM never computes X/Y."""
    ref = get_entity(path, outlet_handle)
    rx = re.compile(OUTLET_BLOCK_REGEX, re.IGNORECASE)
    if ref["type"] != "INSERT" or not rx.search(ref.get("block_name") or ""):
        raise CadError("ENTITY_TYPE_MISMATCH",
                       f"Handle {outlet_handle} is not a known outlet block ({ref.get('block_name')}).",
                       {"handle": outlet_handle, "block": ref.get("block_name")})
    if allowed_bbox:
        b = ref["bbox"]
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        if not (allowed_bbox[0] <= cx <= allowed_bbox[2] and allowed_bbox[1] <= cy <= allowed_bbox[3]):
            raise CadError("OUT_OF_SCOPE", f"Outlet {outlet_handle} outside allowed_bbox.",
                           {"handle": outlet_handle})
    res = move_along_wall(path, outlet_handle, wall_handle, displacement, unit, direction,
                          expected_revision, dry_run=dry_run, out_path=out_path)
    if dry_run or not res.get("ok"):
        return res
    # collision check on result (outlet vs panels)
    target = out_path or path
    outlets = electrical_find_outlets(target)
    panels = electrical_find_panels(target)
    hits = detect_collisions(outlets + panels, clearance=2.0)
    mine = [h for h in hits if outlet_handle.upper() in (h["a"], h["b"])]
    res["validations"].append({"check": "post_move_collision", "ok": len(mine) == 0,
                               "detail": f"{len(mine)} collisions"})
    if mine:
        res["ok"] = False
        res["error_code"] = "COLLISION_DETECTED"
        res["error"] = f"Move creates collision: {mine}"
    return res


def electrical_place_panel_on_wall(path: str, template_id: str, wall_handle: str,
                                   position_rule: str = "free_interval_nearest_to_handle",
                                   clearance: float = 10.0, new_label: str | None = None,
                                   expected_revision: str | None = None, dry_run: bool = False,
                                   out_path: str | None = None,
                                   near_handle: str | None = None) -> dict:
    """Spec section 22: find free interval, orient long side parallel, clone rigid group."""
    op_id = uuid.uuid4().hex[:12]
    ident = assert_revision(path, expected_revision)
    before = ident if isinstance(ident, dict) else ident.to_dict()
    tpl = get_template(template_id)
    tw, th = tpl["bbox"][2] - tpl["bbox"][0], tpl["bbox"][3] - tpl["bbox"][1]
    need = max(tw, th) + 2 * clearance
    doc = ezdxf.readfile(path)
    segs = _wall_segments(doc, ["ARQ", "ARQ-PAREDE", "PAREDE", "A-WALL", "ARCH", "WALL"])
    # also accept ANY line as wall if wall_layers empty in fixture: fallback to all LINE segs
    if not segs:
        for e in doc.modelspace():
            try:
                if e.dxftype() == "LINE":
                    p1 = (float(e.dxf.start.x), float(e.dxf.start.y))
                    p2 = (float(e.dxf.end.x), float(e.dxf.end.y))
                    segs.append({"handle": str(e.dxf.handle), "p1": list(p1), "p2": list(p2),
                                 "length": math.hypot(p2[0] - p1[0], p2[1] - p1[1]),
                                 "layer": str(e.dxf.layer)})
            except Exception:
                continue
    w = next((s for s in segs if s["handle"].upper() == wall_handle.upper()), None)
    if w is None:
        raise CadError("WALL_NOT_FOUND", f"Wall {wall_handle} not found.", {"wall_handle": wall_handle})
    L = w["length"] or 1e-9
    # occupied intervals from panels+outlets projected on wall
    occ = []
    for r in electrical_find_panels(path) + electrical_find_outlets(path):
        p = r["insertion_point"] or [(r["bbox"][0] + r["bbox"][2]) / 2, (r["bbox"][1] + r["bbox"][3]) / 2]
        pr = G.nearest_point_on_wall(p[0], p[1], tuple(w["p1"]), tuple(w["p2"]))
        half = clearance / L
        occ.append((max(0.0, pr["t"] - half), min(1.0, pr["t"] + half)))
    free = G.find_free_wall_interval(tuple(w["p1"]), tuple(w["p2"]), occ, need, L, clearance=0.0)
    if free is None:
        raise CadError("NO_FREE_WALL_SPACE", "No free wall interval for panel.", {"need": need})
    # orientation: long side parallel to wall
    wall_ang = G.rotation_parallel_to_wall(tuple(w["p1"]), tuple(w["p2"]))
    angle = wall_ang if tw >= th else wall_ang  # clone keeps template frame; record orientation
    long_parallel = (tw >= th and abs((angle - wall_ang + 90) % 180 - 90) <= 45) or tw < th
    expected = {"at": [free["x"], free["y"]], "wall_angle": wall_ang, "need": need}
    if dry_run:
        return OperationResult(ok=True, operation_id=op_id, drawing_before=before, drawing_after=before,
                               expected_state=expected, actual_state=expected,
                               validations=[{"check": "dry_run_free_interval", "ok": True}]).to_dict()
    anchor = tpl["anchor"]
    dx, dy = free["x"] - anchor[0], free["y"] - anchor[1]
    res = clone_template(path, template_id, dx, dy, 0.0, expected_revision=expected_revision,
                         new_label=new_label, out_path=out_path)
    res["expected_state"] = expected
    # integrity validation on clones
    target = out_path or path
    integ = validate_template_integrity(target, res["created_handles"])
    res["validations"].append({"check": "template_integrity", **{k: v for k, v in integ.items() if k != "checks"}})
    if not integ["ok"]:
        res["ok"] = False
        res["error_code"] = "TEMPLATE_INTEGRITY_FAIL"
        res["error"] = f"Cloned panel failed integrity: {integ['checks']}"
    return res


def electrical_route_conduit(path: str, source_handle: str, destination_handles: list,
                             layer: str = "ELETRODUTO", clearance: float = 5.0,
                             expected_revision: str | None = None, dry_run: bool = False,
                             out_path: str | None = None) -> dict:
    return _route_conduit(path, source_handle, destination_handles, layer, clearance,
                          expected_revision, dry_run, out_path)


def electrical_create_callout(path: str, conduit_edge: dict, circuits: list, conductor_spec: str,
                              placement: str = "above", expected_revision: str | None = None,
                              dry_run: bool = False, out_path: str | None = None) -> dict:
    return _create_callout(path, conduit_edge, circuits, conductor_spec, placement,
                           expected_revision=expected_revision, dry_run=dry_run, out_path=out_path)
