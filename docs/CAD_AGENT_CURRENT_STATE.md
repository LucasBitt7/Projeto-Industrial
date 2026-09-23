# CAD Agent — Current State Diagnosis (2026-09-09, OpenCode 1.18.30)

Auditoria pré-implementação. Nenhum arquivo de produção foi alterado para este diagnóstico.

## 1. Arquitetura atual

- Repo acadêmico (Projeto Industrial / Recapadora de Pneus), branch `main`, sem nenhuma
  infraestrutura de agente CAD: sem `AGENTS.md`, sem `.opencode/`, sem `opencode.json` local.
- `tools/*.py`: geradores de PDF memorial/luminotécnico (matplotlib) + TSVs de auditoria DWG.
  Úteis como referência de domínio, mas sem relação com edição CAD controlada.
- Desenhos de produção: `T1-desenvolvimento/T1/*.dwg|dxf` (V26/V27/V28 + `_antigas/`),
  `PROJETO RECAPADORA - T1 - FINAL.dwg`. Desenho real: 3717 entidades
  (LINE 2053, LWPOLYLINE 478, INSERT 271, TEXT 262, MTEXT 214…), 19 blocos,
  **`$INSUNITS = 0` (unitless!)** — escala deve vir de configuração, nunca de palpite.
- Global `~/.config/opencode/opencode.jsonc`: MCPs `powerbi-modeling-mcp` e `autocad-mcp`
  com `AUTOCAD_MCP_BACKEND=auto` — **fallback silencioso ativo (risco arquitetural)**.
- Python 3.12.3 + ezdxf 1.4.4 + pytest 9.1.1 + PyYAML + matplotlib 3.11. Node v24.12. **Sem QCAD.**

## 2. Pontos reutilizáveis

- ezdxf 1.4.4 (leitura/escrita DXF headless) — base do `FileCadBackend`.
- Convenções de circuito em textos (`T16/T18/T19…`, CALLS.json/SEG-CIRC.json) — base das room rules.
- Scripts de render PDF em matplotlib — padrão para `render_region` (QA visual).
- OpenCode 1.18.30 suporta: custom tools em `.opencode/tools/*.ts` (`tool()` de
  `@opencode-ai/plugin`), agents em `.opencode/agents/*.md` + `agent:{}` no `opencode.json`,
  permissions por ferramenta/agente com wildcards — tudo que a arquitetura precisa.

## 3. Lacunas (o que faltava — implementado nesta branch)

1. DrawingIdentity/revision token; 2. backend explícito; 3. handles como identidade;
4. geometria determinística; 5. conversão de unidades; 6. scope guard; 7. transação
por arquivo; 8. readback automático; 9. TemplateRegistry/RigidEntityGroup;
10. integridade de painel; 11. colisões; 12. grafo de eletrodutos; 13. semântica de
ambientes; 14. callouts compostas; 15. artifact registry; 16. completion gate;
17. CLI; 18. tools tipadas; 19. agentes Inspector/Executor/Validator;
20. bloqueio de LISP arbitrário; 21. testes + regressão dos 9 bugs reais; 22. docs.

## 4. Riscos

- `INSUNITS=0` no desenho real: qualquer operação geométrica sem fallback configurado
  deve dar `UNKNOWN_UNITS` (implementado — falha visível, nunca palpite).
- `AUTOCAD_MCP_BACKEND=auto` global: a config local desta branch exige backend explícito
  e o backend live falha fechado sem canal; a config global do usuário deve ser ajustada
  (ver `docs/AUTOCAD_MCP_BACKEND_OPTIONS.md`).
- Sem QCAD: round-trip DWG→DXF validado apenas via re-leitura ezdxf; QCAD é P1.
- Nomes exatos das tools do MCP autocad são desconhecidos neste Linux (MCP é win32);
  o bloqueio usa wildcard `*execute_lisp*`/`*lisp*` — revisar se o MCP expuser outro nome.

## 5. Plano de migração (executado)

Incremental, sem quebrar nada: branch `feat/electrical-cad-agent-reliability`;
nada apagado/substituído; produção nunca editada (só cópias em `/tmp` e fixtures
sintéticas); sem push automático; sem installs destrutivos.
