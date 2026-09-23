"""Session discipline: inspection ledger, write gate, artifact lineage.

- Every agent-facing WRITE op must present the `expected_revision` obtained from
  INSPECT of the SAME file. Missing token -> WRITE_WITHOUT_INSPECTION (refused).
  The token itself is unforgeable proof of inspection (sha256 of canonical state).
- `resolve_current_artifact()` answers "which file is THE drawing now" from the
  transaction registry lineage instead of guessing '*final*.dxf'.
"""
from __future__ import annotations

import glob
import json
import os

from .drawing import assert_revision
from .errors import CadError

REGISTRY_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             ".cad-agent", "transactions")


def require_expected_revision(expected_revision: str | None, drawing: str) -> str:
    if not expected_revision:
        raise CadError("WRITE_WITHOUT_INSPECTION",
                       f"Write to {drawing} refused: no expected_revision. "
                       f"Run INSPECT first (cad-inspect_inspect_drawing) and pass its revision_token. "
                       f"No CAD modification may occur before inspection.",
                       {"drawing": drawing})
    # also verify it is still current (stale plan -> DRAWING_REVISION_MISMATCH)
    assert_revision(drawing, expected_revision)
    return expected_revision


def resolve_current_artifact(project: str | None = None) -> dict:
    """Return the latest PASS transaction manifest (optionally filtered by project
    substring in output_path). FAILs instead of guessing a '*final*' filename."""
    manifests = []
    for mp in glob.glob(os.path.join(REGISTRY_ROOT, "*", "manifest.json")):
        try:
            with open(mp, encoding="utf-8") as f:
                m = json.load(f)
            if m.get("status") == "PASS" and (not project or project in str(m.get("output_path", ""))):
                manifests.append((os.path.getmtime(mp), m))
        except Exception:
            continue
    if not manifests:
        raise CadError("DRAWING_NOT_FOUND",
                       "No PASS artifact in the transaction registry. Inspect the source drawing explicitly; "
                       "never guess '*final*.dxf'.",
                       {"project": project})
    manifests.sort(key=lambda x: x[0])
    latest = manifests[-1][1]
    return {"ok": True, "source": latest.get("source_path"), "output": latest.get("output_path"),
            "final_sha256": latest.get("final_sha256"), "transaction_id": latest.get("transaction_id")}
