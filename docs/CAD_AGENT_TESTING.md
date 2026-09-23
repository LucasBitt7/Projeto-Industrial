# CAD Agent Testing

```bash
python3 -m pytest tests/ -q
```

## Pirâmide

- **Unitários** (`test_geometry.py`, `test_units.py`, `test_core.py`): kernel geométrico,
  unidades, identidade/revisão, backends, scope guard, integridade de template. Sem I/O CAD
  real exceto fixtures sintéticas (`tests/conftest.py::make_fixture` — parede, TUG, grupo
  QDF coerente, texto T18, árvore de eletrodutos, `$INSUNITS=4`).
- **Integração A–J** (`test_integration.py`): move outlet 300 mm + readback; revisão errada;
  fora do bbox; clone de painel (fill dentro do outline); árvore (cycles=0, connected);
  órfão; circuito proibido; colisão painel×tomada; callout incompleta; round-trip DXF→DXF.
- **Regressão bugs 1–9** (`test_regression.py`): QDF desmontado, orientação QDL,
  TOM/TUE atrás do quadro, T16 no banheiro, T19 no controle, Tn órfão, segmento órfão,
  identity mismatch, revision stale — cada um com o código esperado.
- **Transação/artefatos** (`test_transaction.py`): commit PASS, violação descarta temp
  sem tocar a fonte, recusa de overwrite in-place, registry versionado.

## Regras

- Produção nunca é tocada: só fixtures sintéticas e cópias `tmp_path`.
- QCAD ausente neste host: round-trip DWG fica como P1 (`validate_qcad_roundtrip`).
- P0 gate: 45/45 PASS antes de declarar a infra pronta.
