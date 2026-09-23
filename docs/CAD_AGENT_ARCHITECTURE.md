# CAD Agent Architecture

```
USUARIO -> OPENCODE -> CAD INSPECTOR (read-only) -> PLANO ESTRUTURADO (PlanManifest+hash)
-> CAD EXECUTOR (writes limitados) -> ELECTRICAL CAD TOOLS (geometria determinística)
-> BACKEND EXPLICITO (file | autocad_live) -> READBACK -> CAD VALIDATOR (read-only)
-> PASS / FAIL (completion gate)
```

O LLM decide **o quê** (intenção, função dos objetos, plano). Código determinístico decide
**como**: coordenadas, projeções, offsets, snapping, interseções, bboxes, rotação,
caminhos, hashes, tolerâncias, validações. O modelo nunca faz geometria precisa mentalmente.

## Automatic routing (nativo OpenCode 1.18.30)

Sem suporte da plataforma a roteamento automático entre agentes, a integração usa os
três mecanismos nativos combinados (nenhuma configuração inventada):

1. **`AGENTS.md` (auto-load)** — manda o agente principal chamar `cad-router_classify`
   antes de qualquer tool call e delegar via `task` aos subagentes
   `cad-router`/`cad-inspector`/`cad-executor`/`cad-validator`.
2. **Plugin `.opencode/plugins/cad-guard.ts`** — `shell.env` injeta `CAD_BACKEND=file`;
   `tool.execute.before` recusa escritas ad-hoc em `*.dxf/*.dwg` com o mesmo veredito
   determinístico de `cad_agent/guard.py` (`WRITE_BYPASS_REFUSED`).
3. **Permissions (`opencode.json`)** — `*execute_lisp*` negado; bash com allows
   granulares para `tool_bridge.py`/CLI/testes; resto `ask`.

## Componentes (`cad_agent/`)

| Módulo | Papel |
|---|---|
| `errors.py` | `CadError(code, message, details)` + 25 códigos (`DRAWING_REVISION_MISMATCH`, `SCOPE_VIOLATION`, `TEMPLATE_INTEGRITY_FAIL`, `ROOM_SEMANTIC_VIOLATION`, `ORPHAN_*`, `NETWORK_*`, `PANEL_ORIENTATION_FAIL`, `DRAWING_IDENTITY_MISMATCH`, `BACKEND_*`…) |
| `models.py` | `DrawingIdentity`, `CadEntityRef`, `BBox`, `Scope`, `PlanManifest` (+hash), `OperationResult` (envelope padrão), `CadTemplate`, `TransactionManifest`, `RoomRules` |
| `units.py` | `UnitContext` via `$INSUNITS`; unitless sem fallback => `UNKNOWN_UNITS` FAIL |
| `geometry.py` | Kernel puro: projeções, along-wall, bbox, snapping, interseções, alinhamento, rigid transforms, `find_free_wall_interval`, `orthogonal_route`, `route_with_clearance`, grafo (`polyline_to_graph`, `connected_components`, `detect_cycles`, `unique_path`, `orphan_endpoints`) |
| `backends/` | `resolve_backend()` explícito (`auto` rejeitado); `FileCadBackend` (ezdxf); `AutoCadLiveBackend` (fails closed sem `CAD_LIVE_ENDPOINT`/`AUTOCAD_MCP_IPC`) |
| `drawing.py` | `drawing_identity()`, `drawing_fingerprint()`, `entity_fingerprint()`, `scope_fingerprint()`, `assert_revision()` |
| `entities.py` | Descoberta por layer/tipo/bloco/regex/bbox; `get_entity(handle)`; descrição visual só na descoberta |
| `walls.py` | Detecção de paredes, `move_along_wall()` (projeta→avança→dry-run→move→readback) |
| `templates.py` | `capture_template()`, `clone_template()` (UM rigid transform), `validate_template_integrity()` (fill/diagonal dentro do outline, labels adjacentes, compacidade) |
| `collisions.py` | bbox+clearance all-vs-all com kinds (panel/outlet/callout/text/…) |
| `conduit.py` | `route_conduit()` + `validate_network_graph()` (connected, acyclic, orphans) |
| `rooms.py` | `validate_room()`/`validate_project_scope()` por regex de circuito |
| `callouts.py` | `create_callout()` (grupo líder+texto, nunca Tn órfão) + `validate_callouts()` |
| `validators.py` | `validate_no_changes_outside_scope()`, `validate_delete_guard()`, `completion_gate()` (5 portas AND) |
| `transaction.py` | `FileTransaction`: cópia→temp→aplica→readback→scope→publicação atômica; recusa overwrite in-place |
| `artifacts.py` | Registry `.cad-agent/transactions/<txid>/` + `versioned_output()` (`<proj>_<kind>_vNN_<txid>.dxf`) |
| `audit.py` | JSONL em `.logs/cad-agent/` |
| `render.py` | PNG via matplotlib — QA visual apenas |
| `electrical.py` | API de alto nível: `electrical_find_outlets/panels`, `electrical_move_outlet_along_wall`, `electrical_place_panel_on_wall`, `electrical_route_conduit`, `electrical_create_callout` |
| `tool_bridge.py` | Ponte única das tools TS → Python (envelope `{ok,…}`) |
| `__main__.py` | CLI |

## Decisões-chave

- Handles são identidade após descoberta; escrita rejeita referência vaga.
- Toda escrita: `expected_revision` + `dry_run` + `out_path` distinto + readback do disco.
- Templates movem como UM grupo rígido (nunca fill separado do outline).
- Falha visível > sucesso inventado: sem layer 0 fallback, sem blocos parecidos, sem palpite de unidade.
