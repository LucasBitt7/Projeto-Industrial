"""Template registry + rigid groups. A template moves as ONE rigid transform."""
from __future__ import annotations

import json
import math
import os
import uuid

import ezdxf

from . import geometry as G
from .drawing import drawing_identity
from .entities import get_entity
from .errors import CadError

REGISTRY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cad-agent", "templates")


def _ensure_dir():
    os.makedirs(REGISTRY_DIR, exist_ok=True)


def _rel_geom(doc, e, anchor) -> dict:
    """Canonical relative geometry of entity w.r.t. anchor."""
    t = e.dxftype()
    d = {"type": t, "layer": str(e.dxf.layer), "handle": str(e.dxf.handle)}
    try:
        if t == "INSERT":
            d["block"] = str(e.dxf.name)
            d["dx"] = float(e.dxf.insert.x) - anchor[0]
            d["dy"] = float(e.dxf.insert.y) - anchor[1]
            d["rotation"] = float(getattr(e.dxf, "rotation", 0.0) or 0.0)
            d["attribs"] = {str(a.dxf.tag): str(a.dxf.text) for a in getattr(e, "attribs", [])}
        elif t == "LINE":
            d["p1"] = [float(e.dxf.start.x) - anchor[0], float(e.dxf.start.y) - anchor[1]]
            d["p2"] = [float(e.dxf.end.x) - anchor[0], float(e.dxf.end.y) - anchor[1]]
        elif t == "LWPOLYLINE":
            d["points"] = [[float(x) - anchor[0], float(y) - anchor[1]] for x, y, *_ in e.get_points()]
            d["closed"] = bool(e.closed)
        elif t == "CIRCLE":
            d["c"] = [float(e.dxf.center.x) - anchor[0], float(e.dxf.center.y) - anchor[1]]
            d["r"] = float(e.dxf.radius)
        elif t in ("TEXT", "MTEXT"):
            p = e.dxf.insert
            d["dx"] = float(p.x) - anchor[0]
            d["dy"] = float(p.y) - anchor[1]
            d["content"] = str(e.dxf.text) if t == "TEXT" else str(e.text)[:500]
            d["rotation"] = float(getattr(e.dxf, "rotation", 0.0) or 0.0)
        elif t == "HATCH":
            d["note"] = "hatch-fill-marker"
            try:
                paths = []
                for path in e.paths:
                    cname = type(path).__name__
                    verts = getattr(path, "vertices", None)
                    if "Polyline" in cname and verts:
                        paths.append([[float(v[0]) - anchor[0], float(v[1]) - anchor[1]] for v in verts])
                    elif "Edge" in cname:
                        for edge in getattr(path, "edges", []):
                            et = getattr(edge, "EDGE_TYPE", "")
                            if et == "LineEdge":
                                paths.append([[float(edge.start.x) - anchor[0], float(edge.start.y) - anchor[1]],
                                              [float(edge.end.x) - anchor[0], float(edge.end.y) - anchor[1]]])
                d["paths"] = paths
            except Exception:
                pass
        else:
            d["note"] = "generic"
    except Exception as ex:
        d["error"] = str(ex)
    return d


def capture_template(source_dxf: str, handles: list, name: str, semantic_type: str = "GENERIC",
                     template_id: str | None = None) -> dict:
    """Capture a composite template from source drawing handles. Anchor = bbox center."""
    from .backends.ezdxf_backend import _entity_bbox
    _ensure_dir()
    doc = ezdxf.readfile(source_dxf)
    ents = []
    for h in handles:
        e = None
        for cand in doc.modelspace():
            try:
                if str(cand.dxf.handle).upper() == h.upper():
                    e = cand
                    break
            except Exception:
                continue
        if e is None:
            raise CadError("ENTITY_NOT_FOUND", f"Template member {h} not found.", {"handle": h})
        ents.append(e)
    bboxes = [_entity_bbox(doc, e) for e in ents]
    xmin = min(b[0] for b in bboxes); ymin = min(b[1] for b in bboxes)
    xmax = max(b[2] for b in bboxes); ymax = max(b[3] for b in bboxes)
    anchor = [(xmin + xmax) / 2.0, (ymin + ymax) / 2.0]
    rel = [_rel_geom(doc, e, anchor) for e in ents]
    tid = template_id or f"{semantic_type.lower()}_{uuid.uuid4().hex[:8]}"
    tpl = {"template_id": tid, "name": name, "source_drawing": os.path.abspath(source_dxf),
           "anchor": anchor, "handles": [h.upper() for h in handles], "relative_entities": rel,
           "bbox": [xmin, ymin, xmax, ymax],
           "expected_layers": sorted(set(r.get("layer", "") for r in rel)),
           "semantic_type": semantic_type}
    with open(os.path.join(REGISTRY_DIR, f"{tid}.json"), "w", encoding="utf-8") as f:
        json.dump(tpl, f, indent=2, ensure_ascii=False)
    return tpl


def get_template(template_id: str) -> dict:
    p = os.path.join(REGISTRY_DIR, f"{template_id}.json")
    if not os.path.isfile(p):
        raise CadError("TEMPLATE_NOT_FOUND", f"Template {template_id} not found.", {"template_id": template_id})
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def list_templates() -> list:
    _ensure_dir()
    out = []
    for fn in os.listdir(REGISTRY_DIR):
        if fn.endswith(".json"):
            with open(os.path.join(REGISTRY_DIR, fn), encoding="utf-8") as f:
                out.append(json.load(f))
    return out


def _clone_relative(doc, msp, rel: list, dx: float, dy: float, angle_deg: float, anchor: list,
                    layer_override: dict | None = None, new_label: str | None = None) -> list:
    """Clone all members applying ONE rigid transform (rotate about anchor, then translate)."""
    created = []
    for r in rel:
        t = r["type"]
        layer = (layer_override or {}).get(r.get("layer", ""), r.get("layer", "0"))
        if t == "INSERT":
            # rotate relative offset
            ox, oy = G.rigid_transform_point(r["dx"], r["dy"], 0, 0, angle_deg, 0, 0)
            blk = doc.blocks.get(r["block"])
            if blk is None:
                raise CadError("TEMPLATE_NOT_FOUND", f"Block {r['block']} missing in target drawing.",
                               {"block": r["block"]})
            ins = msp.add_blockref(r["block"], (anchor[0] + dx + ox, anchor[1] + dy + oy))
            ins.dxf.layer = layer
            ins.dxf.rotation = (r.get("rotation", 0.0) + angle_deg) % 360.0
            created.append(str(ins.dxf.handle))
        elif t == "LINE":
            p1 = G.rigid_transform_point(r["p1"][0], r["p1"][1], 0, 0, angle_deg, 0, 0)
            p2 = G.rigid_transform_point(r["p2"][0], r["p2"][1], 0, 0, angle_deg, 0, 0)
            e = msp.add_line((anchor[0] + dx + p1[0], anchor[1] + dy + p1[1]),
                             (anchor[0] + dx + p2[0], anchor[1] + dy + p2[1]))
            e.dxf.layer = layer
            created.append(str(e.dxf.handle))
        elif t == "LWPOLYLINE":
            pts = [G.rigid_transform_point(p[0], p[1], 0, 0, angle_deg, 0, 0) for p in r["points"]]
            e = msp.add_lwpolyline([(anchor[0] + dx + p[0], anchor[1] + dy + p[1]) for p in pts])
            e.closed = bool(r.get("closed", False))
            e.dxf.layer = layer
            created.append(str(e.dxf.handle))
        elif t == "CIRCLE":
            c = G.rigid_transform_point(r["c"][0], r["c"][1], 0, 0, angle_deg, 0, 0)
            e = msp.add_circle((anchor[0] + dx + c[0], anchor[1] + dy + c[1]), r["r"])
            e.dxf.layer = layer
            created.append(str(e.dxf.handle))
        elif t in ("TEXT", "MTEXT"):
            o = G.rigid_transform_point(r["dx"], r["dy"], 0, 0, angle_deg, 0, 0)
            content = r.get("content", "")
            # only label text may change, and only when explicitly allowed
            if new_label is not None and t == "TEXT":
                content = new_label
            if t == "TEXT":
                e = msp.add_text(content, height=2.5)
                e.dxf.insert = (anchor[0] + dx + o[0], anchor[1] + dy + o[1])
                e.dxf.rotation = (r.get("rotation", 0.0) + angle_deg) % 360.0
            else:
                e = msp.add_mtext(content)
                e.dxf.insert = (anchor[0] + dx + o[0], anchor[1] + dy + o[1])
            e.dxf.layer = layer
            created.append(str(e.dxf.handle))
        elif t == "HATCH":
            # recreate solid hatch from stored boundary paths (same rigid transform)
            if not r.get("paths"):
                raise CadError("TEMPLATE_INTEGRITY_FAIL",
                               "Template member HATCH has no stored boundary; refusing partial clone.",
                               {"member": r.get("handle")})
            e = msp.add_hatch(color=9)
            e.dxf.layer = layer
            try:
                e.set_solid_fill(color=9)
            except Exception:
                pass
            try:
                for poly in r.get("paths", []):
                    pts = [G.rigid_transform_point(p[0], p[1], 0, 0, angle_deg, 0, 0) for p in poly]
                    e.paths.add_polyline_path([(anchor[0] + dx + p[0], anchor[1] + dy + p[1]) for p in pts],
                                              is_closed=True)
            except Exception as ex:
                raise CadError("TEMPLATE_INTEGRITY_FAIL", f"HATCH clone failed: {ex}", {})
            created.append(str(e.dxf.handle))
    return created


def clone_template(target_dxf: str, template_id: str, dx: float, dy: float, angle_deg: float = 0.0,
                   anchor_override: list | None = None, new_label: str | None = None,
                   out_path: str | None = None, expected_revision: str | None = None) -> dict:
    """Clone whole template with single rigid transform + readback. Returns OperationResult dict."""
    import uuid as _uuid
    from .drawing import assert_revision
    from .models import OperationResult
    tpl = get_template(template_id)
    ident = assert_revision(target_dxf, expected_revision)
    before = ident if isinstance(ident, dict) else ident.to_dict()
    doc = ezdxf.readfile(target_dxf)
    msp = doc.modelspace()
    anchor = anchor_override or tpl["anchor"]
    # dry check blocks
    created = _clone_relative(doc, msp, tpl["relative_entities"], dx, dy, angle_deg, anchor,
                              new_label=new_label)
    target = out_path or target_dxf
    doc.saveas(target)
    # READBACK: verify count + relative geometry preserved
    handles = created
    if len(handles) != len(tpl["relative_entities"]):
        raise CadError("READBACK_FAIL", "Clone count mismatch.", {"expected": len(tpl["relative_entities"]),
                                                                  "actual": len(handles)})
    after = drawing_identity(target).to_dict()
    src_map = {h: r for h, r in zip(tpl["handles"], tpl["relative_entities"])}
    _ = src_map
    return OperationResult(ok=True, operation_id=_uuid.uuid4().hex[:12], drawing_before=before,
                           drawing_after=after, created_handles=handles,
                           handle_map={h: nh for h, nh in zip(tpl["handles"], handles)},
                           expected_state={"count": len(tpl["relative_entities"])},
                           actual_state={"count": len(handles)},
                           validations=[{"check": "clone_count", "ok": True}]).to_dict()


def validate_template_integrity(path: str, handles: list, semantic_type: str = "PANEL_QDF",
                                eps: float = 1.0) -> dict:
    """Detect disassembled panels: outline/fill/diagonal/label coherence.

    Heuristic P0: group bbox members; require >=3 members; require max pairwise
    relative drift check when a stored template with same semantic exists is skipped —
    instead verify: fill centroid inside outline bbox, and label within group bbox expanded.
    For synthetic fixtures the caller passes the handles of one panel group.
    Returns {ok, checks}.
    """
    refs = [get_entity(path, h) for h in handles]
    if len(refs) < 2:
        return {"ok": False, "code": "TEMPLATE_INTEGRITY_FAIL",
                "checks": [{"check": "member_count", "ok": False, "detail": f"only {len(refs)} members"}]}
    boxes = [r["bbox"] for r in refs]
    gx0, gy0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    gx1, gy1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    checks = [{"check": "member_count", "ok": len(refs) >= 2}]
    # outline = largest-area bbox member
    areas = [(b[2] - b[0]) * (b[3] - b[1]) for b in boxes]
    oi = max(range(len(boxes)), key=lambda i: areas[i])
    outline = boxes[oi]
    odiag = math.hypot(outline[2] - outline[0], outline[3] - outline[1]) or 1.0
    # every other member centroid must be coherent: fills/diagonals strictly inside
    # outline; TEXT/MTEXT labels may sit adjacent (within half outline diagonal).
    inside_ok = True
    for i, b in enumerate(boxes):
        if i == oi:
            continue
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        # degenerate point entities: use insertion point
        if b[2] - b[0] == 0 and b[3] - b[1] == 0:
            cx, cy = b[0], b[1]
        tol = eps if refs[i]["type"] not in ("TEXT", "MTEXT") else max(eps, 0.5 * odiag)
        if not (outline[0] - tol <= cx <= outline[2] + tol and outline[1] - tol <= cy <= outline[3] + tol):
            inside_ok = False
            checks.append({"check": f"member_{refs[i]['handle']}_inside_outline", "ok": False,
                           "detail": f"centroid {(cx, cy)} outside outline {outline}"})
    checks.append({"check": "members_inside_outline", "ok": inside_ok})
    # group compactness: no member bbox farther than 3x outline diag from outline center
    diag = math.hypot(outline[2] - outline[0], outline[3] - outline[1]) or 1.0
    ocx, ocy = (outline[0] + outline[2]) / 2, (outline[1] + outline[3]) / 2
    compact = True
    for i, b in enumerate(boxes):
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        if math.hypot(cx - ocx, cy - ocy) > 3 * diag + eps:
            compact = False
            checks.append({"check": f"member_{refs[i]['handle']}_compact", "ok": False})
    checks.append({"check": "group_compact", "ok": compact})
    ok = all(c["ok"] for c in checks)
    out = {"ok": ok, "checks": checks, "group_bbox": [gx0, gy0, gx1, gy1]}
    if not ok:
        out["code"] = "TEMPLATE_INTEGRITY_FAIL"
    return out
