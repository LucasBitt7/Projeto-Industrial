"""Parametrized rigid clone (versioned capability extension).

Stock `clone_template` copies geometry verbatim and can only replace TEXT
labels via `new_label`. Unifilar diagrams use MTEXT for every electrical
value, so a faithful-but-parametrized clone was a missing capability.
This module extends (never replaces) the stock behavior:

- ONE rigid transform for all members (same guarantee as stock).
- `text_map`: exact source-content -> new content for TEXT/MTEXT members.
  Unknown keys FAIL CLOSED (TEXTMAP_NO_MATCH). Unmapped texts are kept
  verbatim (template-faithful).
- Full MTEXT fidelity (char_height, style, attachment_point, rotation,
  layer) re-read from the SOURCE drawing — stock clone drops these.
- `extra_groups`: clone a member subset (e.g. one CircuitRow) with an
  additional offset, same angle + text_map (for panels with more rows
  than the source template, growing the frame by the measured row_pitch).
- `member_edits`: deterministic post-clone adjustments on created members
  (`translate`, `extend_y_min`, `extend_y_max`), identified by SOURCE
  handle. Used only for frame/busbar/ground growth by a measured module.
- `dry_run=True`: compute everything, save nothing.
- Always requires `out_path != source`, `expected_revision`, and performs
  readback (reopen + verify handles and MTEXT contents).
"""
from __future__ import annotations

import os
import uuid as _uuid

import ezdxf

from . import geometry as G
from .drawing import assert_revision, drawing_identity
from .errors import CadError
from .models import OperationResult
from .templates import get_template

SUPPORTED = ("LINE", "LWPOLYLINE", "CIRCLE", "TEXT", "MTEXT")


def _fidelity(source_dxf: str, handles: list) -> dict:
    """Re-read TEXT/MTEXT fidelity fields from the source drawing."""
    doc = ezdxf.readfile(source_dxf)
    msp = doc.modelspace()
    out = {}
    for h in handles:
        for cand in msp:
            try:
                if str(cand.dxf.handle).upper() != h.upper():
                    continue
            except Exception:
                continue
            t = cand.dxftype()
            if t in ("TEXT", "MTEXT"):
                d = cand.dxf
                out[h.upper()] = {
                    "type": t,
                    "height": float(getattr(d, "char_height", 0.0) or 0.0)
                    or float(getattr(d, "height", 0.0) or 0.0),
                    "style": str(getattr(d, "style", "") or ""),
                    "attachment": int(getattr(d, "attachment_point", 1) or 1),
                    "rotation": float(getattr(d, "rotation", 0.0) or 0.0),
                }
            break
    return out


def _place(rel: dict, fid: dict, anchor: list, dx: float, dy: float,
           angle_deg: float, text_map: dict, tag: str = "base",
           handle_rules: dict | None = None) -> dict:
    """Compute creation spec for one template member (no side effects).

    Text resolution order (fail-closed, template-faithful by default):
    1. f"{tag}:{HANDLE}" in handle_rules, 2. HANDLE in handle_rules,
    3. exact content in text_map, 4. keep source content verbatim.
    """
    t = rel["type"]
    if t not in SUPPORTED:
        raise CadError("UNSUPPORTED_MEMBER", f"Member type {t} cannot be cloned.",
                       {"handle": rel.get("handle")})
    ax, ay = anchor
    handle_rules = handle_rules or {}
    spec = {"type": t, "layer": rel.get("layer", "0"), "src": rel.get("handle")}
    if t == "LINE":
        p1 = G.rigid_transform_point(rel["p1"][0], rel["p1"][1], 0, 0, angle_deg, 0, 0)
        p2 = G.rigid_transform_point(rel["p2"][0], rel["p2"][1], 0, 0, angle_deg, 0, 0)
        spec["p1"] = [ax + dx + p1[0], ay + dy + p1[1]]
        spec["p2"] = [ax + dx + p2[0], ay + dy + p2[1]]
    elif t == "LWPOLYLINE":
        pts = [G.rigid_transform_point(p[0], p[1], 0, 0, angle_deg, 0, 0)
               for p in rel["points"]]
        spec["points"] = [[ax + dx + p[0], ay + dy + p[1]] for p in pts]
        spec["closed"] = bool(rel.get("closed", False))
    elif t == "CIRCLE":
        c = G.rigid_transform_point(rel["c"][0], rel["c"][1], 0, 0, angle_deg, 0, 0)
        spec["c"] = [ax + dx + c[0], ay + dy + c[1]]
        spec["r"] = float(rel["r"])
    else:  # TEXT / MTEXT
        o = G.rigid_transform_point(rel["dx"], rel["dy"], 0, 0, angle_deg, 0, 0)
        spec["insert"] = [ax + dx + o[0], ay + dy + o[1]]
        content = rel.get("content", "")
        hkey = str(rel.get("handle", "")).upper()
        if f"{tag}:{hkey}" in handle_rules:
            content = handle_rules[f"{tag}:{hkey}"]
        elif hkey in handle_rules:
            content = handle_rules[hkey]
        elif content in (text_map or {}):
            content = text_map[content]
        spec["content"] = content
        spec["rotation"] = (fid.get("rotation", rel.get("rotation", 0.0)) + angle_deg) % 360.0
        spec["height"] = fid.get("height", 0.0)
        spec["style"] = fid.get("style", "")
        spec["attachment"] = fid.get("attachment", 1)
    return spec


def _create(msp, doc, spec: dict) -> str:
    t = spec["type"]
    if t == "LINE":
        e = msp.add_line(tuple(spec["p1"]), tuple(spec["p2"]))
    elif t == "LWPOLYLINE":
        e = msp.add_lwpolyline([tuple(p) for p in spec["points"]])
        e.closed = spec["closed"]
    elif t == "CIRCLE":
        e = msp.add_circle(tuple(spec["c"]), spec["r"])
    elif t == "TEXT":
        e = msp.add_text(spec["content"], height=spec["height"] or 2.5)
        e.dxf.insert = tuple(spec["insert"])
        e.dxf.rotation = spec["rotation"]
        if spec["style"]:
            if spec["style"] not in doc.styles:
                raise CadError("STYLE_MISSING", f"Text style missing: {spec['style']}",
                               {"style": spec["style"]})
            e.dxf.style = spec["style"]
    elif t == "MTEXT":
        e = msp.add_mtext(spec["content"])
        e.dxf.insert = tuple(spec["insert"]) + ((0.0,) if len(tuple(spec["insert"])) == 2 else ())
        e.dxf.rotation = spec["rotation"]
        if spec["height"]:
            e.dxf.char_height = spec["height"]
        if spec["style"]:
            if spec["style"] not in doc.styles:
                raise CadError("STYLE_MISSING", f"Text style missing: {spec['style']}",
                               {"style": spec["style"]})
            e.dxf.style = spec["style"]
        e.dxf.attachment_point = spec["attachment"]
    else:  # pragma: no cover
        raise CadError("UNSUPPORTED_MEMBER", f"Cannot create {t}.", {})
    e.dxf.layer = spec["layer"]
    return str(e.dxf.handle)


def _spec_points(s: dict) -> list:
    """Collect (x, y) points of a creation spec for bbox purposes."""
    t = s["type"]
    if t == "LINE":
        return [tuple(s["p1"]), tuple(s["p2"])]
    if t == "LWPOLYLINE":
        return [tuple(p) for p in s["points"]]
    if t == "CIRCLE":
        c, r = s["c"], s["r"]
        return [(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)]
    return [tuple(s["insert"])]


def _apply_edits_to_points(pts: list, ops: list) -> list:
    """Apply translate/extend edits to a point list (dry-run bbox honesty)."""
    out = [list(p) for p in pts]
    for op, delta in ops:
        if op == "translate":
            ox, oy = delta
            out = [[x + ox, y + oy] for x, y in out]
        elif op == "extend_y_min":
            ys = [p[1] for p in out]
            m = min(ys)
            out = [[x, y + delta if y == m else y] for x, y in out]
        elif op == "extend_y_max":
            ys = [p[1] for p in out]
            m = max(ys)
            out = [[x, y + delta if y == m else y] for x, y in out]
    return out


def clone_parametrized(target_dxf: str, template_id: str, dx: float, dy: float,
                       angle_deg: float = 0.0, anchor_override: list | None = None,
                       text_map: dict | None = None, handle_rules: dict | None = None,
                       extra_groups: list | None = None, extra_texts: list | None = None,
                       member_edits: list | None = None, out_path: str | None = None,
                       expected_revision: str | None = None, dry_run: bool = False) -> dict:
    """Clone a template rigidly, replacing MTEXT/TEXT contents via text_map."""
    if not expected_revision:
        raise CadError("WRITE_WITHOUT_INSPECTION",
                       f"Write to {target_dxf} refused: no expected_revision. "
                       f"Run INSPECT first and pass its revision_token.",
                       {"drawing": target_dxf})
    tpl = get_template(template_id)
    ident = assert_revision(target_dxf, expected_revision)
    before = ident if isinstance(ident, dict) else ident.to_dict()
    if not out_path or os.path.abspath(out_path) == os.path.abspath(target_dxf):
        raise CadError("OUTPATH_REQUIRED",
                       "out_path must be given and differ from the source drawing.",
                       {"out_path": out_path})
    text_map = dict(text_map or {})
    # fail closed on unknown text_map keys
    known_contents = {r.get("content", "") for r in tpl["relative_entities"]
                      if r["type"] in ("TEXT", "MTEXT")}
    for k in text_map:
        if k not in known_contents:
            raise CadError("TEXTMAP_NO_MATCH", f"text_map key matches no template text: {k!r}",
                           {"key": k})
    anchor = list(anchor_override) if anchor_override else list(tpl["anchor"])
    fid = _fidelity(tpl["source_drawing"], tpl["handles"])
    by_handle = {r.get("handle", "").upper(): r for r in tpl["relative_entities"]}
    tpl_cache = {template_id: (tpl, fid, by_handle)}

    def _tpl(tid):
        if tid not in tpl_cache:
            t = get_template(tid)
            tpl_cache[tid] = (t, _fidelity(t["source_drawing"], t["handles"]),
                              {r.get("handle", "").upper(): r for r in t["relative_entities"]})
        return tpl_cache[tid]

    jobs = [("base", r, dx, dy, None, template_id) for r in tpl["relative_entities"]]
    for gi, g in enumerate(extra_groups or []):
        _t, _f, _b = _tpl(g.get("template_id", template_id))
        for h in g.get("handles", []):
            r = _b.get(str(h).upper())
            if r is None:
                raise CadError("ENTITY_NOT_FOUND", f"extra_group handle not in template: {h}",
                               {"handle": h})
            jobs.append((f"extra{gi}", r, dx + float(g.get("dx", 0)), dy + float(g.get("dy", 0)),
                         g.get("text_map"), g.get("template_id", template_id)))

    specs = []
    for tag, r, jdx, jdy, gmap, tid in jobs:
        _t, _f, _b = _tpl(tid)
        f = _f.get(str(r.get("handle", "")).upper(), {})
        known = {x.get("content", "") for x in _t["relative_entities"]
                 if x["type"] in ("TEXT", "MTEXT")}
        merged = dict(text_map or {})
        if gmap:
            for k in gmap:
                if k not in known:
                    raise CadError("TEXTMAP_NO_MATCH",
                                   f"extra_group text_map key matches nothing: {k!r}", {"key": k})
            merged.update(gmap)
        specs.append((tag, r, _place(r, f, anchor, jdx, jdy, angle_deg, merged, tag,
                                    handle_rules)))
    for ei, xt in enumerate(extra_texts or []):
        for req in ("content", "layer", "style", "height"):
            if not xt.get(req):
                raise CadError("BAD_ANNOTATION", f"extra_texts[{ei}] missing {req}.", {})
        o = G.rigid_transform_point(float(xt.get("dx", 0)), float(xt.get("dy", 0)),
                                    0, 0, angle_deg, 0, 0)
        specs.append((f"note{ei}", {"handle": f"NOTE{ei}"},
                      {"type": "MTEXT", "layer": xt["layer"], "src": f"NOTE{ei}",
                       "insert": [anchor[0] + dx + o[0], anchor[1] + dy + o[1]],
                       "content": xt["content"], "rotation": angle_deg % 360.0,
                       "height": float(xt["height"]), "style": xt["style"],
                       "attachment": int(xt.get("attachment", 1))}))

    # index specs by source handle for edit application (base wins on duplicates)
    spec_edits = {}
    for ed in member_edits or []:
        spec_edits.setdefault(str(ed.get("handle", "")).upper(), []).append(ed)

    def _ops_for(src_handle):
        ops = []
        for ed in spec_edits.get(str(src_handle).upper(), []):
            op = ed.get("op")
            if op == "translate":
                ops.append(("translate", (float(ed.get("dx", 0)), float(ed.get("dy", 0)))))
            elif op in ("extend_y_min", "extend_y_max"):
                ops.append((op, float(ed.get("delta", 0))))
            else:
                raise CadError("BAD_EDIT", f"Unknown member_edit op: {op}.", {"op": op})
        return ops

    if dry_run:
        xs, ys = [], []
        for _tag, r, s in specs:
            for x, y in _apply_edits_to_points(
                    _spec_points(s), _ops_for(r.get("handle", ""))):
                xs.append(x)
                ys.append(y)
        return OperationResult(
            ok=True, operation_id="dryrun",
            drawing_before=before, drawing_after=before,
            expected_state={"count": len(specs),
                            "bbox": [min(xs), min(ys), max(xs), max(ys)]},
            actual_state={"count": len(specs)},
            validations=[{"check": "dry_run_computed", "ok": True}],
            warnings=["dry_run: nothing saved"],
        ).to_dict()

    doc = ezdxf.readfile(target_dxf)
    msp = doc.modelspace()
    created, handle_map, content_expect = [], {}, {}
    for _tag, r, s in specs:
        nh = _create(msp, doc, s)
        created.append(nh)
        key = str(r.get("handle", "")).upper()
        if key not in handle_map:  # base wins: edits address base members
            handle_map[key] = nh
        if s["type"] in ("TEXT", "MTEXT"):
            content_expect[nh] = s["content"]

    # deterministic member edits (frame/busbar/ground growth by measured module)
    for ed in member_edits or []:
        nh = handle_map.get(str(ed.get("handle", "")).upper())
        if nh is None:
            raise CadError("ENTITY_NOT_FOUND", "member_edit handle not cloned.",
                           {"handle": ed.get("handle")})
        ent = doc.entitydb.get(nh)
        op = ed.get("op")
        if op == "translate":
            ox, oy = float(ed.get("dx", 0)), float(ed.get("dy", 0))
            t = ent.dxftype()
            if t in ("TEXT", "MTEXT"):
                p = ent.dxf.insert
                ent.dxf.insert = (p.x + ox, p.y + oy)
            elif t == "LINE":
                ent.dxf.start = (ent.dxf.start.x + ox, ent.dxf.start.y + oy)
                ent.dxf.end = (ent.dxf.end.x + ox, ent.dxf.end.y + oy)
            elif t == "LWPOLYLINE":
                ent.set_points([(x + ox, y + oy) for x, y, *_ in ent.get_points()])
            elif t == "CIRCLE":
                ent.dxf.center = (ent.dxf.center.x + ox, ent.dxf.center.y + oy)
            else:
                raise CadError("UNSUPPORTED_MEMBER", f"translate unsupported for {t}.", {})
        elif op in ("extend_y_min", "extend_y_max"):
            delta = float(ed.get("delta", 0))
            t = ent.dxftype()
            if t != "LINE":
                raise CadError("UNSUPPORTED_MEMBER", f"{op} only supports LINE.", {})
            s, e = ent.dxf.start, ent.dxf.end
            if op == "extend_y_min":
                if s.y <= e.y:
                    ent.dxf.start = (s.x, s.y + delta)
                else:
                    ent.dxf.end = (e.x, e.y + delta)
            else:
                if s.y >= e.y:
                    ent.dxf.start = (s.x, s.y + delta)
                else:
                    ent.dxf.end = (e.x, e.y + delta)
        else:
            raise CadError("BAD_EDIT", f"Unknown member_edit op: {op}.", {"op": op})

    doc.saveas(out_path)
    # READBACK on the saved artifact
    back = ezdxf.readfile(out_path)
    rdb = back.modelspace()
    seen = set()
    for cand in rdb:
        try:
            seen.add(str(cand.dxf.handle).upper())
        except Exception:
            pass
    missing = [h for h in created if h.upper() not in seen]
    if missing:
        raise CadError("READBACK_FAIL", "Created handles missing after save.", {"missing": missing})
    content_checks = []
    for nh, exp in content_expect.items():
        for cand in rdb:
            try:
                if str(cand.dxf.handle).upper() == nh.upper():
                    got = str(cand.dxf.text) if cand.dxftype() == "TEXT" else str(cand.text)
                    content_checks.append({"check": f"text:{nh}", "ok": got == exp,
                                           "detail": "" if got == exp else f"{got!r}!={exp!r}"})
                    if got != exp:
                        raise CadError("READBACK_FAIL", "Text content mismatch.",
                                       {"handle": nh, "got": got, "expected": exp})
                    break
            except CadError:
                raise
            except Exception:
                continue
    after = drawing_identity(out_path).to_dict()
    return OperationResult(
        ok=True, operation_id=_uuid.uuid4().hex[:12],
        drawing_before=before, drawing_after=after,
        created_handles=created, handle_map=handle_map,
        expected_state={"count": len(specs)}, actual_state={"count": len(created)},
        validations=[{"check": "clone_count", "ok": len(created) == len(specs)}] + content_checks,
        artifact_paths={"out": os.path.abspath(out_path)},
    ).to_dict()
