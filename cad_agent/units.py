"""Unit handling. Never guess scale: INSUNITS is authoritative."""
from __future__ import annotations

from .errors import CadError, UNKNOWN_UNITS

# DXF $INSUNITS codes -> mm per drawing unit
_MM_PER_UNIT = {
    0: None,   # unitless -> unknown, must FAIL unless configured
    1: 25.4,   # inches
    2: 304.8,  # feet
    3: 1609344.0,  # miles
    4: 1.0,    # mm
    5: 10.0,   # cm
    6: 1000.0,  # m
    7: 1e-6,   # km -> mm
    8: 25.4 / 1000.0,  # microinches
    9: 25.4 / 1000.0 * 1000.0,  # mils (0.0254mm)? keep simple
    10: 914.4,  # yards
    11: 1e-9,  # angstroms -> mm
    12: 1e-6,  # nm -> mm
    13: 1e-3,  # um -> mm
    14: 1000.0,  # dm -> mm (100mm)? dm=100mm
    15: 10000.0,  # dam
    16: 100000.0,  # hm
    17: 1000000.0,  # Gm
    18: 149597870700000.0,  # AU
    19: 9.4607e18,  # ly
    20: 3.0857e19,  # pc
    21: 304.8 / 1000000.0,  # US survey feet approx
    22: 25.4,  # US survey inch
    23: 304.8,  # US survey yard
    24: 1609344.0,  # US survey mile
}

_UNIT_ALIASES = {
    "mm": 1.0, "millimeter": 1.0, "millimetre": 1.0,
    "cm": 10.0, "centimeter": 10.0,
    "m": 1000.0, "meter": 1000.0, "metre": 1000.0,
    "in": 25.4, "inch": 25.4,
    "ft": 304.8, "foot": 304.8, "feet": 304.8,
}


class UnitContext:
    """Converts explicit user units to drawing units using $INSUNITS."""

    def __init__(self, insunits: int, configured_fallback_mm_per_unit: float | None = None,
                 configured_unit_name: str | None = None):
        self.insunits = int(insunits or 0)
        mm_per_unit = _MM_PER_UNIT.get(self.insunits)
        if mm_per_unit is None:
            if configured_fallback_mm_per_unit is not None:
                mm_per_unit = float(configured_fallback_mm_per_unit)
                self.resolved_by = f"configured:{configured_unit_name or 'fallback'}"
            else:
                raise CadError(UNKNOWN_UNITS,
                               f"$INSUNITS={self.insunits} is unitless/undefined and no configured fallback. "
                               f"Refusing to guess scale.",
                               {"insunits": self.insunits})
        else:
            self.resolved_by = f"insunits:{self.insunits}"
        self.mm_per_unit = float(mm_per_unit)

    def to_drawing_units(self, value: float, unit: str) -> float:
        key = unit.strip().lower()
        if key not in _UNIT_ALIASES:
            raise CadError(UNKNOWN_UNITS, f"Unknown unit '{unit}'. Use mm/cm/m/in/ft.",
                           {"unit": unit})
        mm = float(value) * _UNIT_ALIASES[key]
        return mm / self.mm_per_unit

    def from_drawing_units(self, value: float, unit: str) -> float:
        key = unit.strip().lower()
        if key not in _UNIT_ALIASES:
            raise CadError(UNKNOWN_UNITS, f"Unknown unit '{unit}'.", {"unit": unit})
        mm = float(value) * self.mm_per_unit
        return mm / _UNIT_ALIASES[key]

    def to_dict(self) -> dict:
        return {"insunits": self.insunits, "mm_per_unit": self.mm_per_unit,
                "resolved_by": self.resolved_by}
