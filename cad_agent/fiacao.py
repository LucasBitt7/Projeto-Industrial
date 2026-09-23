"""FIACAO callouts bound to conduit edges + guarded deletes.

Covers the capability gap documented by executor FAILs:
- clone_template drops INSERT attributes (C/B) and visual overrides.
- create_callout builds ELE-CALLOUT leader+MTEXT, not the drawing-native
  FIACAO_LAMP_FNT INSERT pattern (INSERT on _ELT_ELETRODUTOS, attribs on
  ELET_FIAÇÃO, color 4/ciano, Continuous, textstyle6, h0.08, rot0).
- No delete op exists in the high-level surface.

All writes are revision-gated, dry_run-first, never in place (out_path
required and must differ from path), identity-checked, readback-verified.
"""
from __future__ import annotations

import math
import uuid

import ezdxf

from .drawing import assert_revision, drawing_identity
from .errors import CadError
from .models import OperationResult


def _insertion_point(ent) -> tuple:
    try:
        ins = ent.dxf.insert
        return (float(ins[0]), float(ins[1]))
    except Exception:
        return (0.0, 0.0)


def _entity_bbox(doc, ent) -> list:
    from ezdxf.bbox import extents
    box = extents([ent])
    return [box.extmin.x, box.extmin.y, box.extmax.x, box.extmax.y]


def delete_entities_guarded(path: str, handles: list, identity: dict | None = None,
                            expected_count: int | None = None,
                            expected_revision: str | None = None, dry_run: bool = False,
                            out_path: str | None = None) -> dict:
    """Delete ONLY listed handles after identity check. Never in place."""
    op_id = uuid.uuid4().hex[:12]
    if not handles:
        raise CadError("DELETE_GUARD", "Refusing delete of empty handle list.", {})
    if not out_path or out_path == path:
        raise CadError("DELETE_GUARD", "Delete requires a distinct out_path (never in place).",
                       {"out_path": out_path})
    ident = assert_revision(path, expected_revision)
    before = ident if isinstance(ident, dict) else ident.to_dict()
    if expected_count is not None and len(handles) != expected_count:
        raise CadError("DELETE_GUARD",
                       f"Handle count {len(handles)} != expected {expected_count}.",
                       {"handles": handles})
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    checked = []
    for h in handles:
        try:
            ent = doc.entitydb[h]
        except KeyError:
            raise CadError("ENTITY_NOT_FOUND", f"Handle {h} not found.", {"handle": h})
        info = {"handle": h, "type": ent.dxftype(), "layer": ent.dxf.layer,
                "bbox": _entity_bbox(doc, ent)}
        if ent.dxftype() == "INSERT":
            info["block"] = ent.dxf.name
        if ent.dxftype() in ("TEXT", "MTEXT"):
            try:
                info["text"] = ent.dxf.text if ent.dxftype() == "TEXT" else ent.text
            except Exception:
                pass
        want = (identity or {}).get(h, {})
        for key in ("type", "layer", "block"):
            if key in want and info.get(key) != want[key]:
                raise CadError("DELETE_GUARD",
                               f"Identity mismatch on {h}: {key} {info.get(key)} != {want[key]}.",
                               {"handle": h, "actual": info, "expected": want})
        if "bbox" in want:
            wb, ab = want["bbox"], info["bbox"]
            if any(abs(a - b) > 0.01 for a, b in zip(wb, ab)):
                raise CadError("DELETE_GUARD", f"Bbox mismatch on {h}.",
                               {"handle": h, "actual": ab, "expected": wb})
        checked.append(info)
    expected = {"deleted": handles, "count": len(handles)}
    if dry_run:
        return OperationResult(ok=True, operation_id=op_id, drawing_before=before,
                               drawing_after=before, expected_state=expected,
                               actual_state=expected,
                               validations=[{"check": "dry_run_identity_ok", "ok": True,
                                             "detail": f"{len(checked)} identities verified"}]).to_dict()
    for h in handles:
        doc.entitydb[h].destroy()
    doc.saveas(out_path)
    after = drawing_identity(out_path).to_dict()
    # readback: handles must be gone
    doc2 = ezdxf.readfile(out_path)
    for h in handles:
        if h in doc2.entitydb:
            raise CadError("READBACK_FAIL", f"Handle {h} still present after delete.",
                           {"handle": h})
    return OperationResult(ok=True, operation_id=op_id, drawing_before=before,
                           drawing_after=after, deleted_handles=handles,
                           expected_state=expected,
                           actual_state={"deleted": handles, "count": len(handles)},
                           validations=[{"check": "delete_readback_absent", "ok": True}]).to_dict()


FIACAO_BLOCK = "FIACAO_LAMP_FNT"
FIACAO_INSERT_LAYER = "_ELT_ELETRODUTOS"
FIACAO_ATTRIB_LAYER = "ELET_FIAÇÃO"
FIACAO_ATTRIB_COLOR = 4
FIACAO_ATTRIB_LTYPE = "Continuous"
FIACAO_ATTRIB_STYLE = "textstyle6"
FIACAO_ATTRIB_HEIGHT = 0.08


def _dist_point_to_segment(px, py, ax, ay, bx, by) -> float:
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def create_fiacao_callout_bound(path: str, source_handle: str, circuit: str,
                               conductor_spec: str, edge_p1: list, edge_p2: list,
                               insert_xy: list, max_dist: float = 0.005,
                               expected_revision: str | None = None, dry_run: bool = False,
                               out_path: str | None = None) -> dict:
    """Clone a FIACAO_LAMP_FNT pattern INSERT bound ONTO a conduit edge.

    Copies block + relative ATTRIB offsets from source; overrides C/B values;
    forces pattern visuals (attrib layer/color/linetype/style/height/rotation);
    INSERT layer _ELT_ELETRODUTOS. Refuses when insert farther than max_dist
    from the edge segment (never floating). No leaders invented.
    """
    op_id = uuid.uuid4().hex[:12]
    if not circuit or not conductor_spec:
        raise CadError("ORPHAN_CALLOUT", "Fiacao callout requires circuit + conductor spec.", {})
    if not out_path or out_path == path:
        raise CadError("ORPHAN_CALLOUT", "Requires a distinct out_path (never in place).",
                       {"out_path": out_path})
    ident = assert_revision(path, expected_revision)
    before = ident if isinstance(ident, dict) else ident.to_dict()
    d = _dist_point_to_segment(insert_xy[0], insert_xy[1],
                               edge_p1[0], edge_p1[1], edge_p2[0], edge_p2[1])
    expected = {"circuit": circuit, "spec": conductor_spec, "at": insert_xy,
                "edge_dist": d, "bound": d <= max_dist}
    if not expected["bound"]:
        raise CadError("ORPHAN_CALLOUT",
                       f"Insert farther than {max_dist} from edge ({d:.4f}). Refusing floating callout.",
                       expected)
    if dry_run:
        return OperationResult(ok=True, operation_id=op_id, drawing_before=before,
                               drawing_after=before, expected_state=expected,
                               actual_state=expected,
                               validations=[{"check": "dry_run_bound_ok", "ok": True}]).to_dict()
    doc = ezdxf.readfile(path)
    try:
        src = doc.entitydb[source_handle]
    except KeyError:
        raise CadError("ENTITY_NOT_FOUND", f"Source {source_handle} not found.", {})
    if src.dxftype() != "INSERT":
        raise CadError("ENTITY_TYPE_MISMATCH", "Source must be an INSERT.",
                       {"handle": source_handle})
    msp = doc.modelspace()
    sx, sy = _insertion_point(src)
    nx, ny = float(insert_xy[0]), float(insert_xy[1])
    new = msp.add_blockref(src.dxf.name, (nx, ny, 0.0))
    new.dxf.layer = FIACAO_INSERT_LAYER
    try:
        new.dxf.rotation = float(src.dxf.rotation or 0.0)
    except Exception:
        pass
    try:
        new.dxf.xscale = float(src.dxf.xscale or 1.0)
        new.dxf.yscale = float(src.dxf.yscale or 1.0)
    except Exception:
        pass
    values = {"C": circuit, "B": conductor_spec}
    for a in src.attribs:
        tag = a.dxf.tag
        offx = float(a.dxf.insert[0]) - sx
        offy = float(a.dxf.insert[1]) - sy
        na = new.add_attrib(tag, values.get(tag, a.dxf.text), (nx + offx, ny + offy))
        na.dxf.layer = FIACAO_ATTRIB_LAYER
        try:
            na.dxf.color = FIACAO_ATTRIB_COLOR
        except Exception:
            pass
        try:
            na.dxf.linetype = FIACAO_ATTRIB_LTYPE
        except Exception:
            pass
        try:
            na.dxf.style = FIACAO_ATTRIB_STYLE
        except Exception:
            pass
        try:
            na.dxf.height = FIACAO_ATTRIB_HEIGHT
        except Exception:
            pass
        try:
            na.dxf.rotation = float(a.dxf.rotation or 0.0)
        except Exception:
            pass
    created = [str(new.dxf.handle)]
    doc.saveas(out_path)
    after = drawing_identity(out_path).to_dict()
    # readback
    doc2 = ezdxf.readfile(out_path)
    rb = doc2.entitydb[created[0]]
    got = {a.dxf.tag: a.dxf.text for a in rb.attribs}
    if got.get("C") != circuit or got.get("B") != conductor_spec:
        raise CadError("READBACK_FAIL", "Attributes not persisted.",
                       {"handle": created[0], "got": got})
    return OperationResult(ok=True, operation_id=op_id, drawing_before=before,
                           drawing_after=after, created_handles=created,
                           expected_state=expected,
                           actual_state={"handle": created[0], "at": [nx, ny],
                                         "attrs": got, "edge_dist": d},
                           validations=[{"check": "fiacao_bound_readback", "ok": True}]).to_dict()
