"""Bypass guard: refuses ad-hoc CAD writes outside the cad_agent pipeline.

The OpenCode plugin (.opencode/plugins/cad-guard.ts) delegates to `guard_check`
in tool_bridge so the SAME deterministic rule is enforced in sessions and tested here.
Allowed: bridge ops, `python3 -m cad_agent` read-only/write CLI (audited path),
reads. Refused with WRITE_BYPASS_REFUSED: shell commands that write *.dxf/*.dwg
(saveas/save/redirects) or drive ezdxf into a save outside cad_agent.
"""
from __future__ import annotations

import re

WRITE_VERBS = [
    r"saveas", r"\.save\s*\(", r"\.qsave", r"acad\s+\w+", r"sendcommand",
    r">\s*\S+\.(dxf|dwg)", r"ezdxf.*\bwrite\b",
]

TRUSTED_PATHS = [
    r"cad_agent/tool_bridge\.py",
    r"python3?\s+-m\s+cad_agent",
]


def is_trusted_command(command: str) -> bool:
    return any(re.search(p, command) for p in TRUSTED_PATHS)


def touches_cad_file(command: str) -> bool:
    return bool(re.search(r"\.(dxf|dwg)\b", command, re.IGNORECASE))


def is_adhoc_cad_write(command: str) -> bool:
    """True -> refuse: probable ad-hoc CAD modification bypassing the pipeline."""
    cmd = command or ""
    if is_trusted_command(cmd):
        return False
    if not touches_cad_file(cmd):
        return False
    return any(re.search(p, cmd, re.IGNORECASE) for p in WRITE_VERBS)


def guard_check(command: str) -> dict:
    if is_adhoc_cad_write(command):
        return {"ok": False, "error_code": "WRITE_BYPASS_REFUSED",
                "error": "Ad-hoc CAD write detected. Use the cad_agent pipeline: "
                         "cad-inspect -> plan -> cad-execute (dry_run) -> readback -> cad-validate. "
                         "Temp scripts are allowed only for read-only diagnosis, infra development, "
                         "or a capability cad_agent does not have yet (then extend cad_agent instead).",
                "command": command[:300]}
    return {"ok": True, "command": command[:300]}
