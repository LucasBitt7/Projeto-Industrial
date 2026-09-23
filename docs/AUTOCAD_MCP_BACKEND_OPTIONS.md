# AutoCAD MCP Backend Options

O MCP atual (`autocad-mcp` global, `AUTOCAD_MCP_BACKEND=auto`) foi **preservado, não
substituído**. O que mudou: a camada elétrica não depende dele e nunca faz fallback
silencioso para ele (ou dele para ezdxf).

## Estado

- `cad_agent/backends/base.py::resolve_backend()`: só aceita `file` ou `autocad_live`.
- `FileCadBackend` (ezdxf): headless, CI, auditoria, transformações. Padrão (`CAD_BACKEND=file`).
- `AutoCadLiveBackend`: construtor falha com `BACKEND_UNAVAILABLE` salvo se
  `CAD_LIVE_ENDPOINT` ou `AUTOCAD_MCP_IPC` (caminho existente) estiver configurado.
  Operações ainda delegam ao canal real (P1) — hoje, sem canal, falha fechado.

## Ação recomendada no config global do usuário

Trocar `AUTOCAD_MCP_BACKEND=auto` por `file` (ou remover o env e deixar o default
explícito por chamada), para eliminar o fallback silencioso também fora desta camada.

## Caminho P1: backend .NET/transacional robusto

1. Implementar canal IPC com handshake de identidade do desenho aberto
   (comparar `sha256` + `revision_token` antes de cada escrita).
2. Estender `AutoCadLiveBackend` com `open_identity/list_entities/get_entity/apply`
   sobre esse canal, reaproveitando `assert_revision`, readback e validators
   (nenhuma mudança em `electrical.py` — a API elétrica é agnóstica ao backend).
3. Manter `FileCadBackend` como referência oracular: divergência live-vs-file em
   `drawing_fingerprint()` => `ROUNDTRIP_MISMATCH`/revisão.

A `electrical_*` API funciona independentemente do MCP concreto.
