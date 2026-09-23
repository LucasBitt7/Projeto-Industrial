# CAD Agent Safety

1. **Backend explícito**: `CAD_BACKEND=file|autocad_live`. `auto`/vazio => rejeitado.
   Live sem canal (`CAD_LIVE_ENDPOINT`/`AUTOCAD_MCP_IPC`) => `BACKEND_UNAVAILABLE` (fail closed).
2. **Revision token**: escrita exige `expected_revision`; mudou desde o inspect =>
   `DRAWING_REVISION_MISMATCH`. Nunca editar arquivo diferente do inspecionado.
3. **Handles**: identidade pós-descoberta. Escritas rejeitam referência vaga.
4. **Sem fallback**: layer/bloco/template/unidade/parede/handle ausente => FAIL com código.
   Layer 0 nunca é fallback. Bloco padrão nunca explodido nem redesenhado à mão.
5. **LISP**: `*execute_lisp*`/`*lisp*` negados no `opencode.json` e nos 3 agentes CAD.
   Automação só via wrappers versionados/testados desta camada.
6. **Escopo**: `validate_no_changes_outside_scope()` compara antes/depois canônico;
   criado/apagado/modificado fora => `SCOPE_VIOLATION`, transação descartada.
7. **Deletes**: só com handles resolvidos + `expected_count` (delete guard); divergência => FAIL.
8. **Transação**: fonte copiada p/ temp; publish atômico só após readback+validação;
   overwrite in-place recusado; falha descarta temp, fonte intacta.
9. **Readback**: automático em toda escrita (reabre do disco, compara com tolerância).
10. **Completion gate**: PASS = execution ∧ readback ∧ scope ∧ validators ∧ artifact_identity.
11. **Protegidos**: `config/electrical-cad.yaml: layers.protected` (arquitetura, cotas,
    nomes de ambientes) intocáveis sem autorização explícita.
12. **Render é QA**: PNG nunca fornece coordenada, alinhamento, conexão ou distância.
13. **Produção**: desenvolver/testar só em cópias e fixtures; nunca sobrescrever originais;
    artefatos versionados `<projeto>_<tipo>_vNN_<txid>.dxf` em `.cad-agent/transactions/`.
