"""Artifact registry: one directory per transaction, no more V23/V24 confusion."""
from __future__ import annotations

import json
import os
import shutil
import time

REGISTRY_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cad-agent", "transactions")


def create_artifact_dir(transaction_id: str) -> str:
    p = os.path.join(REGISTRY_ROOT, transaction_id)
    os.makedirs(os.path.join(p, "previews"), exist_ok=True)
    return p


def write_manifest(transaction_id: str, manifest: dict) -> str:
    d = create_artifact_dir(transaction_id)
    mp = os.path.join(d, "manifest.json")
    manifest = dict(manifest)
    manifest["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return mp


def store_file(transaction_id: str, name: str, src: str) -> str:
    d = create_artifact_dir(transaction_id)
    dst = os.path.join(d, name)
    shutil.copy2(src, dst)
    return dst


def versioned_output(project: str, kind: str, transaction_id: str, revision: int, ext: str = "dxf") -> str:
    safe = "".join(c if (c.isalnum() or c in "-_") else "_" for c in project)
    return os.path.abspath(f"{safe}_{kind}_v{revision:02d}_{transaction_id}.{ext}")
