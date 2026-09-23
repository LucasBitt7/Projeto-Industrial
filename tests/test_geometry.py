import math
from cad_agent import geometry as G


def test_project_point_to_line():
    x, y, t = G.project_point_to_line(5, 5, 0, 0, 10, 0)
    assert abs(x - 5) < 1e-9 and abs(y) < 1e-9 and abs(t - 0.5) < 1e-9


def test_project_point_to_polyline():
    r = G.project_point_to_polyline(5, 5, [(0, 0), (10, 0), (10, 10)])
    assert abs(r["x"] - 5) < 1e-9 and r["seg_index"] == 0


def test_midpoint_and_along():
    assert G.midpoint((0, 0), (10, 10)) == (5, 5)
    x, y = G.point_along_line(0, 0, 10, 0, 3)
    assert abs(x - 3) < 1e-9 and abs(y) < 1e-9


def test_distance_point_segment():
    assert abs(G.distance_point_segment(5, 5, 0, 0, 10, 0) - 5) < 1e-9
    assert abs(G.distance_point_segment(15, 0, 0, 0, 10, 0) - 5) < 1e-9


def test_snap():
    assert G.snap_endpoints((0, 0), (0.5, 0), 1.0)[2] is True
    assert G.snap_endpoints((0, 0), (5, 0), 1.0)[2] is False


def test_bbox():
    assert G.bbox_intersects([0, 0, 2, 2], [1, 1, 3, 3])
    assert not G.bbox_intersects([0, 0, 1, 1], [2, 2, 3, 3])
    assert G.expand_bbox([0, 0, 1, 1], 1) == [-1, -1, 2, 2]


def test_rotations():
    assert abs(G.rotation_parallel_to_wall((0, 0), (10, 0))) < 1e-9
    assert abs(G.rotation_perpendicular_to_wall((0, 0), (10, 0)) - 90) < 1e-9
    assert abs(G.align_entity_to_wall(5, (0, 0), (10, 0), "parallel") - 0) < 1e-9


def test_rigid_clone_preserves_geometry():
    pts = [(0, 0), (3, 0), (3, 4)]
    moved = G.clone_group_preserve_relative_geometry(pts, 10, 20, 90, 0, 0)
    d0 = math.hypot(pts[0][0] - pts[1][0], pts[0][1] - pts[1][1])
    d1 = math.hypot(moved[0][0] - moved[1][0], moved[0][1] - moved[1][1])
    assert abs(d0 - d1) < 1e-9


def test_free_interval():
    free = G.find_free_wall_interval((0, 0), (100, 0), [(0.4, 0.6)], 10, 100, 0.0)
    assert free is not None


def test_orthogonal_route():
    r = G.orthogonal_route((0, 0), (10, 5))
    assert r[0] == (0, 0) and r[-1] == (10, 5) and len(r) == 3


def test_graph_cycle_and_path():
    g = G.polyline_to_graph([[(0, 0), (1, 0), (1, 1), (0, 0)]])
    assert len(G.detect_cycles(g)) >= 1
    g2 = G.polyline_to_graph([[(0, 0), (1, 0), (2, 0)]])
    assert len(G.connected_components(g2)) == 1
    assert G.unique_path(g2, 0, 2) == [0, 1, 2]
    assert G.unique_path(g2, 0, 99) is None
