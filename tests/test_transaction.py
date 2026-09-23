"""Transaction + artifact registry tests."""
import shutil
import pytest
from cad_agent.artifacts import create_artifact_dir, versioned_output, write_manifest
from cad_agent.drawing import drawing_identity
from cad_agent.errors import CadError
from cad_agent.transaction import FileTransaction


def test_transaction_commit_pass(fx, tmp_path):
    import ezdxf
    path, h = fx
    out = str(tmp_path / "tx_out.dxf")
    scope = {"allowed_bbox": [-100, -100, 20000, 10000]}
    tx = FileTransaction(path, out, scope=scope, plan_hash="abc")
    doc = ezdxf.readfile(tx.working_path)
    for e in doc.modelspace():
        try:
            if str(e.dxf.handle) == h["outlet"]:
                e.dxf.insert = (float(e.dxf.insert.x) + 50, float(e.dxf.insert.y))
        except Exception:
            pass
    doc.saveas(tx.working_path)
    tx.record("move_outlet", {"handle": h["outlet"]})
    m = tx.commit()
    assert m["status"] == "PASS"
    assert drawing_identity(out).entity_count == drawing_identity(path).entity_count


def test_transaction_scope_violation_discards(fx, tmp_path):
    import ezdxf
    path, h = fx
    out = str(tmp_path / "tx_bad.dxf")
    tx = FileTransaction(path, out, scope={"allowed_bbox": [0, 0, 10, 10]})
    doc = ezdxf.readfile(tx.working_path)
    for e in doc.modelspace():
        try:
            if str(e.dxf.handle) == h["outlet"]:
                e.dxf.insert = (float(e.dxf.insert.x) + 50, float(e.dxf.insert.y))
        except Exception:
            pass
    doc.saveas(tx.working_path)
    with pytest.raises(CadError) as ei:
        tx.commit()
    assert ei.value.code == "VALIDATION_FAIL"


def test_transaction_refuses_inplace(fx, tmp_path):
    path, h = fx
    with pytest.raises(CadError):
        FileTransaction(path, path)


def test_artifact_registry(tmp_path):
    d = create_artifact_dir("test123")
    mp = write_manifest("test123", {"status": "PASS"})
    assert "test123" in mp
    v = versioned_output("recapadora", "tug", "abc123", 27)
    assert "recapadora_tug_v27_abc123.dxf" in v
