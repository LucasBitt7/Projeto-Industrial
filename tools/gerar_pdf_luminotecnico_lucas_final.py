#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera PDF detalhado do luminotécnico - parte do Lucas (FINAL_REVISADA)."""
from fpdf import FPDF
from fpdf.fonts import FontFace
from pathlib import Path

OUT = Path("/mnt/c/Users/lucas/Desktop/Engenharia/ProjetosIndustriais/T1_LUMINOTECNICO_LUCAS_Passo_a_Passo_FINAL.pdf")

class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 7)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "T1  |  Luminotécnico  |  Parte do Lucas  |  Método dos Lumens  |  LUM-LUCAS_FINAL_REVISADA.xlsx", align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "", 7)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f"Página {self.page_no()}/{{nb}}", align="C")

pdf = PDF(orientation="P", unit="mm", format="A4")
pdf.alias_nb_pages("{nb}")
pdf.set_auto_page_break(True, margin=15)
pdf.set_margins(15, 15, 15)

# fontes unicode
pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
pdf.add_font("DejaVuMono", "", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")

AZUL = (31, 78, 120)
CINZA = (90, 90, 90)
PRETO = (30, 30, 30)
FUNDO_AZUL = (217, 234, 247)
FUNDO_AMARELO = (255, 243, 205)
BORDA_AMARELA = (200, 160, 40)

def capa():
    pdf.add_page()
    pdf.ln(18)
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(*AZUL)
    pdf.cell(0, 8, "PROJETO INDUSTRIAL  |  RECAPADORA DE PNEUS  (EEL 2026-2)  |  T1", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("DejaVu", "B", 26)
    pdf.set_text_color(*AZUL)
    pdf.multi_cell(0, 11, "Luminotécnico\nParte do Lucas", align="C")
    pdf.ln(2)
    pdf.set_font("DejaVu", "", 13)
    pdf.set_text_color(*CINZA)
    pdf.cell(0, 8, "Passo a passo detalhado  —  Método dos Lumens", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    # caixa
    pdf.set_fill_color(*FUNDO_AZUL)
    pdf.set_draw_color(*AZUL)
    x0 = pdf.get_x()
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(*PRETO)
    pdf.multi_cell(0, 6.5,
        "4 áreas:  Sala de Produtos (Saída de Produtos)  •  Controle de Qualidade  •  Banheiro / Vestiário  •  Escritório\n"
        "Luminária: TMS 426  2 x 40 W fluorescente (3 000 lm por lâmpada) + reator duplo 24,1 W, FP 0,90\n"
        "Resultado final:  38 luminárias  |  3 955,8 W  |  1 915,9 var  |  4 560 VA (adotado)  |  QDL5 + QDL6 + QDL7",
        border=1, fill=True, align="C")
    pdf.ln(6)
    pdf.set_font("DejaVu", "", 9.5)
    pdf.set_text_color(*PRETO)
    pdf.multi_cell(0, 5.5,
        "Este documento explica desde o zero como cada número foi obtido, com a fórmula, os valores substituídos e a origem de cada dado. "
        "Nenhum valor é inventado: tudo vem do enunciado, da aba DADOS (linhas 11 a 14), das Tabelas Auxiliares (Mamede / Philips) ou de uma premissa declarada.\n\n"
        "Base oficial: LUM-LUCAS_FINAL_REVISADA.xlsx (aba LUM-LUCAS, 219 linhas) + aba DADOS do PROJETO INDUSTRIAIS TRABALHO.xlsx + RESPONSABILIDADES.xlsx (parte do LUCAS). "
        "Critério da aula de 27/08: sempre usar a condição mais crítica (NOTES.txt: usar pot. vetorial P+jQ; sempre usar a mais crítica).")
    pdf.ln(4)
    pdf.set_fill_color(*FUNDO_AMARELO)
    pdf.set_draw_color(*BORDA_AMARELA)
    pdf.set_font("DejaVu", "B", 9.5)
    pdf.set_text_color(120, 80, 0)
    pdf.multi_cell(0, 6,
        "ATENÇÃO — LEIA PRIMEIRO: este memorial usa E = 200 / 1 500 / 200 / 750 lux (valor MÁXIMO entre faixa e específica). "
        "Versões antigas que usavam 500 lux no CQ e 250 lux no Escritório estão ERRADAS por usarem só a coluna “E específica”.",
        border=1, fill=True, align="C")
    pdf.ln(4)
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(*CINZA)
    pdf.multi_cell(0, 4.5,
        "Fontes: Dados iniciais do projeto PIE Recapadora (EEL 2026-2), 6 páginas  •  Slides PIE 02 (Mamede, NBR 5413)  •  A1 P1 Tabelas Auxiliares  •  Manual Philips TMS 426 + tabela de reatores\n"
        "Gerado em 2026-09-03 a partir da planilha FINAL_REVISADA. A planilha é a verdade oficial — este PDF é a explicação linha a linha.",
        align="C")

def h1(num, titulo):
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(*AZUL)
    pdf.ln(2)
    pdf.multi_cell(0, 7, f"{num}  {titulo}")
    pdf.set_draw_color(*AZUL)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)

def h2(titulo):
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(*AZUL)
    pdf.ln(1)
    pdf.multi_cell(0, 6, titulo)
    pdf.ln(1)

def p(texto, bold=False, size=9.5, color=PRETO):
    pdf.set_font("DejaVu", "B" if bold else "", size)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, 5.2, texto)
    pdf.ln(1)

def bullet(texto, size=9.5):
    pdf.set_font("DejaVu", "", size)
    pdf.set_text_color(*PRETO)
    x = pdf.get_x()
    pdf.cell(5, 5.2, "•")
    pdf.multi_cell(0, 5.2, texto)
    pdf.ln(0.5)

def caixa(texto, fill=FUNDO_AZUL, border=AZUL, tcolor=PRETO, bold=False, size=9.5):
    pdf.set_fill_color(*fill)
    pdf.set_draw_color(*border)
    pdf.set_font("DejaVu", "B" if bold else "", size)
    pdf.set_text_color(*tcolor)
    pdf.multi_cell(0, 5.5, texto, border=1, fill=True, align="L")
    pdf.ln(2)

def formula(texto):
    pdf.set_fill_color(240, 240, 240)
    pdf.set_draw_color(150, 150, 150)
    pdf.set_font("DejaVuMono", "", 9)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 6, texto, border=1, fill=True, align="C")
    pdf.ln(2)

def tabela(headers, rows, widths=None, fontsize=8):
    if widths is None:
        w = (pdf.w - 30) / len(headers)
        widths = [w]*len(headers)
    pdf.set_font("DejaVu", "B", fontsize)
    pdf.set_fill_color(*AZUL)
    pdf.set_text_color(255, 255, 255)
    pdf.set_draw_color(*AZUL)
    for i, h in enumerate(headers):
        pdf.cell(widths[i], 7, h, border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_font("DejaVu", "", fontsize)
    pdf.set_text_color(*PRETO)
    pdf.set_draw_color(180, 200, 215)
    fill = False
    for row in rows:
        # calcula altura
        hmax = 6
        # desenha
        if fill:
            pdf.set_fill_color(235, 244, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        y0 = pdf.get_y()
        x0 = pdf.get_x()
        # usa multicell por coluna? simplificado: cell com altura fixa, quebra manual curta
        for i, cell in enumerate(row):
            pdf.set_xy(x0 + sum(widths[:i]), y0)
            # estima linhas
            pdf.multi_cell(widths[i], 6, str(cell), border=1, fill=True, align="C")
        # ajusta y para a maior altura
        y1 = pdf.get_y()
        # na prática multi_cell sequencial quebra; então reimplementamos com table() nativa para robustez:
        fill = not fill
    # NOTA: acima o desenho manual com multi_cell sequencial não alinha; por isso usamos o motor table abaixo quando necessário.
    # Para garantir alinhamento perfeito, redesenhamos com fpdf.table se a tabela for simples:
    pass

def tabela2(headers, rows, col_widths=None, fontsize=7.5):
    """Usa o motor nativo de tabelas do fpdf2 (alinhado)."""
    style_h = FontFace(emphasis="BOLD", color=(255,255,255), fill_color=AZUL)
    pdf.set_font("DejaVu", "", fontsize)
    with pdf.table(
        col_widths=col_widths,
        text_align="CENTER",
        line_height=5.2,
        first_row_as_headings=True,
        headings_style=style_h,
        width=pdf.w - 30,
    ) as table:
        table.row(headers)
        for r in rows:
            table.row([str(c) for c in r])

# ============ CONTEÚDO ============
capa()

# --- INDICE ---
pdf.add_page()
h1("Sumário", "")
p("Leia na ordem. Cada seção depende da anterior. Se precisar defender um número em aula, siga a cadeia: enunciado → tabela citada → fórmula → substituição → verificação.", bold=True)
for item in [
    "1. Onde está a parte do Lucas (e como conferir na planilha)",
    "2. O que o enunciado exige (com citações literais)",
    "3. Fundamentos em 5 minutos (grandezas + lógica do Método dos Lumens)",
    "4. Dados de entrada (dimensões, pé-direito, plano de trabalho)",
    "5. Iluminância E — a etapa mais crítica (peso + MAX faixa × específica)",
    "6. Luminária, lâmpada e reator (de onde vêm 6 000 lm, 104,1 W, 120 VA)",
    "7. Refletâncias (o que é dado e o que é premissa — bege 35%)",
    "8. Índice K e fator Fu (com as 4 interpolações abertas número a número)",
    "9. Fator de depreciação Fdl = 0,75",
    "10. Fluxo total e número de luminárias (com substituições completas)",
    "11. Distribuição na planta (grades + regra X,Y ≤ 1,5×Hlp)",
    "12. Carga elétrica P+jQ e E obtida (potência vetorial)",
    "13. Resumo por QDL e total geral",
    "14. Verificação, premissas, checklist de apresentação e referências",
]:
    bullet(item, size=9.5)

# --- 1 ---
pdf.add_page()
h1("1.", "Onde está a parte do Lucas (e como conferir na planilha)")
p("A divisão do trabalho está no arquivo RESPONSABILIDADES.xlsx. O LUCAS responde por 4 ambientes, no memorial e na planta do T1. Todo o resto do T1 (Caldeiras, Bombas/Prensa, Depósitos, Raspa, Recapagem, Subestação) é de Dante, Pietro e João.")
tabela2(["Etapa", "Responsável", "Atividade"],
    [["T1 memorial + planta", "LUCAS", "Saída de Produtos (Sala de Produtos)"],
     ["T1 memorial + planta", "LUCAS", "Controle de Qualidade"],
     ["T1 memorial + planta", "LUCAS", "Banheiro (Vestiário)"],
     ["T1 memorial + planta", "LUCAS", "Escritório"]],
    col_widths=(45, 30, 105))
pdf.ln(2)
p("Na planilha oficial, esses 4 ambientes são exatamente as linhas 11 a 14 da aba DADOS (PROJETO INDUSTRIAIS TRABALHO.xlsx) e as linhas 3 a 6 da aba LUM-LUCAS (LUM-LUCAS_FINAL_REVISADA.xlsx). Se alguém mudar uma dimensão, a aba LUM-LUCAS recalcula tudo por fórmula — não há número digitado à mão nos resultados.", bold=True)
tabela2(["Ambiente", "Linha DADOS", "Linha LUM-LUCAS", "QDL destino"],
    [["Sala de Produtos", "11", "3 / 22 / 82 / 103...", "QDL6"],
     ["Controle de Qualidade", "12", "4 / 23 / 83 / 104...", "QDL6"],
     ["Banheiro / Vestiário", "13", "5 / 24 / 84 / 105...", "QDL7"],
     ["Escritório", "14", "6 / 25 / 85 / 106...", "QDL5"]],
    col_widths=(55, 30, 45, 50))
pdf.ln(2)
caixa("Como conferir em 1 minuto: abra LUM-LUCAS_FINAL_REVISADA.xlsx → aba LUM-LUCAS → coluna A. As fórmulas usam =A3, =B3*C3, =ROUNDUP etc. As células amarelas são premissas editáveis (E, refletâncias, Fdl, fluxo da lâmpada). As verdes/azuis são calculadas. Mude D12 (Fdl) ou B67 (fluxo) e veja a coluna Nlu recalcular.", bold=False)

# --- 2 ---
pdf.add_page()
h1("2.", "O que o enunciado exige (citações literais)")
p("Os trechos abaixo são transcrições do arquivo “PIE Industria RECAPADORA (EEL_2026-2) - Dados iniciais do projeto.pdf”. Eles definem método, altura, lâmpada e piso — e amarram cada escolha do memorial.")
caixa("“Para as áreas Sala de Caldeiras, Compressor (Bombas e Prensa), Depósito de Carcaças e Raspa → O método utilizado deverá ser o de Lumens.” — Dados iniciais, p. 5/6", fill=(232,241,248), border=AZUL)
caixa("“Para a área Recapagem → O método utilizado deverá ser o de Cavidades.” — Dados iniciais, p. 5/6 (por isso a Recapagem NÃO é do Lucas e NÃO entra neste PDF)", fill=(232,241,248), border=AZUL)
caixa("“A altura de manuseio para o trabalho é de 0,8 metros.” — Dados iniciais, p. 5/6  →  Hpp = 0,80 m em todas as 4 salas.", fill=(232,241,248), border=AZUL)
p("Para as áreas do Lucas (Sala de Produto, CQ, Banheiro, Escritório) o memorial do grupo adota o Método dos Lumens, com piso em azulejo cinza e lâmpadas fluorescentes ou similares — coerente com o texto do enunciado que autoriza “lâmpadas de vapor de sódio, ou similares” nas áreas industriais altas e fluorescentes nas demais áreas administrativas. A estrutura do memorial deve seguir a ordem QDGBT → QDGF → QDGL → QDGM1 → QDGM2 → QD-GERADOR, com QDL5 (Escritório), QDL6 (Sala de Produto + CQ) e QDL7 (Banheiros).", size=9.5)
bullet("Tensão BT 380/220 V, 60 Hz; altitude 1 200 m; 45 °C — dados que serão usados nas etapas T2/T3 (condutores, motores), mas que já fixam 220 V como tensão de cálculo das cargas de iluminação.")
bullet("Curto presumido 5 kA nos QDLs/QDFs (7 kA só nos CCMs) — não dimensiona lâmpada, mas será usado na escolha dos disjuntores dos circuitos L18–L21 (ver PDF QDL_QDGL_QDF_LUCAS).")
bullet("TUG/TUE dessas 4 áreas pelo método residencial/comercial da NBR 5410; climatizadores na Sala de Produto, CQ e Escritório; chuveiros 9 kW nos Banheiros — etapa QDF, fora do escopo luminotécnico, mas citada para rastreabilidade.")

# --- 3 ---
pdf.add_page()
h1("3.", "Fundamentos em 5 minutos")
h2("3.1  As 6 grandezas que você precisa saber")
tabela2(["Grandeza", "Símb.", "Unidade", "Significado em 1 frase"],
    [["Fluxo luminoso", "Φ", "lúmen (lm)", "Luz total que a fonte emite"],
     ["Iluminância", "E", "lux = lm/m²", "Luz que chega em cada m² do plano de trabalho"],
     ["Área", "S", "m²", "Largura × comprimento"],
     ["Fator de utilização", "Fu", "— (0 a 1)", "Fração do fluxo que realmente atinge o plano útil"],
     ["Fator de depreciação", "Fdl", "— (0 a 1)", "Desconto por sujeira + envelhecimento"],
     ["Índice do recinto", "K", "—", "Proporção entre área e altura útil; diz em que linha da tabela ler o Fu"]],
    col_widths=(38, 14, 28, 100))
pdf.ln(2)
p("Diferenças que confundem: lâmpada é a fonte (o tubo fluorescente de 40 W); luminária é o conjunto completo (carcaça TMS 426 + 2 lâmpadas + reator); reator é o acessório que limita a corrente e dissipa 24,1 W em calor; fluxo por luminária = 2 × 3 000 = 6 000 lm.")
h2("3.2  A lógica do Método dos Lumens em 4 passos")
p("1. A norma fixa o alvo E para a atividade. O fluxo útil que precisa chegar ao plano de trabalho é E × S.")
formula("Passo 1 — fluxo útil:   Φútil  =  E × S")
p("2. Nem toda luz chega: parte é absorvida por teto/parede (Fu) e parte se perde com sujeira/idade (Fdl). Por isso divide-se por Fu×Fdl para achar o fluxo que as lâmpadas precisam emitir.")
formula("Passo 2 — fluxo das lâmpadas:   Φt  =  E × S / (Fu × Fdl)")
p("3. Cada luminária entrega um fluxo fixo (n_lamp × φ_lamp). Dividir dá a quantidade teórica.")
formula("Passo 3 — quantidade:   Nteórico  =  Φt / (n_lamp × φ_lamp)      →      Ninstalado = teto(Nteórico)")
p("4. Arredonda-se SEMPRE para cima e recalcula-se a iluminância que realmente será obtida com o N instalado. Se arredondasse para baixo, E ficaria abaixo da norma.")
formula("Passo 4 — verificação:   Eobtida  =  N × n_lamp × φ_lamp × Fu × Fdl / S    (exigido: Eobtida ≥ E)")
caixa("Altura útil:  Hlp = Htp − Hpp = 3,00 − 0,80 = 2,20 m.  Índice do recinto:  K = L×C / [Hlp×(L+C)].  K diz se a sala é “baixa e compacta” (Fu alto) ou “alta e esguia” (Fu baixo).", bold=True)

# --- 4 ---
pdf.add_page()
h1("4.", "Dados de entrada (nada é inventado)")
p("Dimensões e pé-direito vêm da aba DADOS. Plano de trabalho Hpp = 0,80 m vem do enunciado. Hlp é calculado.")
tabela2(["Ambiente", "L × C [m]", "S [m²]", "Htp [m]", "Hpp [m]", "Hlp [m]"],
    [["Sala de Produtos", "5,00 × 6,00", "30,000", "3,00", "0,80", "2,20"],
     ["Controle de Qualidade", "5,00 × 6,00", "30,000", "3,00", "0,80", "2,20"],
     ["Banheiro / Vestiário", "5,23 × 3,50", "18,305", "3,00", "0,80", "2,20"],
     ["Escritório", "8,12 × 6,00", "48,720", "3,00", "0,80", "2,20"]],
    col_widths=(48, 30, 22, 20, 20, 20), fontsize=7.5)
pdf.ln(2)
p("Cálculo de S (exemplo Sala de Produtos): S = 5,00 × 6,00 = 30,00 m². Banheiro: S = 5,23 × 3,50 = 18,305 m². Escritório: S = 8,12 × 6,00 = 48,72 m². Hlp = 3,00 − 0,80 = 2,20 m em todas (fórmula =E3−D3 na planilha). Se as luminárias forem penduradas por tirante abaixo do teto, Hlp passa a ser altura de instalação − 0,80 (não é o caso aqui: instalação no teto, pé-direito 3 m).")
h2("4.1  Índice K — conta aberta")
formula("K = L×C / [Hlp×(L+C)]")
tabela2(["Ambiente", "Conta", "K"],
    [["Sala de Produtos", "30,00 / [2,20×11,00] = 30,00/24,20", "1,2397"],
     ["Controle de Qualidade", "30,00 / [2,20×11,00] = 30,00/24,20", "1,2397"],
     ["Banheiro", "18,305 / [2,20×8,73] = 18,305/19,206", "0,9531"],
     ["Escritório", "48,72 / [2,20×14,12] = 48,72/31,064", "1,5684"]],
    col_widths=(45, 75, 30))
pdf.ln(1)
p("Interpretação: o Banheiro tem o menor K (0,95) — é proporcionalmente mais “alto” que os demais, então seu Fu é o menor (0,426) e cada lúmen instalado rende menos. O Escritório tem o maior K (1,57) — sala mais “baixa e ampla”, Fu maior (0,567). Salas com mesma área (Sala de Produtos e CQ, ambas 30 m²) têm o mesmo K, mas Fu diferente porque as refletâncias diferem (ver seção 7).")

# --- 5 ---
pdf.add_page()
h1("5.", "Iluminância E — a etapa mais crítica (leia com atenção)")
p("E não é escolhido pela metragem. É escolhido pela ATIVIDADE VISUAL, em duas tabelas da NBR 5413 / Mamede: (a) faixa por tipo de ambiente + peso (idade, precisão, refletância do fundo); (b) valor específico por atividade. No final vale o MAIOR dos dois — “sempre usar a mais crítica” (aula 27/08). Foi exatamente isso que a planilha FINAL_REVISADA faz com =MAX(H22,I22).")
h2("5.1  Peso: por que vale o valor médio da faixa")
tabela2(["Característica adotada", "Valor", "Peso (Tab. 2.5)"],
    [["Idade dos observadores", "41 anos (40 a 55)", "0"],
     ["Velocidade e precisão", "Importante", "0"],
     ["Refletância do fundo da tarefa", "0,40 (30 a 70%)", "0"],
     ["SOMA", "—", "0 → usa o valor MÉDIO da faixa"]],
    col_widths=(70, 45, 65))
pdf.ln(2)
p("Regra da Tab. 2.5 (PIE 02, p. 60): soma −2 ou menos → usa o inferior; soma +2 ou mais → usa o superior; soma −1 a +1 (nosso caso, soma 0) → usa o valor médio da faixa. Por isso a coluna H da planilha usa =IF(G22<=-2,D22,IF(G22>=2,F22,E22)) e resulta em 150 / 1 500 / 75 / 750 lux.")
h2("5.2  Faixa × específica → MAX (a correção que mudou tudo)")
tabela2(["Ambiente", "Faixa", "E faixa (médio)", "E específica", "E ADOTADA = MAX"],
    [["Sala de Produtos", "A: depósito, 100-150-200", "150", "200 (armazen. grandes vol.)", "200"],
     ["Controle de Qualidade", "B: inspeção, 1000-1500-2000", "1 500", "500 (inspeção — valor antigo)", "1 500"],
     ["Banheiro", "A: permanência curta, 50-75-100", "75", "200 (banheiros)", "200"],
     ["Escritório", "B: escritório, 500-750-1000", "750", "250 (sala de trabalho — antigo)", "750"]],
    col_widths=(38, 48, 30, 38, 26), fontsize=7)
pdf.ln(2)
caixa("Por que CQ = 1 500 e Escritório = 750 (e não 500 e 250)? Porque a coluna “E específica” (500/250) é um mínimo genérico da Tab. 2.6, enquanto a faixa (1 500/750) já considera o peso da tarefa. A regra do projeto é ficar com o MAIOR. Usar 500/250 subdimensionaria o CQ em 3× e o Escritório em 3× — erro grave que a versão FINAL_REVISADA corrigiu. Na planilha: J22==MAX(H22,I22), J23==MAX(H23,I23), etc.", fill=FUNDO_AMARELO, border=BORDA_AMARELA, bold=False)
p("Classificações adotadas (coluna B da planilha, Tab. 2.6): Sala de Produtos = “Locais de armazenamento – grandes volumes”; CQ = “Inspeção / Controle de Qualidade” (tarefa especial, exige 1 500 lux); Banheiro = “Banheiros / Vestiários”; Escritório = “Escritórios – sala de trabalho”. São decisões de engenharia documentadas nas linhas 29–32 da planilha — mantenha esses nomes no memorial.")

# --- 6 ---
pdf.add_page()
h1("6.", "Luminária, lâmpada e reator")
p("Escolha: TMS 426 – 2 lâmpadas fluorescentes de 40 W (Tab. 2.9 das Tabelas Auxiliares). Não é a única possível (TMS 500, TCK 427, HDK 472 existem na tabela), mas é a mais rastreável: a tabela dá ao mesmo tempo a luminária, o Fu e os dados do reator. Trocar por LED exigiria substituir Fu e dados elétricos por ficha de fabricante.")
tabela2(["Item", "Valor adotado", "Origem"],
    [["Luminária", "TMS 426, 2 × 40 W, Philips", "Tab. 2.9"],
     ["Lâmpada", "Fluorescente comum 40 W, 3 000 lm", "Tab. 2.1"],
     ["Fluxo por luminária", "2 × 3 000 = 6 000 lm", "Cálculo"],
     ["Reator", "Duplo 2×40 W, 220 V, perdas 24,1 W, FP 0,90, catálogo 0,51 A", "Tabela de reatores"],
     ["Aplicação", "Interiores de baixo pé-direito (3 m) — adequada às 4 salas", "Catálogo Philips"]],
    col_widths=(40, 65, 75))
pdf.ln(2)
h2("6.1  Carga de UMA luminária (conta que se repete 38 vezes)")
formula("P_lum = 2×40 + 24,1 = 104,1 W\nQ_lum = P × tan(arccos 0,90) = 104,1 × 0,4843 = 50,42 var\nS_exata = √(P²+Q²) = √(104,1²+50,42²) = 115,67 VA  →  S_adotada = 120 VA/ponto\nI_exata = 115,67/220 = 0,53 A  |  I_adotada = 120/220 = 0,55 A  (catálogo: 0,51 A — diferença de arredondamento, planilha mantém o cálculo)")
p("Por que S adotada = 120 VA e não 115,67 VA? Porque as etapas seguintes (QDL, condutores, proteção) trabalham com potência aparente arredondada por ponto, a favor da segurança, e porque 120 VA × N dá números inteiros (3×120=360, 18×120=2 160...). A planilha guarda as duas: S exata (física) e S adotada (projeto). E por que P+jQ? Porque a nota do projeto exige potência vetorial — o reator é indutivo, então Q ≠ 0 e S > P. Ignorar Q subdimensionaria corrente e condutor.")
caixa("1 luminária = 104,1 W + j 50,42 var  →  115,67 VA (exata)  →  120 VA (projeto)  →  0,55 A em 220 V. Guarde esses 4 números: eles multiplicam tudo.", bold=True)

# --- 7 ---
pdf.add_page()
h1("7.", "Refletâncias (o que é dado e o que é premissa)")
p("Refletância ρ = fração da luz que a superfície devolve. Teto/parede claros devolvem mais luz → Fu maior → menos luminárias. A Tab. de refletâncias dá: branco-neve 80, branco-marfim 70, creme-claro 70, bege 45, cinza-claro 45. A Tab. 2.9 (Fu da TMS 426) só tem colunas para teto 70/50/30 e parede 50/30/10, sempre com piso 10%.")
tabela2(["Amb.", "DADO (planilha)", "Adotado", "Critério"],
    [["S. Produtos", "Teto CLARO / Parede CLARA", "50% / 50%", "CLARO/CLARA = descrição qualitativa → coluna clara 50/50; piso azulejo cinza registrado, mas tabela só tem piso 10%"],
     ["CQ", "Teto BRANCO / Parede BRANCA", "70% / 50%", "BRANCO = branco-neve 80%, mas tabela não tem 80% → usa o limite 70%; parede idem → maior coluna 50%"],
     ["Banheiro", "Teto CLARO / Parede CLARA", "50% / 50%", "Igual à Sala de Produtos"],
     ["Escritório", "Teto BRANCO / Parede BEGE", "70% / 35%", "BEGE = 35–40% → adotado 35% (mais crítico); interpola entre parede 30% e 50%"]],
    col_widths=(28, 52, 30, 70), fontsize=7.5)
pdf.ln(2)
caixa("Pontos para defender: (1) CLARO/CLARA não é número medido — 50% é premissa compatível com “ambiente claro”. (2) BRANCO seria 80%, mas a tabela não tem 80% — usa-se 70% (regra do slide PIE 02 p. 67: “se exceder o tabelado, usa-se a mais próxima”). (3) BEGE 35% é o limite inferior da faixa 35–40% — escolha a favor da segurança; se o professor exigir 45%, o Fu sobe de 0,567 para ~0,60 e o N do Escritório pode cair de 15 para 14 (recalcular). (4) Piso azulejo cinza foi registrado, mas o Fu publicado é para piso 10% — limitação declarada, não erro.", fill=FUNDO_AMARELO, border=BORDA_AMARELA)

# --- 8 ---
pdf.add_page()
h1("8.", "Fator de utilização Fu (com as 4 interpolações abertas)")
p("Fu = fração do fluxo das lâmpadas que atinge o plano útil. Depende de K + refletâncias. Lê-se na Tab. 2.9 da TMS 426; se K cair entre duas linhas, interpola-se (PIE 02 p. 67: “a interpolação define um valor entre os limites tabelados”). Se a parede cair entre duas colunas (bege 35%), interpola-se de novo entre colunas.")
formula("Interpolação em K:  Fu = Fu_inf + (K − K_inf)/(K_sup − K_inf) × (Fu_sup − Fu_inf)\nInterpolação entre colunas (só Escritório):  Fu(35%) = Fu(30%) + (35−30)/(50−30) × [Fu(50%) − Fu(30%)]")
h2("8.1  Sala de Produtos — 50/50, K = 1,2397 entre 1,00 (Fu 0,44) e 1,25 (Fu 0,49)")
formula("Fu = 0,44 + (1,2397−1,00)/(1,25−1,00) × (0,49−0,44) = 0,44 + 0,9588 × 0,05 = 0,4879")
h2("8.2  Controle de Qualidade — 70/50, K = 1,2397 entre 1,00 (Fu 0,50) e 1,25 (Fu 0,56)")
formula("Fu = 0,50 + (1,2397−1,00)/0,25 × (0,56−0,50) = 0,50 + 0,9588 × 0,06 = 0,5575")
h2("8.3  Banheiro — 50/50, K = 0,9531 entre 0,80 (Fu 0,38) e 1,00 (Fu 0,44)")
formula("Fu = 0,38 + (0,9531−0,80)/(1,00−0,80) × (0,44−0,38) = 0,38 + 0,7654 × 0,06 = 0,4259")
h2("8.4  Escritório — 70/30 ↔ 70/50, K = 1,5684 entre 1,50 e 2,00, parede 35% (interpolação dupla)")
formula("Fu(30%) = 0,54 + (1,5684−1,50)/0,50 × (0,61−0,54) = 0,54 + 0,1367 × 0,07 = 0,5496\nFu(50%) = 0,61 + (1,5684−1,50)/0,50 × (0,68−0,61) = 0,61 + 0,1367 × 0,07 = 0,6196\nFu(35%) = 0,5496 + (35−30)/(50−30) × (0,6196−0,5496) = 0,5496 + 0,25 × 0,07 = 0,5671")
caixa("Resumo Fu:  Sala de Produtos 0,488  |  CQ 0,558  |  Banheiro 0,426  |  Escritório 0,567.  Na planilha: H103==0,44+(E103−1)/0,25×0,05; H104==0,50+(E104−1)/0,25×0,06; H105==0,38+(E105−0,8)/0,2×0,06; H106==dupla interpolação. Confira os vizinhos na Tab. 2.9 antes de apresentar.", bold=True)

# --- 9 ---
pdf.add_page()
h1("9.", "Fator de depreciação Fdl = 0,75")
p("Fdl desconta sujeira + envelhecimento. Como está no denominador de Φt, Fdl menor → mais fluxo exigido → mais luminárias. A planilha adota Fdl = 0,75 (categoria “luminária comercial”, Tabela 2.9 de Mamede / quadro de Fdl das Tabelas Auxiliares).")
caixa("“Luminária comercial … 0,75” — Tabelas Auxiliares, quadro de Fdl  |  “Na ausência de dados de manutenção … Fdl = 0,7” — PIE 02 p. 69. Critério: existe valor específico para o tipo adotado (0,75), então ele prevalece sobre o genérico 0,70. Na dúvida prevalece o menor (aula p. 70) — aqui não há dúvida porque há dado específico. Célula B121 da planilha.", fill=(232,241,248), border=AZUL)
formula("Φt = E × S / (Fu × Fdl)      com Fdl = 0,75 em todas as 4 salas")
p("Sensibilidade: se o professor exigir Fdl = 0,70, o fluxo sobe ×(0,75/0,70) = +7,1% e o CQ (folga pequena) pode pedir luminária extra. Deixe B121 editável e mostre os dois cenários na apresentação — isso demonstra domínio, não erro.")

# --- 10 ---
h1("10.", "Fluxo total e número de luminárias (conta completa)")
p("Agora é só substituir. Fluxo por luminária = 6 000 lm em todas.")
tabela2(["Ambiente", "E×S", "Fu×Fdl", "Φt = E×S/(Fu×Fdl)", "Nteórico = Φt/6000", "N adotado"],
    [["S. Produtos", "200×30 = 6 000", "0,4879×0,75=0,3660", "16 395,66 lm", "2,7326 →", "3"],
     ["CQ", "1500×30 = 45 000", "0,5575×0,75=0,4181", "107 619,33 lm", "17,9366 →", "18"],
     ["Banheiro", "200×18,305 = 3 661", "0,4259×0,75=0,3194", "11 460,51 lm", "1,9101 →", "2"],
     ["Escritório", "750×48,72 = 36 540", "0,5671×0,75=0,4253", "85 914,94 lm", "14,3192 →", "15"]],
    col_widths=(30, 38, 38, 34, 22, 18), fontsize=7)
pdf.ln(2)
p("Exemplo aberto — Sala de Produtos:", bold=True)
formula("Φt = 200 × 30,00 / (0,4879 × 0,75) = 6 000 / 0,36595 = 16 395,66 lm\nNteórico = 16 395,66 / (2 × 3 000) = 16 395,66 / 6 000 = 2,7326  →  N = teto(2,7326) = 3  (grade 3×1)")
p("Exemplo aberto — CQ (o maior):", bold=True)
formula("Φt = 1 500 × 30,00 / (0,5575 × 0,75) = 45 000 / 0,41814 = 107 619,33 lm\nNteórico = 107 619,33 / 6 000 = 17,9366  →  N = 18  (grade 6×3)")
p("Exemplo aberto — Banheiro:", bold=True)
formula("Φt = 200 × 18,305 / (0,4259 × 0,75) = 3 661,00 / 0,31944 = 11 460,51 lm\nNteórico = 11 460,51 / 6 000 = 1,9101  →  N = 2  (grade 1×2)")
p("Exemplo aberto — Escritório:", bold=True)
formula("Φt = 750 × 48,72 / (0,5671 × 0,75) = 36 540,00 / 0,42530 = 85 914,94 lm\nNteórico = 85 914,94 / 6 000 = 14,3192  →  N = 15  (grade 3×5)")
caixa("Arredondamento sempre para cima (ROUNDUP na planilha, col. F158:F161). 2 luminárias na Sala de Produtos dariam E = 146 lux < 200 — reprovado. Por isso 2,73 vira 3, 17,94 vira 18, 1,91 vira 2 e 14,32 vira 15.", bold=True)

# --- 11 ---
pdf.add_page()
h1("11.", "Distribuição na planta (quantidade → desenho)")
p("A planilha calcula a quantidade; o CAD confirma se ela cabe com espaçamento uniforme. Regra da aula (PIE 02 p. 74):")
formula("X, Y ≤ 1,5 × Hlp  =  1,5 × 2,20  =  3,30 m  ;   X1 = X/2 ,  Y1 = Y/2  (meia distância nas bordas)")
tabela2(["Ambiente", "Grade", "X / X1 [m]", "Y / Y1 [m]", "1,5×Hlp", "Veredito"],
    [["S. Produtos (5×6)", "3×1 = 3", "2,00 / 1,00", "— / 2,50", "3,30", "CERTO"],
     ["CQ (5×6)", "6×3 = 18", "1,00 / 0,50", "1,67 / 0,83", "3,30", "CERTO"],
     ["Banheiro (5,23×3,5)", "1×2 = 2", "— / 1,75", "2,62 / 1,31", "3,30", "CERTO"],
     ["Escritório (8,12×6)", "3×5 = 15", "2,00 / 1,00", "1,62 / 0,81", "3,30", "CERTO"]],
    col_widths=(36, 22, 32, 32, 22, 36), fontsize=7.5)
pdf.ln(2)
p("Como ler: Sala de Produtos 3×1 significa 3 colunas ao longo dos 6 m (X = 6/3 = 2,00 m, borda X1 = 1,00 m) e 1 fileira nos 5 m (Y = 0, borda Y1 = 2,50 m). CQ 6×3: X = 6/6 = 1,00 m, Y = 5/3 = 1,67 m. Banheiro 1×2: 1 coluna (X1 = 3,50/2 = 1,75 m) e 2 fileiras (Y = 5,23/2 = 2,615 m). Escritório 3×5: X = 6/3 = 2,00 m, Y = 8,12/5 = 1,624 m. Todos os máximos ≤ 3,30 m → CERTO (col. J167:J170).")
caixa("Papel do CAD: conferir portas, pilares, climatizadores e portas de armário; se a grade precisar de 1 ponto extra por obstáculo, recalcular Eobtida. A quantidade da planilha é o MÍNIMO normativo — o desenho pode exigir mais, nunca menos.", fill=FUNDO_AMARELO, border=BORDA_AMARELA)

# --- 12 ---
h1("12.", "Carga elétrica P+jQ e iluminância obtida")
p("Cada luminária consome P e Q (reator indutivo). A planilha registra potência vetorial por ambiente (P+jQ), S exata, S adotada (120 VA×N), correntes e E obtida — exatamente o que a nota “Usar pot. vetorial p+jQ” cobra.")
formula("P_amb = N × 104,1  |  Q_amb = N × 50,42  |  S_exata = √(P²+Q²)  |  S_adot = N × 120  |  I = S/220  |  Eobt = N×6000×Fu×Fdl/S")
tabela2(["Ambiente", "N", "P [W]", "Q [var]", "S adot. [VA]", "I adot. [A]", "E obt. [lux]"],
    [["S. Produtos", "3", "312,3", "151,25", "360", "1,64", "219,6 ≥ 200 OK"],
     ["CQ", "18", "1 873,8", "907,52", "2 160", "9,82", "1 505,3 ≥ 1500 OK"],
     ["Banheiro", "2", "208,2", "100,84", "240", "1,09", "209,4 ≥ 200 OK"],
     ["Escritório", "15", "1 561,5", "756,27", "1 800", "8,18", "785,7 ≥ 750 OK"]],
    col_widths=(30, 14, 26, 26, 28, 24, 32), fontsize=7.5)
pdf.ln(2)
p("Exemplo aberto — E obtida da Sala de Produtos:", bold=True)
formula("Eobt = 3 × 6 000 × 0,4879 × 0,75 / 30,00 = 13 174,21 / 60  →  219,57 lux  ≥  200  ✓  (folga +19,6 lux, +9,8%)")
p("Folgas (Eobt − E): Sala de Produtos +19,6 (+9,8%); CQ +5,3 (+0,4% — a mais apertada, qualquer revisão de Fdl/fluxo mexe nela); Banheiro +9,4 (+4,7%); Escritório +35,7 (+4,8%). Folga pequena no CQ é normal: 17,94 → 18 dá só +0,36% de sobra teórica antes do Fu arredondado; o cálculo exato com Fu 0,5575 fecha em +0,35%. É o ambiente para destacar na apresentação como “ponto de atenção”.")
caixa("Corrente de referência (não dimensiona ainda): I = S_adot/220. Ex.: CQ 2 160/220 = 9,82 A; Escritório 1 800/220 = 8,18 A. O dimensionamento de condutor/disjuntor vem no T2 com método de instalação, agrupamento, queda de tensão e 5 kA (ver PDF QDL_QDGL_QDF_LUCAS).", bold=False)

# --- 13 ---
pdf.add_page()
h1("13.", "Resumo por QDL e total geral")
p("O enunciado fixa: QDL5 = Escritório; QDL6 = Sala de Produto + CQ; QDL7 = Banheiros (p. 2/6). A planilha fecha exatamente assim (linhas 197–200).")
tabela2(["QDL", "Ambientes", "Luminárias", "P [W]", "Q [var]", "S adot. [VA]", "I adot. [A]"],
    [["QDL5", "Escritório", "15", "1 561,5", "756,27", "1 800", "8,18"],
     ["QDL6", "S. Produtos + CQ", "21 (3+18)", "2 186,1", "1 058,78", "2 520", "11,45"],
     ["QDL7", "Banheiro", "2", "208,2", "100,84", "240", "1,09"],
     ["TOTAL", "4 ambientes", "38", "3 955,8", "1 915,88", "4 560", "20,73*"]],
    col_widths=(22, 42, 26, 24, 24, 26, 22), fontsize=7.5)
pdf.ln(1)
p("* Total I = soma das correntes de referência (1,64+9,82+1,09+8,18 = 20,73 A). Não é corrente trifásica — cada QDL/circuito será distribuído por fase no balanceamento (etapa QDL, PDF irmão). O que vale para o T1 é: 38 pontos × 120 VA = 4 560 VA de carga de iluminação da parte do Lucas, sendo 1 800 VA no QDL5, 2 520 VA no QDL6 e 240 VA no QDL7.")
caixa("TOTAL DA PARTE DO LUCAS:  38 luminárias TMS 426 (3 + 18 + 2 + 15)  |  P = 3 955,8 W  |  Q = 1 915,9 var  |  S = 4 560 VA (adotado)  |  E obtida 219,6 / 1 505,3 / 209,4 / 785,7 lux — todas ≥ alvo.", bold=True, fill=(232,241,248), border=AZUL)

# --- 14 ---
h1("14.", "Verificação, premissas, checklist e referências")
h2("14.1  Verificação técnica final (como está na planilha, linhas 202–211)")
tabela2(["Item", "Verificação", "Resultado"],
    [["Método", "Lumens nas 4 áreas", "OK"],
     ["Peso E", "41 anos + importante + 40% → soma 0 → valor médio", "OK"],
     ["E final", "MAX(faixa, específica) = 200/1500/200/750", "OK (mais crítica)"],
     ["Refletâncias", "50/50, 70/50, 50/50, 70/35 (bege crítico)", "OK"],
     ["Fu", "Tab. Philips TMS 426 + interpolação (dupla no Escritório)", "OK"],
     ["Fdl", "0,75 luminária comercial", "OK"],
     ["Nlu", "ROUNDUP + grade + X,Y ≤ 3,30 m", "OK"],
     ["Carga", "P+jQ, S, I e Eobt registrados", "OK"]],
    col_widths=(30, 110, 40), fontsize=7.5)
pdf.ln(2)
h2("14.2  Premissas e limitações (diga em voz alta na apresentação)")
for t in [
    "1. Pé-direito 3,00 m = altura de instalação (DADOS K11:K14). Se houver tirante/rebaixo, recalcular Hlp e K.",
    "2. CLARO/CLARA → 50/50 é premissa qualitativa documentada, não medição. BRANCO 80% → 70% por limite de tabela (PIE 02 p. 67).",
    "3. BEGE → 35% (pior caso da faixa 35–40%). Se adotar 45%, Fu sobe e N do Escritório deve ser revisto.",
    "4. Piso azulejo cinza registrado, mas Fu publicado só para piso 10% — limitação da tabela, declarada na col. H82:H85.",
    "5. Fdl 0,75 (comercial). Alternativa 0,70 genérica deve ser mostrada como sensibilidade.",
    "6. TMS 426 é escolha de cálculo. Trocar luminária/lâmpada/reator invalida Fu e carga — tudo deve ser refeito.",
    "7. Este PDF não dimensiona disjuntor, condutor, queda de tensão nem circuitos — isso é o T2 (PDF QDL/QDGL/QDF).",
    "8. CAD valida disposição física; quantidade da planilha é o mínimo normativo.",
]:
    bullet(t, size=8.5)
h2("14.3  Roteiro de apresentação (10 passos, 5 minutos)")
for i, t in enumerate([
    "Mostre o trecho do enunciado que exige Lumens e Hpp 0,80 m.",
    "Mostre DADOS linhas 11–14 e RESPONSABILIDADES (4 áreas do Lucas).",
    "Explique o peso soma 0 → valor médio + MAX com a específica (por que 1 500 e 750).",
    "Mostre a TMS 426: 2×40 W, 3 000 lm, 6 000 lm/ponto, reator 24,1 W FP 0,90.",
    "Mostre as refletâncias e diga o que é dado e o que é premissa (bege 35%).",
    "Calcule Hlp 2,20 m e K ao vivo para 1 sala.",
    "Abra a Tab. 2.9, mostre os 2 vizinhos de Fu e faça 1 interpolação com números.",
    "Justifique Fdl 0,75 e cite a alternativa 0,70.",
    "Calcule Φt → N → ROUNDUP → Eobt para 1 sala; mostre a tabela das 4.",
    "Feche com o total 38 / 3 955,8 W / 4 560 VA por QDL e diga que o CAD confirma a grade.",
], 1):
    p(f"{i}. {t}", size=9)
h2("14.4  Onde está cada número (rastreabilidade)")
p("LUM-LUCAS_FINAL_REVISADA.xlsx, aba LUM-LUCAS: dims B3:C6; Hlp F3:F6; peso B14:B17; E H22:J25 e E final J22:J25 e B145:B148; luminária B60:B75; refletâncias B82:H85; K E103:E106 e Fu H103:H106; Fdl B121; Φt F145:F148; Nlu E158:H161; grade G158:H161 e B167:J170; carga B179:B185 e C190:J193; QDL C197:G200; verificação A202:D211. DADOS: PROJETO INDUSTRIAIS TRABALHO.xlsx aba DADOS linhas 11–14. Responsabilidades: RESPONSABILIDADES.xlsx.", size=8.5)
h2("14.5  Referências")
for t in [
    "Dados iniciais PIE Recapadora (EEL 2026-2), 6 p. — método, Hpp, QDL5/6/7, TUG/TUE, gerador, plantas.",
    "PIE 02 — Introdução à Engenharia de Luminotécnica (Mamede, NBR 5413), p. 60–75 — peso, E, Fu, Fdl, K, disposição, reator.",
    "A1 P1 — Tabelas Auxiliares — Tab. 2.1 (3 000 lm), Tab. 2.5 (peso), Tab. 2.6 (faixas), Tab. 2.9 (Fu TMS 426), Tab. 2.10 (refletâncias), Tab. 2.14/Fig. 2.30 (Fdl), tabela de reatores (24,1 W, FP 0,90).",
    "Manual Philips TMS 426 + catálogo de reatores (fluxo, Fu, perdas).",
    "LUM-LUCAS_FINAL_REVISADA.xlsx (verdade oficial) + PROJETO INDUSTRIAIS TRABALHO.xlsx (DADOS, LUM-SP-CQ-B-E) + QD-ILUMINAÇÃO.xlsx (continuidade T2) + RESPONSABILIDADES.xlsx.",
    "NOTES.txt — pot. vetorial P+jQ; sempre usar a mais crítica (aula 27/08).",
]:
    bullet(t, size=8.5)
pdf.ln(4)
caixa("Pronto para entregar: transfira as 4 tabelas (E, K/Fu, N/Eobt, QDL) para o T1-MEMORIAL DE CALCULO.docx na ordem QDL5 → QDL6 → QDL7, anexe este PDF como memória de cálculo detalhada e leve a planilha FINAL_REVISADA aberta para mostrar as fórmulas ao professor.", bold=True, fill=(232,241,248), border=AZUL)

pdf.output(str(OUT))
print(f"OK: {OUT} ({OUT.stat().st_size/1024:.0f} kB)")
