"""Policy tests: write-requires-inspection, bypass guard, false-completion gate."""
import json
import subprocess
import pytest
from cad_agent.errors import CadError
from cad_agent.guard import guard_check, is_adhoc_cad_write


def _bridge(op, args):
    p = subprocess.run(["python3", "cad_agent/tool_bridge.py", op, json.dumps(args)],
                       capture_output=True, text=True)
    return json.loads(p.stdout or "{}"), p.returncode


def test_write_without_inspection_refused(fx, tmp_path):
    import shutil
    path, h = fx
    out = str(tmp_path / "w.dxf")
    shutil.copy(path, out)
    # no expected_revision at all
    res, _ = _bridge("move_along_wall", {"drawing": out, "entity_handle": h["outlet"],
                                         "wall_handle": h["wall"], "displacement": 300,
                                         "out_path": str(tmp_path / "w2.dxf")})
    assert res["ok"] is False and res["error_code"] == "WRITE_WITHOUT_INSPECTION", res
    # stale revision also refused
    res2, _ = _bridge("move_along_wall", {"drawing": out, "entity_handle": h["outlet"],
                                          "wall_handle": h["wall"], "displacement": 300,
                                          "expected_revision": "0" * 64,
                                          "out_path": str(tmp_path / "w3.dxf")})
    assert res2["ok"] is False and res2["error_code"] == "DRAWING_REVISION_MISMATCH", res2


def test_all_write_ops_require_revision(fx, tmp_path):
    import shutil
    path, h = fx
    out = str(tmp_path / "z.dxf")
    shutil.copy(path, out)
    for op, args in [
        ("clone_template", {"drawing": out, "template_id": "x", "dx": 1, "dy": 1}),
        ("place_panel", {"drawing": out, "template_id": "x", "wall_handle": h["wall"]}),
        ("route_conduit", {"drawing": out, "source_handle": h["outlet"], "destination_handles": [h["outlet"]]}),
        ("create_callout", {"drawing": out, "conduit_edge": {"x": 0, "y": 0},
                            "circuits": ["T19"], "conductor_spec": "3x2.5mm"}),
    ]:
        res, _ = _bridge(op, args)
        assert res["error_code"] == "WRITE_WITHOUT_INSPECTION", (op, res)


def test_guard_adhoc_write_refused():
    assert is_adhoc_cad_write("python3 fix.py planta.dxf --saveas out.dxf") is True
    r = guard_check("python3 -c \"import ezdxf; d=ezdxf.readfile('a.dxf'); d.saveas('b.dxf')\"")
    assert r["ok"] is False and r["error_code"] == "WRITE_BYPASS_REFUSED"


def test_guard_allows_pipeline_and_readonly():
    assert is_adhoc_cad_write("python3 cad_agent/tool_bridge.py move_along_wall '{...dxf...}'") is False
    assert is_adhoc_cad_write("python3 -m cad_agent inspect planta.dxf") is False
    assert is_adhoc_cad_write("python3 -m pytest tests/ -q") is False
    assert guard_check("python3 -m cad_agent inspect planta.dxf")["ok"] is True


def test_false_completion_is_fail():
    from cad_agent.validators import completion_gate
    # executor saved fine, but validator found a collision
    g = completion_gate(execution_ok=True, readback_ok=True, scope_ok=True,
                        validators_ok=False, artifact_identity_ok=True)
    assert g["status"] == "FAIL", g
    # only all-true passes
    g2 = completion_gate(True, True, True, True, True)
    assert g2["status"] == "PASS"
