"""Conduit network: orthogonal routing + graph validation (tree, no cycles, no orphans)."""
from __future__ import annotations

import math
import uuid

import ezdxf

from . import geometry as G
from .drawing import assert_revision, drawing_identity
from .entities import get_entity
from .errors import CadError
from .models import OperationResult


def _anchor(ref: dict) -> tuple:
    if ref.get("insertion_point"):
        return tuple(ref["insertion_point"])
    b = ref["bbox"]
    return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)


def build_network_from_layer(path: str, layer: str, snap_tol: float = 1.0) -> dict:
    """Collect LINE/LWPOLYLINE segments on conduit layer, build graph."""
    doc = ezdxf.readfile(path)
    polylines = []
    for e in doc.modelspace():
        try:
            if str(e.dxf.layer) != layer:
                continue
            t = e.dxftype()
            if t == "LINE":
                polylines.append([(float(e.dxf.start.x), float(e.dxf.start.y)),
                                  (float(e.dxf.end.x), float(e.dxf.end.y))])
            elif t == "LWPOLYLINE":
                pts = [(float(x), float(y)) for x, y, *_ in e.get_points()]
                if len(pts) >= 2:
                    polylines.append(pts)
        except Exception:
            continue
    graph = G.polyline_to_graph(polylines, snap_tol=snap_tol)
    return {"polylines": polylines, "graph": graph}


def validate_network_graph(graph: dict, terminal_ids: list | None = None) -> dict:
    comps = G.connected_components(graph)
    cycles = G.detect_cycles(graph)
    orphans = G.orphan_endpoints(graph)
    connected = len(comps) <= 1
    checks = [
        {"check": "connected", "ok": connected, "detail": f"{len(comps)} components"},
        {"check": "acyclic", "ok": len(cycles) == 0, "detail": f"{len(cycles)} cycles"},
    ]
    ok = connected and len(cycles) == 0
    out = {"ok": ok, "checks": checks, "components": comps, "cycles": cycles,
           "orphan_endpoints": orphans,
           "connected": connected, "cycle_count": len(cycles)}
    if not connected:
        out["code"] = "NETWORK_DISCONNECTED"
    elif cycles:
        out["code"] = "NETWORK_CYCLE"
    if orphans and terminal_ids is not None:
        non_terminal_orphans = [n for n in orphans if n not in set(terminal_ids)]
        out["non_terminal_orphans"] = non_terminal_orphans
    return out


def route_conduit(path: str, source_handle: str, destination_handles: list,
                  layer: str = "ELETRODUTO", clearance: float = 5.0,
                  expected_revision: str | None = None, dry_run: bool = False,
                  out_path: str | None = None, obstacles: list | None = None) -> dict:
    """Orthogonal tree: source -> each destination with shared trunk where aligned.
    P0 deterministic: route each destination orthogonally from source anchor."""
    op_id = uuid.uuid4().hex[:12]
    ident = assert_revision(path, expected_revision)
    before = ident if isinstance(ident, dict) else ident.to_dict()
    src = get_entity(path, source_handle)
    s = _anchor(src)
    routes = []
    for dh in destination_handles:
        d = get_entity(path, dh)
        e = _anchor(d)
        routes.append(G.route_with_clearance(s, e, obstacles or [], clearance))
    expected = {"routes": routes, "layer": layer}
    if dry_run:
        # validate graph of proposed routes
        g = G.polyline_to_graph(routes, snap_tol=clearance / 10 if clearance else 1.0)
        v = validate_network_graph(g)
        return OperationResult(ok=v["ok"], operation_id=op_id, drawing_before=before,
                               drawing_after=before, expected_state=expected,
                               actual_state={"routes": routes},
                               validations=[{"check": k["check"], "ok": k["ok"]} for k in v["checks"]],
                               error_code=None if v["ok"] else v.get("code", "VALIDATION_FAIL"),
                               error=None if v["ok"] else "proposed network invalid").to_dict()
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    created = []
    for r in routes:
        e = msp.add_lwpolyline([(float(x), float(y)) for x, y in r])
        e.dxf.layer = layer
        created.append(str(e.dxf.handle))
    target = out_path or path
    doc.saveas(target)
    after = drawing_identity(target).to_dict()
    # READBACK: rebuild graph from file and validate
    net = build_network_from_layer(target, layer)
    v = validate_network_graph(net["graph"])
    ok = v["connected"]  # cycles tolerated only if explicitly checked; tree expected
    if v["cycle_count"] > 0:
        ok = False
    return OperationResult(ok=ok, operation_id=op_id, drawing_before=before, drawing_after=after,
                           created_handles=created, expected_state=expected,
                           actual_state={"graph": {"nodes": len(net["graph"]["nodes"]),
                                                  "edges": len(net["graph"]["edges"])}},
                           validations=[{"check": k["check"], "ok": k["ok"]} for k in v["checks"]],
                           error_code=None if ok else (v.get("code") or "VALIDATION_FAIL"),
                           error=None if ok else "routed network failed validation").to_dict()
