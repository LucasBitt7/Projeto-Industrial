# Electrical CAD Agent

Objective: operate electrical drawings with maximum precision and minimum unintended change.

## AUTOMATIC CAD ROUTING (applies without the user naming any tool)

This workspace auto-loads this file (OpenCode project `AGENTS.md`). For EVERY user
request, before any other tool call, classify intent with `cad-router_classify`:

- `route=full_pipeline` (any CAD modification: move/fix/place/align/route/alterar
  tomada, quadro, eletroduto, circuito, planta, bloco CAD — even without the words
  "AutoCAD/DXF", e.g. "mova essa tomada", "arrume o quadro", "copie o padrão do Dante"):
  delegate `cad-inspector` -> PlanManifest -> `cad-executor` (dry_run first) ->
  readback -> `cad-validator` -> completion gate. The user never names tools.
- `route=inspect_only` (counts, listings, "abra o desenho e veja..."): `cad-inspector` only.
- `route=conceptual` or `none` ("explique o que é TUG", voltage-drop scripts, memorials):
  normal answer, NO CAD transaction, NO drawing touched.

For CAD tasks NEVER use shell ad-hoc scripts, ad-hoc ezdxf, or generic MCP directly.
Mandatory tool priority: `cad-inspect_*` / `cad-execute_*` / `cad-validate_*` /
`cad-transaction` / `cad-router_*` and the `cad_agent.electrical` high-level APIs.
Primitive LINE/MOVE math by the LLM is forbidden when a specialized tool exists
(wrong: mental coordinates + move; right: handle + `cad-execute_move_along_wall`).
The `cad-guard` plugin injects `CAD_BACKEND=file` and refuses ad-hoc `*.dxf/*.dwg`
writes (`WRITE_BYPASS_REFUSED`); temp scripts are allowed only for read-only
diagnosis, infra development, or a capability cad_agent lacks (then extend cad_agent).

## Mandatory flow (never skip steps)

1. **INSPECT** — `cad-inspect_inspect_drawing` / `python3 -m cad_agent inspect <dxf>`. Record DrawingIdentity + revision_token.
2. **IDENTIFY** — resolve every target to a HANDLE via find tools. Visual hints are discovery-only.
3. **PLAN** — emit a PlanManifest JSON + plan_hash. Writes outside the plan are forbidden.
4. **EXECUTE** — high-level tools only, `dry_run=true` first, explicit `CAD_BACKEND`, expected_revision checked.
5. **READBACK** — re-read every touched handle from disk (automatic in tools; verify it).
6. **VALIDATE** — independent validator + completion gate. Only then PASS.

No CAD modification may occur before INSPECT: write tools require the
`expected_revision` from inspection (`WRITE_WITHOUT_INSPECTION` refused).
The executor only accepts a PlanManifest + plan_hash + expected_revision + scope;
without a manifest it must request the inspector stage (FAIL otherwise).
No CAD task ends before the validator re-opens the saved artifact.

## Never (hard rules)

- Never modify an entity based only on appearance, proximity, screenshot, or assumption. Always a handle.
- Never invent coordinates or do precise geometry mentally — deterministic code computes.
- Never use layer 0 as fallback. Missing layer/block/template/unit/wall/handle => FAIL with code, no lookalike substitution.
- Never explode a standard electrical block to ease an operation; never replace a standard template with manual sketching.
- Never delete an object whose identity is unconfirmed; no broad layer deletes without resolved handles + expected count + dry-run.
- Never continue after a partial error without readback. Never declare done because a script ran / returned OK / saved — completion requires real final-state validation.
- Never edit a file different from the inspected one (revision_token enforced). Never overwrite production sources in place; write versioned artifacts (`<project>_<kind>_vNN_<txid>.dxf`).
- Never fall back silently between backends: `CAD_BACKEND=file|autocad_live`, `auto` rejected. Live backend without a working channel FAILS CLOSED.
- No arbitrary AutoLISP for normal CAD agents (`*execute_lisp*` denied). LISP only via versioned, tested wrappers.

## Sources of truth

- CAD data is the geometric source. Screenshots/renders are visual QA only — never a coordinate source.
- Handles are identity after discovery. Units come from $INSUNITS (unitless + no config => UNKNOWN_UNITS FAIL).
- A task answer is `TASK STATUS: PASS|FAIL` with DRAWING / SCOPE / OPERATIONS / READBACK / VALIDATIONS / ARTIFACTS / BLOCKERS — never just "done".

## Final answer format (CAD tasks, concise but never omit PASS/FAIL)

TASK STATUS: PASS | FAIL
DRAWING: source / output / revision
OPERATIONS: summary
VALIDATION: readback / scope / geometry / electrical / visual(if any)
BLOCKERS: none | list
ARTIFACTS: final files

## How to ask for CAD changes

> "Move a tomada ao lado da porta 30 cm para a direita."

Inspector resolves handles (outlet + wall) -> planner emits PlanManifest ->
executor calls `electrical_move_outlet_along_wall` (code computes geometry) ->
readback re-reads the handle -> validator confirms. User never supplies coordinates.

See `docs/CAD_AGENT_WORKFLOW.md`, `docs/CAD_AGENT_TOOL_REFERENCE.md`, `docs/CAD_AGENT_SAFETY.md`.
