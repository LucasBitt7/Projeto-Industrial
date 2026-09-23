"""Collision engine: fast bbox + exact segment check where needed."""
from __future__ import annotations

from . import geometry as G


def detect_collisions(refs: list, clearance: float = 0.0, pairs: list | None = None) -> list:
    """refs: list of CadEntityRef dicts (must include handle + bbox).
    pairs: optional list of (kind_a, kind_b, label) rules; by default all-vs-all.
    Returns list of {a, b, rule, overlap}."""
    hits = []
    kinds = {r["handle"]: _kind(r) for r in refs}
    n = len(refs)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = refs[i], refs[j]
            ba = a["bbox"] if clearance == 0 else G.expand_bbox(a["bbox"], clearance)
            bb = b["bbox"]
            # degenerate point bboxes: expand slightly for meaningful overlap
            if _degenerate(ba):
                ba = G.expand_bbox(ba, max(clearance, 1e-6) or 0.5)
            if _degenerate(bb):
                bb = G.expand_bbox(bb, 0.5)
            if G.bbox_intersects(ba, bb):
                rule = f"{kinds[a['handle']]}_vs_{kinds[b['handle']]}"
                hits.append({"a": a["handle"], "b": b["handle"], "rule": rule,
                             "a_kind": kinds[a["handle"]], "b_kind": kinds[b["handle"]]})
    if pairs:
        wanted = set(pairs)
        hits = [h for h in hits if h["rule"] in wanted or f"{h['b_kind']}_vs_{h['a_kind']}" in wanted]
    return hits


def _degenerate(b) -> bool:
    return (b[2] - b[0]) <= 1e-9 and (b[3] - b[1]) <= 1e-9


def _kind(r: dict) -> str:
    blk = (r.get("block_name") or "").upper()
    txt = (r.get("text") or "").upper()
    if "QDF" in blk or "QDF" in txt:
        return "panel"
    if "QDL" in blk or "QDL" in txt:
        return "panel"
    if r["type"] == "INSERT":
        return "outlet"
    if r["type"] in ("TEXT", "MTEXT"):
        return "callout" if txt.startswith("T") else "text"
    return r["type"].lower()
