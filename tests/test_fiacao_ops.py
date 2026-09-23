"""Tests for guarded delete + bound FIACAO callout ops (v04 capability extension).

Builds own fixtures in tmp_path. NEVER touches production drawings.
"""
import ezdxf
import pytest

from cad_agent.drawing import drawing_identity
from cad_agent.fiacao import create_fiacao_callout_bound, delete_entities_guarded


@pytest.fixture()
def fx_dxf(tmp_path):
    p = str(tmp_path / "fx_room_escritorio.dxf")
    doc = ezdxf.new("R2018")
    doc.header["$INSUNITS"] = 6
    msp = doc.modelspace()
    if "FIACAO_LAMP_FNT" not in doc.blocks:
        blk = doc.blocks.new("FIACAO_LAMP_FNT")
        blk.add_attdef("C", (0.079, 0.36), height=0.08)
        blk.add_attdef("B", (-0.014, -0.37), height=0.08)
    src = msp.add_blockref("FIACAO_LAMP_FNT", (10.0, 20.0))
    src.dxf.layer = "_ELT_ELETRODUTOS"
    src.add_attrib("C", "T11", (10.079, 20.36))
    src.add_attrib("B", "# 3x2,5 - (FNT)", (9.986, 19.63))
    for a in src.attribs:
        a.dxf.layer = "ELET_FIAÇÃO"
        a.dxf.color = 4
    edge = msp.add_line((0.0, 0.0), (30.0, 0.0))
    edge.dxf.layer = "_ELT_ELETRODUTOS"
    bad = msp.add_blockref("FIACAO_LAMP_FNT", (50.0, 50.0))
    bad.dxf.layer = "_ELT_ELETRODUTOS"
    bad.add_attrib("C", "TX", (50.079, 50.36))
    bad.add_attrib("B", "# 3x2,5 - (FNT)", (49.986, 49.63))
    doc.saveas(p)
    return p


def rev_of(p):
    return drawing_identity(p).revision_token


def test_delete_identity_ok_and_count(fx_dxf, tmp_path):
    out = str(tmp_path / "out_del.dxf")
    bad_h = None
    doc = ezdxf.readfile(fx_dxf)
    for e in doc.modelspace():
        if e.dxftype() == "INSERT" and any(a.dxf.text == "TX" for a in e.attribs):
            bad_h = e.dxf.handle
    res = delete_entities_guarded(fx_dxf, [bad_h], {"INSERT-notype": {}},
                                  None, rev_of(fx_dxf), True, out)
    assert res["ok"] is True
    # wrong identity refuses
    import copy
    with pytest.raises(Exception):
        delete_entities_guarded(fx_dxf, [bad_h], {bad_h: {"layer": "NOPE"}},
                                None, rev_of(fx_dxf), True, out)
    # real delete removes exactly one
    res2 = delete_entities_guarded(fx_dxf, [bad_h], {bad_h: {"type": "INSERT"}},
                                   1, rev_of(fx_dxf), False, out)
    assert res2["deleted_handles"] == [bad_h]
    doc2 = ezdxf.readfile(out)
    assert bad_h not in doc2.entitydb


def test_delete_never_in_place(fx_dxf):
    import copy
    with pytest.raises(Exception):
        delete_entities_guarded(fx_dxf, ["XX"], None, None, rev_of(fx_dxf), True, fx_dxf)


def test_fiacao_clone_pattern_and_bound(fx_dxf, tmp_path):
    out = str(tmp_path / "out_fia.dxf")
    doc = ezdxf.readfile(fx_dxf)
    src_h = None
    for e in doc.modelspace():
        if e.dxftype() == "INSERT" and any(a.dxf.text == "T11" for a in e.attribs):
            src_h = e.dxf.handle
    # floating refuses
    with pytest.raises(Exception):
        create_fiacao_callout_bound(fx_dxf, src_h, "T13", "# 3x2,5 - (FNT)",
                                    [0.0, 0.0], [30.0, 0.0], [15.0, 5.0],
                                    0.005, rev_of(fx_dxf), True, out)
    # bound dry_run ok, no file written
    r = create_fiacao_callout_bound(fx_dxf, src_h, "T13", "# 3x2,5 - (FNT)",
                                    [0.0, 0.0], [30.0, 0.0], [15.0, 0.0],
                                    0.005, rev_of(fx_dxf), True, out)
    assert r["ok"] is True and r["expected_state"]["bound"] is True
    # real
    r2 = create_fiacao_callout_bound(fx_dxf, src_h, "T13", "# 3x2,5 - (FNT)",
                                     [0.0, 0.0], [30.0, 0.0], [15.0, 0.0],
                                     0.005, rev_of(fx_dxf), False, out)
    h = r2["created_handles"][0]
    d2 = ezdxf.readfile(out)
    ent = d2.entitydb[h]
    assert ent.dxf.layer == "_ELT_ELETRODUTOS"
    got = {a.dxf.tag: a.dxf.text for a in ent.attribs}
    assert got == {"C": "T13", "B": "# 3x2,5 - (FNT)"}
    for a in ent.attribs:
        assert a.dxf.layer == "ELET_FIAÇÃO"
        assert a.dxf.color == 4
        assert a.dxf.height == pytest.approx(0.08)
