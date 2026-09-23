"""Deterministic geometry kernel. Pure functions, no CAD I/O, fully unit-tested."""
from __future__ import annotations

import math
from typing import Iterable


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _mul(a, s):
    return (a[0] * s, a[1] * s)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _norm(a):
    return math.hypot(a[0], a[1])


def _normalize(a):
    n = _norm(a)
    if n == 0:
        return (0.0, 0.0)
    return (a[0] / n, a[1] / n)


def distance_point_segment(px, py, x1, y1, x2, y2) -> float:
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def project_point_to_line(px, py, x1, y1, x2, y2):
    """Orthogonal projection onto infinite line; returns (x, y, t) with t along segment param."""
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return (x1, y1, 0.0)
    t = ((px - x1) * dx + (py - y1) * dy) / l2
    return (x1 + t * dx, y1 + t * dy, t)


def project_point_to_polyline(px, py, points) -> dict:
    """Nearest projection onto polyline. Returns {x, y, seg_index, t, distance}."""
    best = None
    pts = [tuple(map(float, p)) for p in points]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        qx, qy, t = project_point_to_line(px, py, x1, y1, x2, y2)
        tc = max(0.0, min(1.0, t))
        cx, cy = x1 + tc * (x2 - x1), y1 + tc * (y2 - y1)
        d = math.hypot(px - cx, py - cy)
        if best is None or d < best["distance"]:
            best = {"x": cx, "y": cy, "seg_index": i, "t": tc, "distance": d}
    if best is None:
        raise ValueError("polyline needs >= 2 points")
    return best


def nearest_point_on_wall(px, py, wall_p1, wall_p2) -> dict:
    qx, qy, t = project_point_to_line(px, py, wall_p1[0], wall_p1[1], wall_p2[0], wall_p2[1])
    tc = max(0.0, min(1.0, t))
    cx = wall_p1[0] + tc * (wall_p2[0] - wall_p1[0])
    cy = wall_p1[1] + tc * (wall_p2[1] - wall_p1[1])
    return {"x": cx, "y": cy, "t": tc, "distance": math.hypot(px - cx, py - cy)}


def point_along_line(x1, y1, x2, y2, distance: float):
    v = _normalize(_sub((x2, y2), (x1, y1)))
    return (x1 + v[0] * distance, y1 + v[1] * distance)


def midpoint(a, b):
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def nearest_endpoint(px, py, points):
    best, bestd = None, None
    for p in points:
        d = math.hypot(px - p[0], py - p[1])
        if bestd is None or d < bestd:
            best, bestd = (p[0], p[1]), d
    return {"x": best[0], "y": best[1], "distance": bestd}


def snap_endpoints(p, q, tol: float):
    """Snap p to q if within tol. Returns (x, y, snapped: bool)."""
    if math.hypot(p[0] - q[0], p[1] - q[1]) <= tol:
        return (q[0], q[1], True)
    return (p[0], p[1], False)


def _seg_intersection(p1, p2, p3, p4, eps=1e-9):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(d) < eps:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / d
    if -eps <= t <= 1 + eps and -eps <= u <= 1 + eps:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def segment_intersections(segments_a, segments_b=None) -> list:
    """segments: list of ((x1,y1),(x2,y2)). If b None, self-intersections of a."""
    b = segments_b if segments_b is not None else segments_a
    out = []
    for i, s1 in enumerate(segments_a):
        for j, s2 in enumerate(b):
            if segments_b is None and j <= i:
                continue
            pt = _seg_intersection(s1[0], s1[1], s2[0], s2[1])
            if pt is not None:
                out.append({"a": i, "b": j, "x": pt[0], "y": pt[1]})
    return out


def bbox_of_points(points) -> list:
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def bbox_intersects(a, b, tol: float = 0.0) -> bool:
    return not (a[2] + tol < b[0] or b[2] + tol < a[0] or a[3] + tol < b[1] or b[3] + tol < a[1])


def expand_bbox(bbox, amount: float) -> list:
    return [bbox[0] - amount, bbox[1] - amount, bbox[2] + amount, bbox[3] + amount]


def bbox_contains_point(bbox, x, y, tol=0.0) -> bool:
    return (bbox[0] - tol) <= x <= (bbox[2] + tol) and (bbox[1] - tol) <= y <= (bbox[3] + tol)


def rotation_parallel_to_wall(wall_p1, wall_p2) -> float:
    """Angle in degrees of wall direction."""
    return math.degrees(math.atan2(wall_p2[1] - wall_p1[1], wall_p2[0] - wall_p1[0]))


def rotation_perpendicular_to_wall(wall_p1, wall_p2) -> float:
    return rotation_parallel_to_wall(wall_p1, wall_p2) + 90.0


def align_entity_to_wall(entity_angle_deg: float, wall_p1, wall_p2, mode: str = "parallel") -> float:
    """Smallest equivalent target angle (degrees) parallel/perpendicular to wall."""
    if mode == "perpendicular":
        target = rotation_perpendicular_to_wall(wall_p1, wall_p2)
    else:
        target = rotation_parallel_to_wall(wall_p1, wall_p2)
    # normalize delta to [-90, 90] for symmetric entities, else [-180,180]
    delta = (target - entity_angle_deg) % 180.0
    if delta > 90:
        delta -= 180
    return entity_angle_deg + delta


def _rotate_point(px, py, cx, cy, angle_deg):
    r = math.radians(angle_deg)
    dx, dy = px - cx, py - cy
    return (cx + dx * math.cos(r) - dy * math.sin(r), cy + dx * math.sin(r) + dy * math.cos(r))


def rigid_transform_point(px, py, dx, dy, angle_deg, cx=0.0, cy=0.0):
    rx, ry = _rotate_point(px, py, cx, cy, angle_deg)
    return (rx + dx, ry + dy)


def translate_group(points, dx, dy):
    return [(p[0] + dx, p[1] + dy) for p in points]


def rotate_group_rigid(points, cx, cy, angle_deg):
    return [_rotate_point(p[0], p[1], cx, cy, angle_deg) for p in points]


def clone_group_preserve_relative_geometry(points, dx, dy, angle_deg=0.0, cx=0.0, cy=0.0):
    """Rotate about (cx,cy) then translate. Preserves all relative geometry."""
    return [rigid_transform_point(p[0], p[1], dx, dy, angle_deg, cx, cy) for p in points]


def place_entity_on_wall(entity_xy, wall_p1, wall_p2, offset: float = 0.0) -> dict:
    """Project entity anchor onto wall, then offset along wall normal by `offset`."""
    proj = nearest_point_on_wall(entity_xy[0], entity_xy[1], wall_p1, wall_p2)
    vx, vy = _normalize(_sub(tuple(wall_p2), tuple(wall_p1)))
    nx, ny = -vy, vx
    return {"x": proj["x"] + nx * offset, "y": proj["y"] + ny * offset,
            "t": proj["t"], "distance": proj["distance"]}


def find_free_wall_interval(wall_p1, wall_p2, occupied_t: list, need_length: float,
                             wall_length: float, clearance: float = 0.0) -> dict | None:
    """occupied_t: list of (t0,t1) in param space [0,1]. Returns {t_center, x, y} or None."""
    need_t = need_length / wall_length if wall_length > 0 else 1.0
    clr_t = clearance / wall_length if wall_length > 0 else 0.0
    spans = sorted([(max(0.0, a - clr_t), min(1.0, b + clr_t)) for a, b in occupied_t])
    # merge
    merged: list = []
    for s in spans:
        if not merged or s[0] > merged[-1][1]:
            merged.append([s[0], s[1]])
        else:
            merged[-1][1] = max(merged[-1][1], s[1])
    gaps = []
    prev = 0.0
    for s in merged:
        gaps.append((prev, s[0]))
        prev = s[1]
    gaps.append((prev, 1.0))
    for g0, g1 in gaps:
        if (g1 - g0) >= need_t:
            tc = (g0 + g1) / 2.0
            x = wall_p1[0] + tc * (wall_p2[0] - wall_p1[0])
            y = wall_p1[1] + tc * (wall_p2[1] - wall_p1[1])
            return {"t_center": tc, "x": x, "y": y, "gap": (g0, g1)}
    return None


def orthogonal_route(start, end, first: str = "x") -> list:
    """L-shaped manhattan route. Returns [start, corner, end]."""
    sx, sy = start; ex, ey = end
    if first == "x":
        corner = (ex, sy)
    else:
        corner = (sx, ey)
    if corner == start or corner == end:
        return [tuple(start), tuple(end)]
    return [tuple(start), tuple(corner), tuple(end)]


def route_with_clearance(start, end, obstacles: list, clearance: float, first: str = "x") -> list:
    """Orthogonal route; if corner/legs violate expanded obstacle bboxes, try other orientation,
    else insert a detour offset. Deterministic, no guessing."""
    cand_x = orthogonal_route(start, end, "x")
    cand_y = orthogonal_route(start, end, "y")
    for cand in (cand_x, cand_y):
        if not _polyline_hits_obstacles(cand, obstacles, clearance):
            return cand
    # detour: offset perpendicular by clearance + margin
    mx, my = (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0
    dx, dy = end[0] - start[0], end[1] - start[1]
    n = _normalize((-dy, dx))
    off = clearance * 2.0 + 1.0
    via = (mx + n[0] * off, my + n[1] * off)
    return [tuple(start), orthogonal_route(start, via, first)[1], tuple(via),
            orthogonal_route(via, end, first)[1], tuple(end)]


def _polyline_hits_obstacles(polyline, obstacles, clearance) -> bool:
    for i in range(len(polyline) - 1):
        a, b = polyline[i], polyline[i + 1]
        for ob in obstacles:
            eb = expand_bbox(ob, clearance)
            if _segment_hits_bbox(a, b, eb):
                return True
    return False


def _segment_hits_bbox(a, b, bbox) -> bool:
    if bbox_contains_point(bbox, a[0], a[1]) or bbox_contains_point(bbox, b[0], b[1]):
        return True
    corners = [(bbox[0], bbox[1]), (bbox[2], bbox[1]), (bbox[2], bbox[3]), (bbox[0], bbox[3])]
    edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    for e in edges:
        if _seg_intersection(a, b, e[0], e[1]) is not None:
            return True
    return False


# ---- graph utilities for conduit networks ----

def _key(p, tol=1e-6):
    return (round(p[0] / tol) * tol, round(p[1] / tol) * tol)


def polyline_to_graph(polylines, snap_tol: float = 1e-6) -> dict:
    """Build node/edge graph from polylines. Nodes keyed by snapped coord."""
    nodes: dict = {}
    edges: list = []

    def nid(p):
        k = (round(p[0] / max(snap_tol, 1e-9), 6), round(p[1] / max(snap_tol, 1e-9), 6))
        if k not in nodes:
            nodes[k] = {"id": len(nodes), "x": p[0], "y": p[1], "key": k}
        return nodes[k]["id"]

    for pl in polylines:
        for i in range(len(pl) - 1):
            a, b = tuple(pl[i]), tuple(pl[i + 1])
            na, nb = nid(a), nid(b)
            if na != nb:
                edges.append((na, nb))
    adj = {n["id"]: set() for n in nodes.values()}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return {"nodes": list(nodes.values()), "edges": edges, "adj": {k: sorted(v) for k, v in adj.items()}}


def connected_components(graph: dict) -> list:
    adj = graph["adj"]
    seen: set = set()
    comps = []
    for n in adj:
        if n in seen:
            continue
        stack, comp = [n], []
        seen.add(n)
        while stack:
            c = stack.pop()
            comp.append(c)
            for m in adj[c]:
                if m not in seen:
                    seen.add(m)
                    stack.append(m)
        comps.append(sorted(comp))
    return comps


def detect_cycles(graph: dict) -> list:
    adj = graph["adj"]
    visited: set = set()
    cycles = []

    def dfs(u, parent, path):
        visited.add(u)
        path.append(u)
        for v in adj[u]:
            if v == parent:
                continue
            if v in path:
                cycles.append(path[path.index(v):] + [v])
            elif v not in visited:
                dfs(v, u, path)
        path.pop()

    for n in adj:
        if n not in visited:
            dfs(n, -1, [])
    return cycles


def unique_path(graph: dict, src: int, dst: int) -> list | None:
    """BFS shortest path; None if disconnected."""
    from collections import deque
    adj = graph["adj"]
    prev = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        if u == dst:
            break
        for v in adj.get(u, []):
            if v not in prev:
                prev[v] = u
                q.append(v)
    if dst not in prev:
        return None
    path, c = [], dst
    while c is not None:
        path.append(c)
        c = prev[c]
    return list(reversed(path))


def orphan_endpoints(graph: dict) -> list:
    """Degree-1 nodes (endpoints). Caller decides which are legitimate terminals."""
    return [n for n, nbrs in graph["adj"].items() if len(nbrs) == 1]
