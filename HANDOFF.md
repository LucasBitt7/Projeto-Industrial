# HANDOFF — T3 CCM1–CCM6 (Lucas) — estado em 2026-10-05

Curso "Projetos de Instalações Elétricas Industriais" (EEL 2026-2), Recapadora de Pneus. Este arquivo resume o que um novo agente precisa para continuar; as versões anteriores (rodadas 1–6, ~200 linhas) foram condensadas aqui.

## 1. Entregáveis (pasta `T3/`)
| Arquivo | Papel |
|---|---|
| `T3-Memorial de Calculo_REV.docx` | Memorial no estilo T1/T2 (capa/sumário/lista de figuras por campos; "Figura N - … / Fonte: …"; 28 slides das aulas como justificativa). Cap. 1 Introdução · 2 Dados · 3 Critérios · 4–9 CCM1…CCM6 · 10 Resumo/decisões · 11 Referências. |
| `T3_Planilha_de_Calculo.xlsx` | Planilha enxuta, 8 abas, **só valores**: LEIA-ME, PREMISSAS, MOTORES, PROTECAO_MANOBRA, CONDUTORES, CELULAS, CCMS, PENDENCIAS. |
| `T3_LEIA-ME.md` | Resumo curto: arquivos, resultado por CCM, decisões, verificações, sensibilidade. |
| `T3-Memorial de Calculo.docx` | Rascunho original do grupo — **intocado** (versionado no git). |
| `qdgm_ccm_atualizado.xlsx/.pdf` | Matriz de potências do usuário (entrada). |
| `_arquivo_versoes_anteriores.zip` | **Modelo completo com fórmulas (105 abas) + valores (.json)**, memorial e auditoria da rodada anterior. |

## 2. Como regenerar (geradores só no scratchpad da sessão: `…/scratchpad/work/`; copiar para o repo se quiser preservar)
`cfg.py` (entradas: potências, métodos `MET`, geometria) → `build.py <xlsx>` (modelo completo; módulos `calc_sheets/data_sheets/audit_sheets/infer_sheets/text_sheets`) → `evalx.py <xlsx>` (biblioteca `formulas`, ~2 min, gera `.json`) → `verify.py <json>` (recálculo independente; esperado "0 divergências" nos 6 CCMs) → `figs.py` → `slim_xlsx.py <modelo> <saida>` → `memorial.py [saida.docx]` (classe Doc2 em `mem_lib.py`; cap. 1–3 em `mem_front.py`, cap. 10–11 em `mem_back.py`; cap. 4–9 reaproveitam `build_docx*.py` por `exec` com renumeração `CHMAP/SUBMAP` e troca de nomes de abas em `TX`) → `gen_leiame.py`. Slides das aulas: `slides.py` (PyMuPDF → JPEG). Sensibilidade: `scen6.py`.
QA visual: LibreOffice portátil extraído em `scratchpad/lo/` (precisa de `LD_LIBRARY_PATH` com `lo/syslibs`); `memorial.py` usa-o para preencher os números de página do sumário em cache (o Word recalcula ao abrir — responder *Sim* ao pedido de atualizar campos).

## 3. Método (decisões e porquê)
- Motor: P[cv]·0,736; C = 716·cv/n; P_nm,min = P/FC com **FC = 0,934** (PIE 08 slide 28; a fonte primária WEG daria 0,938); menor W22 IR3 Premium (catálogo pp. 34–37); **sem fator de serviço**. Prensas (P10–P15): Cp ≥ 3·C e limite de queda na partida por célula = mín(10 %; 1−√(3C/Cp)); ajustes de projeto P11 → 30 kW, P13 → 37 kW, P14 → 3,7 kW.
- Partida: D direta; YD (P9, P17-M3; dupla tensão 380/660 V assumida); SP série-paralela (P21; quádrupla tensão); CP compensadora (P23, taps 65/80 %); INV inversor CFW700 (P22; relação 3:1 lida como redutora → motor 45 kW); INT intermitente (P24, P_eq com repouso 1/3); R resistivas (contator AC-1). Tensão reduzida: fusível sem limite k·Ip,m (PIE 09 slide 52), K1–K4 aumentados até Fmáx ≥ In,f mín; t_rb corrigido por (Un/Ur)².
- Proteção: contator 1,10·In; relé 1,05–1,15·In com t_rb ≥ tar ≥ 1,25·tpm; fusível gG 1,2·In ≤ In,f·Ta ≤ k·Ip,m (Ta = 0,85); cabos EPR/XLPE em trifólio, FCT 0,87, FCA por nº de circuitos (N = 9 como limite); ΔV terminal ≤ 4 %, total 7 %, partida ≤ 10 % nos terminais (PIE 05 slide 17, FP 0,30, uma célula por vez; rearme escalonado é requisito).
- Alimentador/CCM: I_alim = 1,25·In(maior motor) + Σ In; disjuntor MDWH/ACW (CCM6: ACW800U-ETM800, 800 mm² equivalentes = cabos em paralelo); barramento pelo PIE 05 slide 62.
- Comprimentos: limites superiores pela geometria do DWG **original** (lido só em cópia convertida, nunca editado).
- Potências: conferidas processo a processo com a matriz do usuário — **P14 = 3,5 cv** (o DWG diz '5,3CV'); **P17 = 28+9+2,5 cv/célula** (decisão final do usuário; os 23 cv são do P4/P13).

## 4. Restrições dadas pelo usuário (valem sempre)
Não alterar arquivos CAD (só leitura de cópia); não commitar sem pedir; fonte: aulas > catálogos > internet; classificar dados DADO DIRETO/CALCULADO/INFERIDO/PENDENTE; não inventar dados; confiabilidade > volume; responder em português; manter o `T3-Memorial de Calculo.docx` original intocado; pasta `T3/` enxuta. O `AGENTS.md` (roteamento CAD) só vale para modificação de CAD — nenhuma foi feita.

## 5. Verificações feitas
`verify.py` 0 divergências (6 CCMs); regressão CCM4/CCM5 sem diferença numérica; 25 processos × matriz do usuário (só P17 difere, por decisão); tabela 10.1 × aba CCMS; 28 slides × legendas; pacote docx (XML, ids, imagens órfãs, ordem de pPr); renderização do memorial no LibreOffice; originais intactos (`git diff` vazio).

## 6. Pendências reais
Motores de dupla/quádrupla tensão (P9, P17-M3, P21) a confirmar com a WEG; P22 (3:1, 45 kW × 'dica' de 30 cv); Icc real e ΔV a montante dos QDGM (T4); curva térmica dos disjuntores de célula e Icw da MSW (dados fora da pasta). **Nada foi aberto no Word/Excel** (só LibreOffice).

## 7. Armadilhas da sessão
`pkill -f` mata o próprio shell (use `kill PID`); a ferramenta Write usa `content` e exige Read prévio de arquivo existente; `evalx.py` leva ~2 min com 6 CCMs e não pode rodar em paralelo sobre o mesmo arquivo temporário; `unzip` não existe no ambiente (use `zipfile`); `curl` precisa de `-L` nos downloads da TDF.
