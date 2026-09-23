"""Integration tests A-J (spec section 41). All on synthetic fixture copies."""
import shutil
import pytest
import ezdxf
from cad_agent.drawing import drawing_identity
from cad_agent.errors import CadError


def test_A_move_outlet(fx, tmp_path):
    from cad_agent.electrical import electrical_move_outlet_along_wall
    path, h = fx
    out = str(tmp_path / "moved.dxf")
    shutil.copy(path, out)
    ident = drawing_identity(out)
    # dry run first
    dry = electrical_move_outlet_along_wall(out, h["outlet"], h["wall"], 300, "mm",
                                            expected_revision=ident.revision_token,
                                            dry_run=True, out_path=out)
    assert dry["ok"]
    real = electrical_move_outlet_along_wall(out, h["outlet"], h["wall"], 300, "mm",
                                             expected_revision=ident.revision_token,
                                             out_path=out)
    assert real["ok"], real
    from cad_agent.entities import get_entity
    rb = get_entity(out, h["outlet"])
    assert abs(rb["insertion_point"][0] - 1300) < 0.01  # 1000 + 300 along +X wall


def test_B_wrong_revision(fx, tmp_path):
    from cad_agent.electrical import electrical_move_outlet_along_wall
    path, h = fx
    out = str(tmp_path / "b.dxf")
    shutil.copy(path, out)
    with pytest.raises(CadError) as ei:
        electrical_move_outlet_along_wall(out, h["outlet"], h["wall"], 300, "mm",
                                          expected_revision="f" * 64, out_path=out)
    assert ei.value.code == "DRAWING_REVISION_MISMATCH"


def test_C_outside_bbox_refused(fx, tmp_path):
    from cad_agent.electrical import electrical_move_outlet_along_wall
    path, h = fx
    out = str(tmp_path / "c.dxf")
    shutil.copy(path, out)
    ident = drawing_identity(out)
    with pytest.raises(CadError) as ei:
        electrical_move_outlet_along_wall(out, h["outlet"], h["wall"], 300, "mm",
                                          expected_revision=ident.revision_token,
                                          out_path=out, allowed_bbox=[50000, 50000, 60000, 60000])
    assert ei.value.code == "OUT_OF_SCOPE"


def test_D_panel_template_clone(fx, tmp_path):
    import os
    from cad_agent.templates import capture_template, clone_template, validate_template_integrity, REGISTRY_DIR
    path, h = fx
    out = str(tmp_path / "d.dxf")
    shutil.copy(path, out)
    tpl = capture_template(out, h["panel"], "QDF panel", "PANEL_QDF", template_id="test_qdf_tpl")
    try:
        ident = drawing_identity(out)
        res = clone_template(out, "test_qdf_tpl", 5000, 2000, 0.0, expected_revision=ident.revision_token,
                             out_path=out)
        assert res["ok"]
        integ = validate_template_integrity(out, res["created_handles"])
        assert integ["ok"], integ
    finally:
        try:
            os.remove(os.path.join(REGISTRY_DIR, "test_qdf_tpl.json"))
        except OSError:
            pass


def test_E_conduit_tree(fx, tmp_path):
    from cad_agent.conduit import build_network_from_layer, validate_network_graph
    path, h = fx
    net = build_network_from_layer(path, "ELETRODUTO")
    v = validate_network_graph(net["graph"])
    assert v["connected"] and v["cycle_count"] == 0, v


def test_F_orphan_detected(fx, tmp_path):
    path, h = fx
    orph = str(tmp_path / "f.dxf")
    shutil.copy(path, orph)
    doc = ezdxf.readfile(orph)
    msp = doc.modelspace()
    seg = msp.add_line((20000, 20000), (21000, 20000))
    seg.dxf.layer = "ELETRODUTO"
    doc.saveas(orph)
    from cad_agent.conduit import build_network_from_layer, validate_network_graph
    net = build_network_from_layer(orph, "ELETRODUTO")
    v = validate_network_graph(net["graph"])
    assert not v["connected"] and v["code"] == "NETWORK_DISCONNECTED"
    assert len(v["orphan_endpoints"]) >= 2


def test_G_room_circuit(fx, tmp_path):
    path, h = fx
    bad = str(tmp_path / "g.dxf")
    shutil.copy(path, bad)
    doc = ezdxf.readfile(bad)
    msp = doc.modelspace()
    t = msp.add_text("T16", height=150)
    t.dxf.insert = (1000, 1000)  # inside BANHEIRO which allows only T18/T19
    t.dxf.layer = "ELE-CALLOUT"
    doc.saveas(bad)
    from cad_agent.rooms import validate_room
    room = {"room_id": "BANHEIRO", "bbox_or_polygon": {"bbox": [0, 0, 4000, 3000]},
            "allowed_circuits": ["T18", "T19"], "forbidden_circuits": ["T16"]}
    r = validate_room(bad, room)
    assert not r["ok"] and r["code"] == "ROOM_SEMANTIC_VIOLATION"


def test_H_panel_collision(tmp_path):
    import ezdxf as _ez
    from cad_agent.collisions import detect_collisions
    p = str(tmp_path / "h.dxf")
    doc = _ez.new("R2010")
    msp = doc.modelspace()
    if "QDF" not in doc.blocks:
        doc.blocks.new("QDF").add_circle((0, 0), 50)
    if "TUG" not in doc.blocks:
        doc.blocks.new("TUG").add_circle((0, 0), 50)
    a = msp.add_blockref("QDF", (0, 0)); a.dxf.layer = "ELE-QUADRO"
    b = msp.add_blockref("TUG", (0, 0)); b.dxf.layer = "ELE-TUG"
    doc.saveas(p)
    from cad_agent.entities import find_entities
    refs = find_entities(p, limit=10)
    hits = detect_collisions(refs, clearance=2.0)
    assert len(hits) >= 1


def test_I_callout_incomplete(tmp_path):
    import ezdxf as _ez
    p = str(tmp_path / "i.dxf")
    doc = _ez.new("R2010")
    msp = doc.modelspace()
    t = msp.add_mtext("T19")
    t.dxf.layer = "ELE-CALLOUT"
    doc.saveas(p)
    from cad_agent.callouts import validate_callouts
    r = validate_callouts(p)
    assert not r["ok"] and r["code"] == "ORPHAN_CALLOUT"


def test_J_roundtrip(tmp_path):
    import ezdxf as _ez
    from cad_agent.drawing import drawing_fingerprint
    p = str(tmp_path / "j.dxf")
    q = str(tmp_path / "j_rt.dxf")
    doc = _ez.new("R2010")
    doc.header["$INSUNITS"] = 4
    doc.modelspace().add_line((0, 0), (10, 0))
    doc.saveas(p)
    n0 = drawing_fingerprint(p)["entity_count"]
    d2 = _ez.readfile(p)
    d2.saveas(q)
    n1 = drawing_fingerprint(q)["entity_count"]
    assert n0 == n1 == 1
