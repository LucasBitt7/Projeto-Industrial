# README - Projeto Recapadora de Pneus (EEL 2026-2)

Guia rapido para navegar e desenvolver o Projeto de Instalacoes
Eletricas Industriais da industria recapadora de pneus.

## Dados iniciais do projeto

Fonte: `01 - Dados Iniciais/PIE Industria RECAPADORA (EEL_2026-2) - Dados iniciais do projeto.pdf` (6 paginas).

Resumo do que esta definido no documento (sem inventar valores):

- Industria em altitude 1200 m, temperatura ambiente media 45C, tensao
  disponivel em BT 380/220 Vca, 60 Hz.
- 25 processos de producao (1 a 25), cada celula com maquina mecanica
  (potencia em CV), motores eletricos e, em alguns casos, carga termica.
- Motores devem ser WEG W22 IR3 Premium, dimensionados pelo torque
  equivalente exigido pela potencia mecanica.
- Cada celula tem um quadro de acionamento/protecao; os CCMs sao
  agrupados nos QDGM1 (CCM1 a CCM4) e QDGM2 (CCM5 e CCM6), com
  alimentacao em sistema N-1.
- Quadros de distribuicao: QDGBT (QDGF, QDGL, QDGM1, QDGM2) e
  QD-GERADOR (QDL1, QDF1); QDL0..7 e QDF0..7 por area.
- Corrente de curto-circuito presumida: 5 kA nos quadros de luz/forca
  e 7 kA nos CCMs; curto-circuito no ponto de entrega (AT) de 20 kA.
- Calculo de curto-circuito pela formulacao completa, no caminho
  QDGBT -> QDGM1 -> CCM2 -> P9A.
- Luminotecnico: metodo dos Lumens (Caldeiras, Bombas/Prensa, Deposito
  de Carcacas, Raspa, Sala de Produto, CQ, Banheiros, Escritorio e
  Subestacao) e metodo das Cavidades (Recapagem); lampadas vapor de
  sodio ou similares nas areas de producao; fluorescentes nas demais;
  luminarias antiexplosao na subestacao.
- Ampacidade e queda de tensao (trecho a trecho, formulacao completa)
  usando o catalogo PRYSMIAN (V/A.km).
- TUGs/TUEs: regras por area; chuveiros 9 kW nos banheiros;
  climatizadores em Sala de Produto, CQ e Escritorio.
- Gerador de emergencia externo, proximo a subestacao, para iluminacao
  (Recapagem, Caldeiras, Escritorio) e forca (Sala das Caldeiras).
- Plantas requeridas: entrada de servico (norma Celesc/PEP), diagramas
  unifilares, trifilares, sinotico de queda de tensao, alimentacao de
  cargas, tomadas/iluminacao e detalhes de execucao.
- Estrutura do memorial de calculo e descritivo: ordem QDGBT, QDGF,
  QDGL, QDGM1, QDGM2, QD-GERADOR com os QDLs/QDFs/CCMs por area.

## Funcao do arquivo DWG

`02 - Plantas e DWG/PROJETO INDUSTRIAL - RECAPADORA DE PNEUS - 2026-2.dwg`

- Planta CAD da industria recapadora (formato DWG 2018 / AC1032),
  fornecida como base para o desenvolvimento do projeto.
- Deve ser aberta em AutoCAD, ZWCAD, BricsCAD ou FreeCAD para visualizar
  as areas: Subestacao, Sala das Caldeiras, Bombas e Prensa, Deposito de
  Carcacas, Raspa, Recapagem, Escritorio, Sala de Produto/Controle de
  Qualidade e Banheiros, alem das celulas de producao P1 a P25.
- Sobre ela serao lançadas: plantas luminotecnica (T1), de maquinas
  motrizes/CCMs (T3) e o projeto completo (T4).
- Nao foi possivel converter/analisar o desenho neste ambiente (sem
  software CAD); o arquivo foi preservado intacto.

## Arquivos que servem de referencia

- Slides das aulas: `01 - Aulas e Slides/` (PIE 01 a PIE 11) - teoria,
  formulas e exemplos; o PIE 08 e citado nos dados iniciais para
  especificacao de motores.
- Tabelas luminotecnicas: `02 - Luminotecnica/A1 P1 - Tabelas Auxiliares -
  Calculos Luminotecnicos.pdf` (usada na A1P1 e no T1).
- Manual Prysmian: `03 - Cabos e Condutores/Manual Prysmian de
  Instalacoes Eletricas 2010.pdf` - catalogo OBRIGATORIO para ampacidade
  (tabelas por metodo de instalacao) e queda de tensao unitaria (V/A.km).
- Plano de ensino: `00 - Disciplina e Plano de Ensino/` - prazos e
  entregas T1 a T4.

## Catalogos que provavelmente serao necessarios (WEG)

Todos em `04 - Catalogos Tecnicos/WEG/` (nao ha copias na pasta do
projeto; consulte-os la):

- Motores: `01 - Motores/` (W22 - catalogo tecnico e guia de
  especificacao; motores W22 IR3 Premium exigidos).
- Protecao e manobra: `02 - Protecao e Manobra/` (disjuntores ACW/AGW/
  DWB/DWA, fusiveis NH, minidisjuntores, reles de sobrecarga termico e
  eletronico, temporizadores, seccionadores, contatores).
- Partida e velocidade: `03 - Partida de Motores e Velocidade/`
  (chaves de partida, soft-starter SSW, inversores CFW100/300/500/700 -
  processos 22 e 23 preveem velocidade variavel/tap).
- Fator de potencia: `04 - Correcao de Fator de Potencia/` (capacitores
  e reatores, contatores CWMC) - correcao por QDGM(n) exigida.
- Visao geral: `05 - Visao Geral da Linha/` (capacidade de interrupcao
  e finalidade de cada produto).

## Informacoes ainda a calcular/desenvolver

Com base nos dados iniciais (nao ha valores prontos no material):

1. Luminotecnica (T1): iluminancia por area, numero e posicionamento de
   luminarias (Lumens e Cavidades), especificacao de lampadas e
   luminarias, calculo das cargas de iluminacao.
2. Previsao de cargas e demanda: motores (CV -> kW considerando
   altitude, temperatura e rotacao), cargas termicas, TUGs/TUEs,
   calculo de demanda e fator de potencia por quadro.
3. Condutores (T2): secoes por ampacidade (com fatores de correcao de
   temperatura 45C/altitude 1200 m e agrupamento) e por queda de tensao
   (V/A.km do Prysmian), neutro, protecao, analise termica em regime e
   transitorio.
4. Protecao e manobra: disjuntores/fusiveis/reles por motor e por
   quadro (5 kA e 7 kA presumidos), seletividade, DDRs se aplicaveis.
5. Balanceamento de cargas e fases nos QDLs/QDFs.
6. Correcao de FP: capacitores por QDGM(n) com quadro QDMC(n).
7. Acionamentos: partida direta, estrela-triangulo, compensadora,
   serie-paralela, soft-starter e inversor conforme cada processo;
   contadores de tempo com intertravamento.
8. Curto-circuito pela formulacao completa (20 kA na AT, ramal 50 m,
   10 m trafo-QDGBT, caminho ate P9A).
9. Gerador de emergencia (cargas da recapagem, caldeiras e escritorio).
10. Documentacao CAD (T4): entrada de servico (Celesc/PEP), unifilares,
    trifilares, sinotico de queda de tensao, detalhes de execucao.

## Arquivos que devem ser consultados juntos

- Dados iniciais + planta DWG + plano de ensino (definem escopo e prazos).
- PIE 02 + tabelas auxiliares (A1 P1) para o T1 (luminotecnico).
- PIE 04/PIE 05 + Manual Prysmian para o T2 (condutores).
- PIE 08/PIE 09/PIE 10 + catalogos WEG (motores e acionamentos) para o T3.
- PIE 03/PIE 06/PIE 07/PIE 11 + catalogos WEG de protecao para o T4.

## Observacoes

- Os valores listados acima sao exatamente os do documento de dados
  iniciais; requisitos numericos novos (ex.: iluminancias-alvo) devem
  ser obtidos das normas (NBR 5413/ISO 8995) e do material de aula.
- Para a entrada de servico, o documento indica a norma Celesc/PEP
  (http://pep.celesc.com.br/PEP/docs/NormaPEP.pdf).
- ZIPs originais (dados, plantas e catalogos) preservados em
  `99 - Arquivos Originais Compactados/`.