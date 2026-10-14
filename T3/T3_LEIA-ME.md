# T3 — CCM1 a CCM6 (Recapadora de Pneus) — LEIA-ME

Resumo da pasta `T3/`: o que cada arquivo é, o resultado, as decisões em aberto e o que foi verificado.

## Arquivos

| Arquivo | O que é |
|---|---|
| `T3-Memorial de Calculo_REV.docx` | **Memorial de cálculo** no estilo do T1/T2 (capa, sumário, lista de figuras). Cap. 1–3: introdução, dados do enunciado e critérios, cada um com o slide da aula que o justifica; cap. 4–9: um capítulo por CCM, com exemplos completos; cap. 10: resumo e decisões a validar. |
| `T3_Planilha_de_Calculo.xlsx` | **Planilha enxuta (8 abas)**: PREMISSAS, MOTORES, PROTECAO_MANOBRA, CONDUTORES, CELULAS, CCMS, PENDENCIAS. Seis CCMs empilhados, valores calculados. |
| `T3-Memorial de Calculo.docx` | Rascunho original do grupo (CCM1 e CCM2 iniciais) — **não alterado**; o memorial novo o substitui para fins de cálculo. |
| `qdgm_ccm_atualizado.xlsx` / `.pdf` | Matriz de potências por processo (entrada do projetista) usada para conferir as potências. |
| `_arquivo_versoes_anteriores.zip` | O **modelo completo com fórmulas** (105 abas) que gera a planilha enxuta e seus valores (.json), mais o memorial e a auditoria da rodada anterior. Backups antigos (v1–v5) descartados. |

## Resultado por CCM

| CCM | QDGM | Cargas | Instalada [kW] | S operacional [kVA] | FP | I_alim [A] | Disjuntor geral | Alimentador [mm²] |
|---|---|---|---|---|---|---|---|---|
| CCM1 | QDGM1 | 2 | 200,0 | 100,0 | 1,00 | 151,9 | ACW160H-FMU160-3 | 70 |
| CCM2 | QDGM1 | 8 | 150,0 | 50,3 | 0,82 | 105,1 | ACW160H-FMU125-3 | 50 |
| CCM3 | QDGM1 | 9 | 19,8 | 7,1 | 0,71 | 17,5 | ACW100H-FMU20-3 | 6 |
| CCM4 | QDGM1 | 17 | 126,9 | 98,7 | 0,81 | 196,5 | ACW250H-ATU200-3 | 95 |
| CCM5 | QDGM2 | 22 | 380,6 | 142,0 | 0,83 | 368,7 | ACW400H-ETS400-3 | 240 |
| CCM6 | QDGM2 | 16 | 435,6 | 385,5 | 0,95 | 716,7 | ACW800U-ETM800-3 | 800 |

Alimentador acima de 240 mm² = cabos em paralelo (CCM6: 800 mm² equivalentes, disjuntor ACW800U-ETM800-3).

## Premissas que o professor pode inverter

- Fator de correção T×H: FC = 0,934 (PIE 08 slide 28; a fonte primária WEG daria 0,938).
- Sem fator de serviço na seleção do motor; Ta do fusível = 0,85 (catálogo WEG p. 29; os slides usam 0,9).
- Prensas (P10–P15): conjugado de partida ≥ 3 × o nominal; limite de queda na partida por célula = mín(10 %; 1 − √(3C/Cp)). Ajustes de projeto: P11 → 30 kW, P13 → 37 kW, P14 → 3,7 kW.
- Afundamento: ≤ 10 % nos terminais do dispositivo de partida (PIE 05 slide 17), uma célula por vez; rearme escalonado é requisito.
- Comprimentos e agrupamento: limites superiores pela geometria do DWG original (planta motriz inexistente).

## Decisões a validar

- Motores de dupla tensão 380/660 V (P9, P17-M3) e de quádrupla tensão (P21): disponibilidade no catálogo WEG.
- P22 (inversor): relação 3:1 lida como redutora → motor de 45 kW; a 'dica' do enunciado cita 30 cv, a planta e o texto, 50 cv.
- P9: torque inicial k = 13/33 (a 'dica' de 1/3 daria menos; o motor de 30 kW não muda).
- P14 = 3,5 cv (matriz do projetista; o rótulo do DWG diz '5,3CV').
- P17 = 28 + 9 + 2,5 cv por célula — **encerrado** (CAD e enunciado concordam; os 23 cv da matriz são do P4/P13).
- Icc real, queda de tensão a montante dos QDGM, curva térmica dos disjuntores de célula e Icw da MSW dependem do T4 / de dados fora da pasta.

## O que foi verificado

- Recálculo independente (`verify.py`) de motores, componentes, cabos, células, totais e alimentadores dos seis CCMs: **0 divergências** contra o modelo completo.
- Modelo completo avaliado sem erro de fórmula; regressão CCM4/CCM5 contra a rodada anterior sem diferença numérica (exceto o P14 corrigido).
- Memorial gerado dos mesmos valores; relido com python-docx (sem marcadores vazios); rascunho original intacto.
- Sensibilidade (cada entrada alterada isoladamente, seis CCMs recalculados; sem erro de fórmula e todas as células atendem a queda de partida): altitude 2000 m e 50 °C sobem 6–7 motores e aumentam o alimentador do CCM4 (120 mm²; CCM5 a 300 mm² a 50 °C); FC da fonte WEG muda 4 motores; **com fator de serviço 25 motores descem de potência** (fora do método); Icc 6 kA só afeta o CCM5; 440 V muda os disjuntores gerais do CCM2 e do CCM6 e reprova o contator de 2 motores de 5 cv. Detalhe no memorial, item 10.4.
- **Limites:** nada foi aberto no Word/Excel (sem Office no ambiente; o memorial foi renderizado no LibreOffice, 91 páginas) — ao abrir no Word, ele pede para atualizar os campos (sumário e lista de figuras): responda *Sim*.

Nenhum arquivo CAD foi alterado (o DWG foi lido apenas em cópia convertida).
