"""Room semantics: detect circuit contamination inside rooms."""
from __future__ import annotations

import re

from .entities import find_entities

DEFAULT_CIRCUIT_REGEX = r"\bT\d{1,3}\b"


def _point_in_bbox(x, y, bbox) -> bool:
    return bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]


def _point_in_polygon(x, y, poly) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def _room_contains(room: dict, x, y) -> bool:
    geo = room.get("bbox_or_polygon", {})
    if "bbox" in geo:
        return _point_in_bbox(x, y, geo["bbox"])
    if "polygon" in geo:
        return _point_in_polygon(x, y, geo["polygon"])
    return False


def validate_room(path: str, room: dict, circuit_regex: str = DEFAULT_CIRCUIT_REGEX) -> dict:
    """Scan TEXT/MTEXT/ATTRIB inside room; every circuit tag must be in allowed_circuits
    (and must not be in forbidden_circuits)."""
    rx = re.compile(circuit_regex)
    allowed = set(room.get("allowed_circuits", []))
    forbidden = set(room.get("forbidden_circuits", []))
    refs = find_entities(path, limit=10000)
    violations = []
    checked = 0
    for r in refs:
        texts = []
        if r.get("text"):
            texts.append(str(r["text"]))
        for v in (r.get("attributes") or {}).values():
            texts.append(str(v))
        found = set()
        for t in texts:
            found.update(rx.findall(t))
        if not found:
            continue
        # location: insertion or bbox center
        if r.get("insertion_point"):
            x, y = r["insertion_point"]
        else:
            b = r["bbox"]
            x, y = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        if not _room_contains(room, x, y):
            continue
        checked += 1
        for c in found:
            if c in forbidden or (allowed and c not in allowed):
                violations.append({"handle": r["handle"], "circuit": c, "at": [x, y],
                                   "room": room.get("room_id")})
    ok = len(violations) == 0
    out = {"ok": ok, "room": room.get("room_id"), "checked": checked,
           "violations": violations,
           "checks": [{"check": "room_semantics", "ok": ok,
                       "detail": f"{len(violations)} violations in {checked} tagged entities"}]}
    if not ok:
        out["code"] = "ROOM_SEMANTIC_VIOLATION"
    return out


def validate_project_scope(path: str, rooms: list, circuit_regex: str = DEFAULT_CIRCUIT_REGEX) -> dict:
    results = [validate_room(path, r, circuit_regex) for r in rooms]
    ok = all(r["ok"] for r in results)
    out = {"ok": ok, "rooms": results,
           "checks": [{"check": f"room_{r['room']}", "ok": r["ok"]} for r in results]}
    if not ok:
        out["code"] = "ROOM_SEMANTIC_VIOLATION"
    return out
