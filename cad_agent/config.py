"""Project configuration loader. Single source for domain policy (units, layers, tolerances).

Unit fallback policy (explicit, never guessed):
- If the drawing $INSUNITS is defined (!=0), it is authoritative.
- If $INSUNITS==0 and `units.configured_fallback` (mm per drawing unit) is set in
  config/electrical-cad.yaml, use it and record resolved_by="project_fallback:<name>".
- Otherwise FAIL with UNKNOWN_UNITS. Never infer from visual dimensions.
"""
from __future__ import annotations

import os

import yaml

from .errors import CadError
from .units import UnitContext

_DEFAULT_CANDIDATES = [
    os.environ.get("CAD_CONFIG", ""),
    os.path.join(os.getcwd(), "config", "electrical-cad.yaml"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "electrical-cad.yaml"),
]

_config_cache: dict = {}


def find_config(path: str | None = None) -> str | None:
    if path and os.path.isfile(path):
        return os.path.abspath(path)
    for c in _DEFAULT_CANDIDATES:
        if c and os.path.isfile(c):
            return os.path.abspath(c)
    return None


def load_config(path: str | None = None) -> dict:
    cfg_path = find_config(path)
    if not cfg_path:
        return {}
    if cfg_path not in _config_cache:
        with open(cfg_path, encoding="utf-8") as f:
            _config_cache[cfg_path] = yaml.safe_load(f) or {}
    return _config_cache[cfg_path]


def resolve_unit_context(insunits: int, config_path: str | None = None) -> UnitContext:
    """Build UnitContext honoring the explicit fallback policy. Never guesses."""
    cfg = load_config(config_path)
    units = (cfg.get("units") or {})
    fallback = units.get("configured_fallback")
    name = units.get("configured_unit_name")
    if int(insunits or 0) != 0:
        return UnitContext(int(insunits))
    if fallback is not None:
        return UnitContext(0, configured_fallback_mm_per_unit=float(fallback),
                           configured_unit_name=name or "project_fallback")
    raise CadError("UNKNOWN_UNITS",
                   "$INSUNITS is unitless (0) and config units.configured_fallback is not set. "
                   "Set units.configured_fallback in config/electrical-cad.yaml (with operator sign-off) "
                   "or abort. Refusing to guess scale.",
                   {"insunits": insunits, "config": find_config(config_path)})


def unit_fallback_policy(config_path: str | None = None) -> str:
    cfg = load_config(config_path)
    fb = (cfg.get("units") or {}).get("configured_fallback")
    nm = (cfg.get("units") or {}).get("configured_unit_name")
    if fb is None:
        return "none configured -> UNKNOWN_UNITS FAIL (no guessing)"
    return f"project fallback {fb} mm/unit ({nm or 'unnamed'}) -> resolved_by logged per operation"


def wall_layers(config_path: str | None = None) -> list:
    cfg = load_config(config_path)
    layers = ((cfg.get("layers") or {}).get("walls")) or []
    return layers or ["ARQ", "ARQ-PAREDE", "PAREDE", "A-WALL", "ARCH", "WALL"]


def protected_layers(config_path: str | None = None) -> list:
    cfg = load_config(config_path)
    return ((cfg.get("layers") or {}).get("protected")) or []
