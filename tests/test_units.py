import pytest
from cad_agent.errors import CadError
from cad_agent.units import UnitContext


def test_mm_drawing():
    u = UnitContext(4)
    assert abs(u.to_drawing_units(300, "mm") - 300) < 1e-9
    assert abs(u.to_drawing_units(30, "cm") - 300) < 1e-9


def test_meter_drawing():
    u = UnitContext(6)
    assert abs(u.to_drawing_units(300, "mm") - 0.3) < 1e-9


def test_unknown_units_fail():
    with pytest.raises(CadError) as ei:
        UnitContext(0)
    assert ei.value.code == "UNKNOWN_UNITS"


def test_configured_fallback():
    u = UnitContext(0, configured_fallback_mm_per_unit=1.0, configured_unit_name="mm-assumed-by-operator")
    assert abs(u.to_drawing_units(10, "mm") - 10) < 1e-9


def test_bad_unit_name():
    u = UnitContext(4)
    with pytest.raises(CadError):
        u.to_drawing_units(1, "furlongs")
