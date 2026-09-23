# CAD Agent Tool Reference

Tools TypeScript (thin wrappers sobre `cad_agent/tool_bridge.py <op> '<json>'`).
Envelope de escrita: `{ok, operation_id, drawing_before/after, modified/created/deleted_handles,
handle_map, expected_state, actual_state, validations, warnings, artifact_paths, error_code, error}`.

## Inspector — `.opencode/tools/cad-inspect.ts` (read-only)

| Tool | Bridge op | Uso |
|---|---|---|
| `cad-inspect_inspect_drawing{drawing}` | `inspect` | DrawingIdentity + revision_token (passo 1 sempre) |
| `cad-inspect_find_entities{drawing, layer?, etype?, block_name?, text_regex?, bbox?, limit?}` | `find_entities` | descoberta (hints visuais só aqui) |
| `cad-inspect_get_entity{drawing, handle}` | `get_entity` | ler 1 entidade por handle |
| `cad-inspect_room_entities{drawing, bbox}` | `find_entities` | entidades da sala |
| `cad-inspect_find_blocks{drawing, name_regex?, bbox?, limit?}` | `find_blocks` | blocos por regex |
| `cad-inspect_find_walls{drawing, wall_layers?, bbox?}` | `find_walls` | paredes (handles+p1/p2) |
| `cad-inspect_readback{drawing, handle}` | `get_entity` | re-leitura pós-write |
| `cad-inspect_render_region{drawing, out, bbox?}` | `render` | PNG QA (nunca fonte de coordenada) |

## Executor — `.opencode/tools/cad-execute.ts` (writes controlados)

| Tool | Bridge op | Regras |
|---|---|---|
| `cad-execute_capture_template{drawing, handles, name, semantic_type?, template_id?}` | `capture_template` | registra grupo rígido |
| `cad-execute_clone_template{drawing, template_id, dx, dy, angle_deg?, out_path?, expected_revision?, new_label?}` | `clone_template` | UM transform p/ todos os membros |
| `cad-execute_move_along_wall{drawing, entity_handle, wall_handle, displacement, unit?, direction?, expected_revision?, dry_run?, out_path?, allowed_bbox?}` | `move_along_wall` | LLM nunca calcula X/Y |
| `cad-execute_place_on_wall{drawing, template_id, wall_handle, position_rule?, clearance?, new_label?, expected_revision?, dry_run?, out_path?}` | `place_panel` | free interval + lado maior paralelo |
| `cad-execute_align_to_wall{drawing, wall_handle, mode?}` | `find_walls` | só geometria, sem write |
| `cad-execute_route_conduit{drawing, source_handle, destination_handles, layer?, clearance?, expected_revision?, dry_run?, out_path?}` | `route_conduit` | árvore ortogonal + grafo |
| `cad-execute_connect_circuit{…}` | `route_conduit` | caso single-destino |
| `cad-execute_create_callout{drawing, conduit_edge, circuits, conductor_spec, placement?, …}` | `create_callout` | grupo líder+texto, nunca Tn órfão |
| `cad-execute_move_callout{…}` | `clone_template` | grupo rígido |

Toda escrita exige `expected_revision` (mismatch => `DRAWING_REVISION_MISMATCH`) e
aceita `dry_run=true` (calcula tudo, não salva). `out_path` nunca pode ser o source.

## Validator — `.opencode/tools/cad-validate.ts` (read-only, re-lê do disco)

| Tool | Bridge op | FAIL code |
|---|---|---|
| `cad-validate_detect_collisions{drawing, bbox?, clearance?, limit?}` | `detect_collisions` | `COLLISION_DETECTED` |
| `cad-validate_validate_room{drawing, room}` | `validate_room` | `ROOM_SEMANTIC_VIOLATION` |
| `cad-validate_validate_network{drawing, layer?}` | `validate_network` | `NETWORK_DISCONNECTED`/`NETWORK_CYCLE` |
| `cad-validate_validate_scope{before, after, scope}` | `validate_scope` | `SCOPE_VIOLATION` |
| `cad-validate_validate_callouts{drawing, layer?}` | `validate_callouts` | `ORPHAN_CALLOUT`/`ORPHAN_ENDPOINT` |
| `cad-validate_template_integrity{drawing, handles, semantic_type?, eps?}` | `template_integrity` | `TEMPLATE_INTEGRITY_FAIL` |

## Transação — `.opencode/tools/cad-transaction.ts`

`cad-transaction{action: status, transaction_id?}` — lê `.cad-agent/transactions/<txid>/manifest.json`.

## CLI (`python3 -m cad_agent … --backend file`)

`inspect | entity | find | fingerprint | validate [config] | render --out | network [--layer] | transaction-status`
