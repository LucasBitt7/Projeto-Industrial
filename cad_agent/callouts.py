"""Callouts as composite templates bound to a conduit edge. Never orphan Tn text."""
from __future__ import annotations

import math
import re
import uuid

import ezdxf

from .drawing import assert_revision, drawing_identity
from .errors import CadError
from .models import OperationResult

CALLOUT_LAYERS = {"CALLOUT": "ELE-CALLOUT"}


def _edge_point(edge: dict) -> tuple:
    if "x" in edge and "y" in edge:
        return (float(edge["x"]), float(edge["y"]))
    if "p1" in edge and "p2" in edge:
        return ((edge["p1"][0] + edge["p2"][0]) / 2, (edge["p1"][1] + edge["p2"][1]) / 2)
    raise CadError("ENTITY_NOT_FOUND", "Callout needs a conduit edge anchor.", {"edge": edge})


def create_callout(path: str, conduit_edge: dict, circuits: list, conductor_spec: str,
                   placement: str = "above", layer: str = "ELE-CALLOUT",
                   expected_revision: str | None = None, dry_run: bool = False,
                   out_path: str | None = None) -> dict:
    """Create Tn + circuits + spec as ONE related group on/near the edge."""
    op_id = uuid.uuid4().hex[:12]
    if not circuits:
        raise CadError("ORPHAN_CALLOUT", "Callout requires >=1 circuit.", {})
    if not conductor_spec:
        raise CadError("ORPHAN_CALLOUT", "Callout requires conductor spec (section/bitola).", {})
    ident = assert_revision(path, expected_revision)
    before = ident if isinstance(ident, dict) else ident.to_dict()
    ex, ey = _edge_point(conduit_edge)
    offs = {"above": (0, 8), "below": (0, -8), "left": (-12, 0), "right": (12, 0),
            "nearest_free": (6, 6), "template_default": (0, 8)}
    dx, dy = offs.get(placement, (0, 8))
    tx, ty = ex + dx, ey + dy
    label = f"{'/'.join(circuits)} {conductor_spec}"
    expected = {"at": [tx, ty], "label": label, "edge": conduit_edge}
    if dry_run:
        return OperationResult(ok=True, operation_id=op_id, drawing_before=before, drawing_after=before,
                               expected_state=expected, actual_state=expected,
                               validations=[{"check": "dry_run", "ok": True}]).to_dict()
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    # group: leader line edge->callout + single MTEXT carrying full spec (never split Tn/spec)
    leader = msp.add_line((ex, ey), (tx, ty))
    leader.dxf.layer = layer
    mt = msp.add_mtext(label)
    mt.dxf.insert = (tx, ty)
    mt.dxf.layer = layer
    try:
        mt.dxf.attachment_point = 5
    except Exception:
        pass
    created = [str(leader.dxf.handle), str(mt.dxf.handle)]
    target = out_path or path
    doc.saveas(target)
    after = drawing_identity(target).to_dict()
    return OperationResult(ok=True, operation_id=op_id, drawing_before=before, drawing_after=after,
                           created_handles=created, expected_state=expected,
                           actual_state={"at": [tx, ty], "label": label},
                           validations=[{"check": "callout_group_created", "ok": True}]).to_dict()


def validate_callouts(path: str, layer: str = "ELE-CALLOUT",
                      circuit_regex: str = r"\bT\d{1,3}\b") -> dict:
    """Every callout text must carry circuit + conductor spec; every leader must touch text."""
    from .entities import find_entities
    rx = re.compile(circuit_regex)
    refs = find_entities(path, layer=layer, limit=5000)
    texts = [r for r in refs if r["type"] in ("TEXT", "MTEXT")]
    leaders = [r for r in refs if r["type"] in ("LINE", "LWPOLYLINE")]
    violations = []
    for t in texts:
        content = t.get("text") or ""
        has_ckt = bool(rx.search(content))
        has_spec = bool(re.search(r"\d+(,\d+)?\s?mm", content) or "#" in content or "mm" in content.lower()
                        or re.search(r"\d+#\d+", content))
        if not (has_ckt and has_spec):
            violations.append({"handle": t["handle"], "issue": "incomplete_callout", "text": content,
                               "code": "ORPHAN_CALLOUT"})
    # orphan leaders: line whose neither endpoint is near any callout text
    for ln in leaders:
        b = ln["bbox"]
        near = False
        for t in texts:
            tb = t["bbox"]
            tcx, tcy = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
            if t.get("insertion_point"):
                tcx, tcy = t["insertion_point"]
            for px, py in [(b[0], b[1]), (b[2], b[3])]:
                if math.hypot(px - tcx, py - tcy) < 25.0:
                    near = True
        if not near:
            violations.append({"handle": ln["handle"], "issue": "orphan_leader", "code": "ORPHAN_ENDPOINT"})
    ok = len(violations) == 0
    out = {"ok": ok, "checked_texts": len(texts), "checked_leaders": len(leaders),
           "violations": violations,
           "checks": [{"check": "callout_integrity", "ok": ok, "detail": f"{len(violations)} violations"}]}
    if not ok:
        out["code"] = "ORPHAN_CALLOUT" if any(v.get("code") == "ORPHAN_CALLOUT" for v in violations) else "ORPHAN_ENDPOINT"
    return out
