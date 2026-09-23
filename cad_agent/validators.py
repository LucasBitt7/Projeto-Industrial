"""Independent validators: scope guard, completion gate, delete guard."""
from __future__ import annotations

import ezdxf

from .drawing import _canonical_entity
from .errors import CadError


def _canon_map(path: str) -> dict:
    doc = ezdxf.readfile(path)
    out = {}
    for e in doc.modelspace():
        try:
            h = str(e.dxf.handle).upper()
            out[h] = _canonical_entity(e)
        except Exception:
            continue
    return out


def _bbox_center(canon: dict):
    for k in ("insert", "center"):
        if k in canon:
            return tuple(canon[k])
    if "start" in canon and "end" in canon:
        return ((canon["start"][0] + canon["end"][0]) / 2, (canon["start"][1] + canon["end"][1]) / 2)
    if "points" in canon and canon["points"]:
        xs = [p[0] for p in canon["points"]]; ys = [p[1] for p in canon["points"]]
        return (sum(xs) / len(xs), sum(ys) / len(ys))
    return None


def validate_no_changes_outside_scope(before_path: str, after_path: str, scope: dict) -> dict:
    """Compare canonical before/after. Any created/deleted/modified entity outside the
    allowed bbox/handles/layers/types => SCOPE_VIOLATION."""
    bmap, amap = _canon_map(before_path), _canon_map(after_path)
    ab = scope.get("allowed_bbox")
    ah = set(h.upper() for h in (scope.get("allowed_handles") or []))
    al = set(scope.get("allowed_layers") or [])
    at = set(scope.get("allowed_entity_types") or [])

    def in_scope(handle: str, canon: dict) -> bool:
        if ah and handle in ah:
            return True
        if al and canon.get("layer") not in al:
            return False
        if at and canon.get("type") not in at:
            return False
        if ab:
            c = _bbox_center(canon)
            if c is None:
                return False
            if not (ab[0] <= c[0] <= ab[2] and ab[1] <= c[1] <= ab[3]):
                return False
        # if no constraint at all matched, treat as in-scope only when scope empty
        if not (ab or ah or al or at):
            return True
        # handle not explicitly allowed but bbox/layer/type passed
        if ah and handle not in ah:
            # handles list is exclusive when present with other filters? No: allow if bbox matches
            # but created handles can never be pre-listed, so bbox/layer must decide.
            pass
        return True

    violations = []
    for h, c in amap.items():
        if h not in bmap:
            if not in_scope(h, c):
                violations.append({"kind": "created_outside_scope", "handle": h, "layer": c.get("layer")})
    for h, c in bmap.items():
        if h not in amap:
            if h not in ah and not _was_in_scope_before(h, c, scope):
                violations.append({"kind": "deleted_outside_scope", "handle": h, "layer": c.get("layer")})
    for h in set(bmap) & set(amap):
        if bmap[h] != amap[h] and h not in ah:
            if not _was_in_scope_before(h, amap[h], scope):
                violations.append({"kind": "modified_outside_scope", "handle": h,
                                   "layer": amap[h].get("layer")})
    ok = len(violations) == 0
    out = {"ok": ok, "violations": violations,
           "checks": [{"check": "scope_guard", "ok": ok, "detail": f"{len(violations)} violations"}]}
    if not ok:
        out["code"] = "SCOPE_VIOLATION"
    return out


def _was_in_scope_before(handle: str, canon: dict, scope: dict) -> bool:
    ab = scope.get("allowed_bbox")
    ah = set(h.upper() for h in (scope.get("allowed_handles") or []))
    al = set(scope.get("allowed_layers") or [])
    at = set(scope.get("allowed_entity_types") or [])
    if ah and handle in ah:
        return True
    if al and canon.get("layer") not in al:
        return False
    if at and canon.get("type") not in at:
        return False
    if ab:
        c = _bbox_center(canon)
        if c is None:
            return False
        return ab[0] <= c[0] <= ab[2] and ab[1] <= c[1] <= ab[3]
    # No bbox: if scope only lists handles, anything else is out of scope
    if ah and handle not in ah:
        return False
    return True


def validate_delete_guard(before_count: int, after_count: int, deleted_handles: list,
                          expected_count: int | None) -> dict:
    if expected_count is not None and len(deleted_handles) != expected_count:
        return {"ok": False, "code": "DELETE_GUARD",
                "checks": [{"check": "delete_count", "ok": False,
                            "detail": f"expected {expected_count}, got {len(deleted_handles)}"}]}
    return {"ok": True, "checks": [{"check": "delete_count", "ok": True}]}


def completion_gate(execution_ok: bool, readback_ok: bool, scope_ok: bool,
                    validators_ok: bool, artifact_identity_ok: bool) -> dict:
    checks = {"execution_ok": execution_ok, "readback_ok": readback_ok, "scope_ok": scope_ok,
              "validators_ok": validators_ok, "artifact_identity_ok": artifact_identity_ok}
    ok = all(checks.values())
    return {"status": "PASS" if ok else "FAIL", "checks": checks}
