"""Tests for cad_agent.parametrize (versioned extension). Synthetic fixtures only."""
import ezdxf
import pytest

from cad_agent.errors import CadError
from cad_agent.parametrize import clone_parametrized
from cad_agent.templates import capture_template


def _doc(path):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    f = msp.add_line((0, 0), (0, 10))
    f.dxf.layer = "L-FRAME"
    t = msp.add_mtext("OLD")
    t.dxf.layer = "L-TXT"
    t.dxf.insert = (1, 5)
    t.dxf.char_height = 0.5
    t.dxf.style = "Standard"
    t.dxf.attachment_point = 1
    doc.saveas(path)
    hs = [str(e.dxf.handle) for e in msp]
    rev = __import__("cad_agent.drawing", fromlist=["drawing_identity"]).drawing_identity(path)
    return hs, rev.revision_token if hasattr(rev, "revision_token") else rev.to_dict()["revision_token"]


def test_parametrized_clone_replaces_and_preserves(tmp_path):
    src = str(tmp_path / "a.dxf")
    hs, rev = _doc(src)
    capture_template(src, hs, "t", template_id="ptpl")
    out = str(tmp_path / "b.dxf")
    res = clone_parametrized(src, "ptpl", 10, 0, text_map={"OLD": "NEW"},
                             out_path=out, expected_revision=rev)
    assert res["ok"] and len(res["created_handles"]) == 2
    back = ezdxf.readfile(out)
    texts = [e.text for e in back.modelspace() if e.dxftype() == "MTEXT"]
    assert sorted(texts) == ["NEW", "OLD"]  # source kept + parametrized clone
    e = [x for x in back.modelspace() if x.dxftype() == "MTEXT"
         and x.text == "NEW"][0]
    assert abs(float(e.dxf.char_height) - 0.5) < 1e-9
    assert tuple(e.dxf.insert)[:2] == (11.0, 5.0)


def test_parametrized_fail_closed(tmp_path):
    src = str(tmp_path / "a.dxf")
    hs, rev = _doc(src)
    capture_template(src, hs, "t", template_id="ptpl2")
    out = str(tmp_path / "b.dxf")
    with pytest.raises(CadError):
        clone_parametrized(src, "ptpl2", 0, 0, text_map={"NOPE": "X"},
                           out_path=out, expected_revision=rev)
    with pytest.raises(CadError):
        clone_parametrized(src, "ptpl2", 0, 0, out_path=src, expected_revision=rev)
    with pytest.raises(CadError):
        clone_parametrized(src, "ptpl2", 0, 0, out_path=out, expected_revision=None)
    r = clone_parametrized(src, "ptpl2", 0, 0, text_map={"OLD": "N"},
                           out_path=out, expected_revision=rev, dry_run=True)
    assert r["ok"] and r["expected_state"]["count"] == 2
    import os
    assert not os.path.exists(out)


def test_handle_rules_extra_group_and_edits(tmp_path):
    import os
    src = str(tmp_path / "a.dxf")
    hs, rev = _doc(src)
    line_h = hs[0]
    capture_template(src, hs, "t", template_id="ptpl3")
    out = str(tmp_path / "b.dxf")
    res = clone_parametrized(
        src, "ptpl3", 0, 0,
        handle_rules={f"base:{line_h}": "ignored-for-line", "extra0:" + hs[1]: "ROW2"},
        extra_groups=[{"handles": [hs[1]], "dx": 0, "dy": -3.0}],
        member_edits=[{"handle": line_h, "op": "translate", "dx": 1.0, "dy": 1.0}],
        out_path=out, expected_revision=rev)
    assert res["ok"] and len(res["created_handles"]) == 3  # base 2 + extra row text
    back = ezdxf.readfile(out)
    texts = sorted(e.text for e in back.modelspace() if e.dxftype() == "MTEXT")
    assert texts == ["OLD", "OLD", "ROW2"]  # source + base clone + extra clone
    lines = [e for e in back.modelspace() if e.dxftype() == "LINE"]
    assert any(abs(e.dxf.start.x - 1.0) < 1e-9 for e in lines)  # translated clone
    assert os.path.exists(out)


def test_extra_texts_and_dry_run_edits(tmp_path):
    import os
    from cad_agent.templates import get_template
    src = str(tmp_path / "a.dxf")
    hs, rev = _doc(src)
    capture_template(src, hs, "t", template_id="ptpl4")
    ax, ay = get_template("ptpl4")["anchor"]
    out = str(tmp_path / "b.dxf")
    xt = {"content": "NOTE", "layer": "L-TXT", "style": "Standard", "height": 0.5,
          "attachment": 1, "dx": 5.0, "dy": -2.0}
    r = clone_parametrized(src, "ptpl4", 0, 0, extra_texts=[xt],
                           member_edits=[{"handle": hs[0], "op": "extend_y_min",
                                          "delta": -4.0}],
                           out_path=out, expected_revision=rev, dry_run=True)
    assert r["ok"] and r["expected_state"]["count"] == 3
    x0, y0, x1, y1 = r["expected_state"]["bbox"]
    assert y0 == pytest.approx(-4.0) and (x1, y1) == pytest.approx((ax + 5.0, 10.0))
    res = clone_parametrized(src, "ptpl4", 0, 0, extra_texts=[xt],
                             member_edits=[{"handle": hs[0], "op": "extend_y_min",
                                            "delta": -4.0}],
                             out_path=out, expected_revision=rev)
    assert res["ok"] and len(res["created_handles"]) == 3
    back = ezdxf.readfile(out)
    assert sorted(e.text for e in back.modelspace()
                  if e.dxftype() == "MTEXT") == ["NOTE", "OLD", "OLD"]
    assert os.path.exists(out)
