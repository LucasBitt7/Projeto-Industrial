"""Structured JSONL audit log."""
from __future__ import annotations

import json
import os
import time

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".logs", "cad-agent")


def log_event(event: dict) -> str:
    os.makedirs(LOG_DIR, exist_ok=True)
    event = dict(event)
    event.setdefault("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    day = time.strftime("%Y-%m-%d", time.gmtime())
    p = os.path.join(LOG_DIR, f"{day}.jsonl")
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return p
