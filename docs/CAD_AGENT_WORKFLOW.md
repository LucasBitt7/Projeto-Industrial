# CAD Agent Workflow

## 0. AUTOMATIC CAD ROUTING (você não precisa mencionar cad_agent)

Todo pedido é classificado automaticamente (`cad-router_classify`, determinístico,
`cad_agent/router.py`) — sem precisar escrever "use cad_agent":

| Você diz | Rota automática |
|---|---|
| "mova essa tomada", "arrume o quadro", "copie o padrão do Dante", "corrija os eletrodutos" | Inspector → Executor → Validator (pipeline completo) |
| "conte as tomadas", "abra o desenho e veja…" | só Inspector (read-only) |
| "explique o que é TUE", script de queda de tensão | resposta normal, sem tocar desenho |

Palavras-chave sozinhas não decidem: semântica (verbos de ação PT/EN + substantivos
CAD + guardas anti-conceito) decide. "Use ezdxf e mova o QDL" continua caindo no
pipeline — mencionar a ferramenta não autoriza bypass. O plugin `cad-guard` recusa
escritas ad-hoc em `*.dxf/*.dwg` (`WRITE_BYPASS_REFUSED`) e injeta `CAD_BACKEND=file`.

## 1. Pedido em linguagem natural

> "Mova a tomada ao lado da porta 30 cm para a direita."

O usuário nunca informa coordenadas nem handles.

## 2. INSPECT (read-only)

```
python3 -m cad_agent inspect <desenho.dxf>
# ou tool: cad-inspect_inspect_drawing
```

Registra `DrawingIdentity`: `absolute_path`, `sha256`, `insunits`, `extents`,
`entity_count`, **`revision_token`**. Backend explícito (`CAD_BACKEND=file`).

## 3. IDENTIFY (handles)

```
python3 -m cad_agent find <desenho> --block 'TUG|TUE' --limit 50
python3 -m cad_agent entity <desenho> <HANDLE>
# ou tools: cad-inspect_find_entities / find_blocks / find_walls / get_entity
```

"Tomada da esquerda" é só hint de busca; o plano cita `outlet_handle=AB12`, `wall_handle=09CD`.

## 4. PLAN (PlanManifest + hash)

JSON com `drawing_identity`, `scope` (bbox/handles/layers), `entities`, `template_refs`,
`operations`, `expected_changes`, `protected_regions`, `validations` + `plan_hash`
(bridge `plan_finalize`). Executor fora do plano => FAIL / `required_plan_revision`.

## 5. EXECUTE (dry-run primeiro)

```
electrical_move_outlet_along_wall(outlet, wall, 300mm)  # dry_run=true -> real
```

Código: resolve handles → vetor da parede → converte mm→unidades → projeta → avança →
checa colisão → move → salva em `out_path` versionado → **readback do mesmo handle**.

## 6. READBACK + VALIDATE (independente)

Validator reabre do zero: identidade, scope guard, readback, integridade de template,
colisões, rede, semântica, callouts. Completion gate (5 ANDs) => veredito.

## 7. Resposta padrão

```
TASK STATUS: PASS
DRAWING: source / source_sha256 / output / output_sha256
SCOPE / OPERATIONS / READBACK / VALIDATIONS / ARTIFACTS / BLOCKERS
```

Nunca apenas "Concluído".
