# LUCAS UNIFILAR DATA AUDIT — QDL5/QDL6/QDL7 (READY) · QDF5/QDF6/QDF7 (BLOCKED)

Drawing: `T1-desenvolvimento/T1/RECAPADORA DE PNEUS - 2026-2-DANTE 08-09-2026 - V29 LUCAS.dxf`
`sha256=c59cb1a4710333bd46f5923898c5722ad05a1deb822e9bdf8a4bc8bd143657fb` · `revision_token=6860e71e…` · entities=3717
Backend: `CAD_BACKEND=file` · `MCP_USED=false (not required)`.
Template-fonte único: **QDL1** (completo, sem "?"). QDL4 descartado como template (possui "MDW-C?-?/? A" e "1#?,0", sem reservas RQDL4-x).

Convenções Dante capturadas do CAD (não inventadas):
título `QDL1 Sala de Caldeiras` · linha `L1-ILUMINAÇÃO` · elétrica `220 V / 1760 VA / 8 A / FASE "S"` ·
reservas `RQDL1-1-RESERVA` / `RQDL1-2-RESERVA` · feeder `Vem do QDGL` · disjuntor
`\pxsm1;{\Fisocp|c0;MDW-C16\P\Fisocp2|c0;16 A - 5 kA}` · condutor fileira `\A1;\pxqc;1#1,5` ·
barramento `380 / 220 V - 123 A - 6 kA - 1 Barra Retangular de Cobre Pintada por fase de 12 mm x 2 mm - seção 23,5 mm²`
(idêntico nos 8 diagramas Dante + memorial P1559/1606/1643/1679/1774/1802/1830/1861 = padrão do projeto).

## READY PANELS

### QDL5 — Escritório — READY
| campo | valor | fonte | status |
| circuito/área | L18 / ESCRITÓRIO | `QDL-ILUMINAÇÃO.xlsx` aba QDL R21 | CONFIRMED |
| tensão/pontos/pot. | 220 V · 15 × 120 VA = 1800 VA | QDL R21 (G=15, H=120) | CONFIRMED |
| corrente | 8,18 A (=1800/220, cross-check memorial) | calc. verificada | CONFIRMED |
| fase/FP | R / 0,90 | memorial Cap.13 / QDL K21=0.9 | CONFIRMED |
| disjuntor circuito | MDW-C10, C, 10 A, 5 kA, 1P | memorial Cap.11 + `DISJUNTORES` R21 In=10 | CONFIRMED |
| fases/neutro/PE | 1,5/1,5/1,5 mm² PVC m7/B1 | `SEÇÃO CONDUTORES` R21 | CONFIRMED |
| alimentador/geral | `Vem do QDGL`, 6 mm², MDWH-C10, 127 m | memorial Cap.14 | CONFIRMED |
| barramento | cobre pintada 380/220 V 123 A (texto padrão) | memorial (8 citações) + CAD B126 | CONFIRMED-BY-STANDARD |
| reservas | RQDL5-1-RESERVA, RQDL5-2-RESERVA | convenção RQDLx-1/-2 do CAD | CONFIRMED |
| título | `QDL5 Escritório` | convenção Dante + planilha | CONFIRMED |
| textos a desenhar | `L18-ILUMINAÇÃO` · `220 V / 1800 VA / 8,18 A / FASE "R"` | formatos Dante, valores audit | READY |

### QDL6 — Saída de Produto + Controle de Qualidade — READY (2 CircuitRows)
| campo | valor | fonte | status |
| L19 | SAIDA DE PRODUTOS, 220 V, 3×120=360 VA, 1,64 A, T, FP 0,90, C10, 1,5 mm² | QDL R22, SEÇÃO R22, DISJ R22, memorial Cap.13 | CONFIRMED |
| L20 | CONTROLE DE QUALIDADE, 220 V, 18×120=2160 VA, 9,82 A, S, FP 0,90, C10, 2,5 mm² | QDL R23, SEÇÃO R23, DISJ R23, memorial Cap.13 | CONFIRMED |
| alimentador/geral | `Vem do QDGL`, 2,5 mm², MDWH-C10/2, 127 m | memorial Cap.14 | CONFIRMED |
| barramento/reservas | padrão 123 A / RQDL6-1, RQDL6-2 | idem QDL5 | CONFIRMED |
| título | `QDL6 Saída de Produto e Controle de Qualidade` | convenção Dante (`QDL4 Raspa e Recapagem`) | CONFIRMED |
| textos | `L19-ILUMINAÇÃO` · `220 V / 360 VA / 1,64 A / FASE "T"` / `L20-ILUMINAÇÃO` · `220 V / 2160 VA / 9,82 A / FASE "S"` | formatos Dante | READY |

### QDL7 — Banheiro/Vestiário — READY
| campo | valor | fonte | status |
| L21 | 220 V, 2×120=240 VA, 1,09 A, T, FP 0,90, C10, 1,5 mm² | QDL R24, SEÇÃO R24, DISJ R24, memorial Cap.13 | CONFIRMED |
| alimentador/geral | `Vem do QDGL`, 1,5 mm², MDWH-C10, 127 m | memorial Cap.14 | CONFIRMED |
| barramento/reservas/título | padrão / RQDL7-1, RQDL7-2 / `QDL7 Banheiro (Vestiário)` | idem | CONFIRMED |
| textos | `L21-ILUMINAÇÃO` · `220 V / 240 VA / 1,09 A / FASE "T"` | formatos Dante | READY |

Detalhes de formato vindos do template (valores do audit): disjuntores fileira
`\pxsm1;{\Fisocp|c0;MDW-C10\P\Fisocp2|c0;10 A - 5 kA}`; gerais
`MDWH-C10` / `MDWH-C10/2` + `10 A - 5 kA` (5 kA = nível do projeto, Dados Iniciais p.3);
condutores fileira `\A1;\pxqc;1#SEÇÃO` (1,5 ou 2,5); tag geral `1#1,5` (QDL5/7, fiel ao QDL1) /
`1#2,5` (QDL6, seção do alimentador auditado); tag `RST` e molduras clonadas fiéis ao template.
Decimais com vírgula (`8,18 A`) conforme padrão BR dos diagramas (`12,0 A`).

## BLOCKED PANELS (fora desta execução — sem entidades criadas)

### QDF5 — BLOCKED_BY_DATA / ELECTRICAL_INCONSISTENCY
Geral `MDW-C10/2` 10 A (`Tomadas…xlsx` QDFG R34) < fase R 12,27 A (T11 5,45 + T13 6,82).
Fases: `QDF-BALANÇO TOTAL` R24. TUE 1500 VA por decisão do usuário (2026-09-10).

### QDF6 — BLOCKED_BY_DATA / ELECTRICAL_INCONSISTENCY
Geral `MDW-C20/2` 20 A (QDFG R35) < fase S 20,91 A (T15 7,27+T16 6,82+T17 6,82);
alimentador 6 mm² no limite pelo critério documentado `Ip'=B×1,05/(0,87×0,72)` (QDFG R60).

### QDF7 — BLOCKED_BY_DATA / ELECTRICAL_INCONSISTENCY (crítica)
Geral `MDW-C32/2` 32 A (QDFG R36) < T19 40,91 A; final T19 In 50 > geral 32 (coordenação
invertida); alimentador 10 mm² reprovado pelo mesmo critério (QDFG R61). Config 1 TUG + 1
chuveiro confirmada pela planta V29 e por decisão do usuário (narrativa 4+3 descartada).

Sem fator de demanda em nenhuma aba (colunas DEMANDA vazias; varredura negativa) —
totais são somas aritméticas. Nenhum "?" desenhado: campo sem fonte = quadro travado.

## ADENDO QDF — READY_AS_DOCUMENTED (autorização usuário 2026-09-10)

Template-base único: **QDF-1** (único QDF Dante 100% resolvido; QDF-4 tem `MDWH-C?-3/?A`
e fileiras `MDW-C?`). Títulos com hífen (`QDF-5 …`), fileiras `Tn - TOMADAS`
(com espaços, convenção QDF Dante), `T19 - CHUVEIRO` (ordem expressa).

Sintaxe de condutores decodificada do Dante (`#N` = nº de fases: `1#` mono, `3#` 3F):
fileiras T11–T18 tag verbatim `1#2,5`; **T19 `1#16`** (sintaxe do template + 16 mm² de
`SEÇÃO CONDUTORES` R22); gerais `2#6` (QDF5/6, fases R+S) e `2#10` (QDF7, R+T),
seções de `Tomadas…xlsx` QDFG R59–R61. Pente geométrico sempre verbatim.
Símbolo do geral: graft do grupo 2-traços do QDL1 (mesmo módulo), pois o do QDF-1 é
3P e os gerais Lucas são /2; textos do geral seguem QDFG R34–R36 (`MDW-C10/2`,
`MDW-C20/2`, `MDW-C32/2` + `10/20/32 A - 5 kA`).
DDR T19: **anotação textual separada `DDR 30 mA`** (`ELET_UNIFILAR_TEXTO2`/`textstyle7`/
0,2836, sob o texto elétrico da fileira) — busca exaustiva provou que não existe
convenção DR/DDR clonável (único `DR` do CAD acompanha label `?`; planilhas e memorial
só exigem por texto). Disjuntor T19 limpo: `MDW-C50` / `50 A - 5 kA` (modelo da família
WEG + In 50 de `DISJUNTORES` R22; curva C e 5 kA padrão do projeto).

ENGINEERING_STATUS por quadro (representado como documentado, sem correção):
QDF5 ELECTRICAL_WARNING (geral 10 A < fase R 12,27 A) · QDF6 ELECTRICAL_WARNING
(geral 20 A < fase S 20,91 A; alimentador no limite) · QDF7 ELECTRICAL_WARNING
(geral 32 A < 40,91 A; final 50 A > geral; alimentador a revisar).
