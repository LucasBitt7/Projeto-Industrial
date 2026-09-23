"""Identity, revision, backends, scope guard, template integrity unit tests."""
import pytest
from cad_agent.backends.base import resolve_backend
from cad_agent.drawing import assert_revision, drawing_identity
from cad_agent.entities import get_entity
from cad_agent.errors import CadError
from cad_agent.templates import validate_template_integrity
from cad_agent.validators import validate_no_changes_outside_scope
import shutil


def test_identity_and_revision(fx):
    path, h = fx
    ident = drawing_identity(path)
    assert ident.insunits == 4
    assert ident.entity_count > 0
    assert len(ident.revision_token) == 64
    assert_revision(path, ident.revision_token)  # no raise
    with pytest.raises(CadError) as ei:
        assert_revision(path, "0" * 64)
    assert ei.value.code == "DRAWING_REVISION_MISMATCH"


def test_backend_explicit_rejects_auto():
    import os
    os.environ.pop("CAD_BACKEND", None)
    with pytest.raises(CadError):
        resolve_backend("auto")
    be = resolve_backend("file")
    assert be.name == "file"


def test_live_backend_fails_closed(monkeypatch):
    monkeypatch.delenv("CAD_LIVE_ENDPOINT", raising=False)
    monkeypatch.delenv("AUTOCAD_MCP_IPC", raising=False)
    from cad_agent.backends.autocad_backend import AutoCadLiveBackend
    with pytest.raises(CadError) as ei:
        AutoCadLiveBackend()
    assert ei.value.code == "BACKEND_UNAVAILABLE"


def test_handles_are_identity(fx):
    path, h = fx
    ref = get_entity(path, h["outlet"])
    assert ref["handle"] == h["outlet"]
    assert ref["type"] == "INSERT"
    with pytest.raises(CadError) as ei:
        get_entity(path, "FFFF")
    assert ei.value.code == "ENTITY_NOT_FOUND"


def test_scope_guard_pass_and_violation(fx, tmp_path):
    path, h = fx
    after = str(tmp_path / "after.dxf")
    shutil.copy(path, after)
    # in-scope scale: whole drawing bbox => pass
    scope = {"allowed_bbox": [-100, -100, 20000, 10000]}
    r = validate_no_changes_outside_scope(path, after, scope)
    assert r["ok"]
    # modify after: move outlet far outside a tight scope
    import ezdxf
    doc = ezdxf.readfile(after)
    for e in doc.modelspace():
        try:
            if str(e.dxf.handle) == h["outlet"]:
                e.dxf.insert = (99999, 99999)
        except Exception:
            pass
    doc.saveas(after)
    tight = {"allowed_bbox": [0, 0, 5000, 5000]}
    r2 = validate_no_changes_outside_scope(path, after, tight)
    assert not r2["ok"] and r2["code"] == "SCOPE_VIOLATION"


def test_template_integrity_ok_and_broken(fx, tmp_path):
    import ezdxf
    path, h = fx
    ok = validate_template_integrity(path, h["panel"])
    assert ok["ok"], ok
    # break: displace fill far away (BUG 1 shape)
    broken = str(tmp_path / "broken.dxf")
    shutil.copy(path, broken)
    doc = ezdxf.readfile(broken)
    for e in doc.modelspace():
        try:
            if str(e.dxf.handle) == h["panel"][1]:
                for p in e.paths:
                    pass
                # hatch move: shift via transform of stored paths is complex; instead move outline away
        except Exception:
            pass
    # simpler break: move the LABEL far outside outline
    for e in doc.modelspace():
        try:
            if str(e.dxf.handle) == h["panel"][3]:
                e.dxf.insert = (90000, 90000)
        except Exception:
            pass
    doc.saveas(broken)
    bad = validate_template_integrity(broken, h["panel"])
    assert not bad["ok"] and bad["code"] == "TEMPLATE_INTEGRITY_FAIL"
