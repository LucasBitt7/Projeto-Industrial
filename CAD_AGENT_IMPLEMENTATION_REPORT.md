# CAD Agent Implementation Report — P0 Reliability Layer

Branch: `feat/electrical-cad-agent-reliability` (from `main`). No commit/push performed.
Produção nunca alterada: todos os testes/demos usam fixtures sintéticas (`tests/conftest.py`)
ou cópias em `/tmp`; nenhum `.dwg/.dxf` original foi escrito.

## Estado anterior → arquitetura implementada

Diagnóstico: `docs/CAD_AGENT_CURRENT_STATE.md`. Antes: LLM com comandos CAD genéricos via
MCP `autocad-mcp` em modo `auto` (fallback silencioso), sem identidade de desenho, sem
handles, sem transação, sem validação. Depois: pipeline
Inspector → PlanManifest+hash → Executor → Electrical Tools → backend explícito →
readback → Validator → PASS/FAIL (detalhes: `docs/CAD_AGENT_ARCHITECTURE.md`).

## Arquivos criados

- `cad_agent/`: `__init__.py`, `__main__.py` (CLI), `tool_bridge.py`, `errors.py`,
  `models.py`, `units.py`, `geometry.py`, `drawing.py`, `entities.py`, `walls.py`,
  `templates.py`, `collisions.py`, `conduit.py`, `rooms.py`, `callouts.py`,
  `validators.py`, `transaction.py`, `artifacts.py`, `audit.py`, `render.py`,
  `electrical.py`, `backends/{base,ezdxf_backend,autocad_backend}.py`
- `.opencode/tools/`: `cad-inspect.ts` (8 tools), `cad-execute.ts` (9 tools),
  `cad-validate.ts` (6 tools), `cad-transaction.ts` (1 tool)
- `.opencode/agents/`: `cad-inspector.md`, `cad-executor.md`, `cad-validator.md`
- `.opencode/package.json`, `opencode.json` (nega `*execute_lisp*`/`*lisp*` global +
  por agente; registra os 3 subagentes), `AGENTS.md` (rígido), `.gitignore`
- `config/electrical-cad.yaml` (unidades, tolerâncias, layers, aliases, routing,
  room_rules BANHEIRO/CONTROLE, panel/callout rules)
- `docs/`: `CAD_AGENT_CURRENT_STATE.md`, `CAD_AGENT_ARCHITECTURE.md`,
  `CAD_AGENT_WORKFLOW.md`, `CAD_AGENT_TOOL_REFERENCE.md`, `CAD_AGENT_SAFETY.md`,
  `AUTOCAD_MCP_BACKEND_OPTIONS.md`, `CAD_AGENT_TESTING.md`
- `tests/`: `conftest.py`, `test_geometry.py`, `test_units.py`, `test_core.py`,
  `test_integration.py` (A–J), `test_regression.py` (bugs 1–9), `test_transaction.py`

Arquivos modificados: nenhum de produção. (O `git status` mostra deleções/untracked
pré-existentes do workspace — intocados por esta tarefa.)

## Tools / Agents / Validators / Testes

- 24 custom tools tipadas (8 inspect read-only, 9 execute com dry-run+revisão,
  6 validate read-only, 1 transaction status) — ver `docs/CAD_AGENT_TOOL_REFERENCE.md`.
- 3 subagentes com permissões: inspector (edit deny), executor (edit ask, sem LISP),
  validator (edit deny, veredito `TASK STATUS: PASS|FAIL`).
- Validators: scope guard, delete guard, template integrity, colisões, grafo
  (connected/acyclic/orphans), semântica de ambientes, callouts, completion gate (5 ANDs).
- **Testes: 45/45 PASS** (`python3 -m pytest tests/ -q`): geometria, unidades,
  identidade/revisão, backend explícito, scope, templates, integração A–J, regressão
  bugs 1–9, transação/artefatos.

## Backend

`CAD_BACKEND=file` (ezdxf, default) | `autocad_live` (fails closed sem
`CAD_LIVE_ENDPOINT`/`AUTOCAD_MCP_IPC`). `auto` rejeitado. MCP atual preservado;
ajuste pendente no config global do usuário (`AUTOCAD_MCP_BACKEND=auto` → `file`).

## Smoke test (fixture, `/tmp/smoke`)

`inspect` (rev `9f143da3bd13`, INSUNITS=4) → identify (outlet `35`, wall `2F`) →
`dry_run` (to `[1300,0]`) → execute (op `452ecccbb2f5`, artefato versionado) →
readback (`[1300,0]` exato) → scope+network OK → **GATE=PASS**.
`validate base.dxf config/electrical-cad.yaml` → exit 0. Render PNG OK (QA apenas).
Recusas verificadas: OUT_OF_SCOPE, DRAWING_REVISION_MISMATCH, TEMPLATE_INTEGRITY_FAIL,
ROOM_SEMANTIC_VIOLATION, NETWORK_DISCONNECTED.

## Como usar / diagnosticar

```bash
CAD_BACKEND=file python3 -m cad_agent inspect <dxf>
CAD_BACKEND=file python3 -m cad_agent validate <dxf> config/electrical-cad.yaml
python3 -m pytest tests/ -q
```

## Limitações conhecidas (P1)

QCAD ausente (sem `validate_qcad_roundtrip` DWG); live backend sem canal real ainda;
nomes exatos das tools do MCP win32 a confirmar no Windows; desenho real com
`INSUNITS=0` exigirá fallback configurado em `config/electrical-cad.yaml` ou FAIL;
orientação de painel (BUG 2) coberta por regra+teste geométrico, validador dedicado
de orientação é P1.

## Addendum — Automatic CAD Routing (integração final)

- `cad_agent/router.py`: classificador semântico (substantivos CAD + verbos PT/EN flexionados + guardas conceitual/não-CAD). 9 testes cobrindo os 6 exemplos exigidos + casos sem keyword ("mova essa tomada", "copie o padrão do Dante") + bypass ("use ezdxf e mova o QDL" → pipeline).
- `cad_agent/config.py`: fallback de unidade explícito via `config/electrical-cad.yaml` (atual: não configurado → `UNKNOWN_UNITS` FAIL; `resolved_by` registrado quando configurado). `walls.move_along_wall` usa `resolve_unit_context`.
- `cad_agent/guard.py` + plugin `.opencode/plugins/cad-guard.ts`: `shell.env` injeta `CAD_BACKEND=file`; `tool.execute.before` recusa escrita ad-hoc em `*.dxf/*.dwg` (`WRITE_BYPASS_REFUSED`) com a mesma regra testada em `tests/test_policy.py`.
- `cad_agent/session.py`: `require_expected_revision` (bridge recusa write sem revisão → `WRITE_WITHOUT_INSPECTION`) + `resolve_current_artifact` (lineage do registry, nunca adivinhar `*final*.dxf`).
- `.opencode/tools/cad-router.ts`: `classify`, `guard_check`, `current_artifact`. Subagente `cad-router` + entradas em `opencode.json` (bash granular allow p/ bridge/CLI/testes).
- `AGENTS.md`: seção AUTOMATIC CAD ROUTING + formato final de resposta; prompts inspector/executor reforçados (manifest mínimo / manifest obrigatório).
- Global `~/.config/opencode/opencode.jsonc`: `AUTOCAD_MCP_BACKEND` `auto`→`file` (backup `.bak-cadagent`). MCPs preservados.
- Demos A/B/C executadas em fixtures (`/tmp`): A full_pipeline PASS com readback exato; B inspect_only sem writes; C conceptual sem transação. Produção intocada.
