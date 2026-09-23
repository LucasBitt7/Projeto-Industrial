"""Synthetic fixtures. NEVER touch production drawings; tests build their own DXF."""
import ezdxf
import pytest


def make_fixture(path, insunits=4):
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = insunits
    msp = doc.modelspace()
    # wall on PAREDE layer
    wall = msp.add_line((0, 0), (10000, 0))
    wall.dxf.layer = "PAREDE"
    # second wall (vertical, other room)
    wall2 = msp.add_line((10000, 0), (10000, 6000))
    wall2.dxf.layer = "PAREDE"
    # outlet block def + instance near wall
    if "TUG" not in doc.blocks:
        blk = doc.blocks.new("TUG")
        blk.add_circle((0, 0), 50)
    outlet = msp.add_blockref("TUG", (1000, 100))
    outlet.dxf.layer = "ELE-TUG"
    # panel group QDF: outline + fill + diagonal + label (coherent)
    outline = msp.add_lwpolyline([(3000, 0), (3600, 0), (3600, 800), (3000, 800)], close=True)
    outline.dxf.layer = "ELE-QUADRO"
    hatch = msp.add_hatch(color=9)
    hatch.dxf.layer = "ELE-QUADRO"
    hatch.paths.add_polyline_path([(3100, 100), (3500, 100), (3500, 700), (3100, 700)], is_closed=True)
    diag = msp.add_line((3000, 0), (3600, 800))
    diag.dxf.layer = "ELE-QUADRO"
    label = msp.add_text("QDF", height=200)
    label.dxf.insert = (3300, 900)
    label.dxf.layer = "ELE-QUADRO"
    # texts for room semantics (BANHEIRO bbox [0,0,4000,3000] per config).
    # NOTE: circuit tags live on ELE-CIRCUITO (plain labels), NOT on ELE-CALLOUT,
    # which is reserved for complete callout groups (circuit + conductor spec).
    t_ok = msp.add_text("T18 - 2x2.5mm", height=150)
    t_ok.dxf.insert = (500, 2000)
    t_ok.dxf.layer = "ELE-CIRCUITO"
    # conduit tree on ELETRODUTO: trunk + branch sharing node (5000,3000)
    c1 = msp.add_line((5000, 3000), (7000, 3000))
    c1.dxf.layer = "ELETRODUTO"
    c2 = msp.add_line((7000, 3000), (7000, 5000))
    c2.dxf.layer = "ELETRODUTO"
    doc.saveas(path)
    return {
        "wall": wall.dxf.handle, "wall2": wall2.dxf.handle,
        "outlet": outlet.dxf.handle,
        "panel": [outline.dxf.handle, hatch.dxf.handle, diag.dxf.handle, label.dxf.handle],
        "outline": outline.dxf.handle,
    }


@pytest.fixture
def fx(tmp_path):
    p = str(tmp_path / "fixture.dxf")
    handles = make_fixture(p)
    return p, handles


@pytest.fixture
def fx_unitless(tmp_path):
    p = str(tmp_path / "unitless.dxf")
    handles = make_fixture(p, insunits=0)
    return p, handles
