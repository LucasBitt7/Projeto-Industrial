#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guia completo da parte do Lucas — do zero à prova. Luminotécnico + QDL/QDGL/QDF."""
from fpdf import FPDF
from fpdf.fonts import FontFace
from pathlib import Path

OUT = Path("/mnt/c/Users/lucas/Desktop/Engenharia/ProjetosIndustriais/T1_T2_LUCAS_Guia_Completo_Prova.pdf")

AZUL_D = (31, 78, 120)
AZUL = (41, 98, 150)
AZUL_BG = (232, 241, 248)
VERDE_D = (35, 110, 65)
VERDE_BG = (228, 243, 232)
AMBAR_D = (140, 95, 5)
AMBAR_BG = (255, 243, 205)
AMBAR_BD = (200, 160, 40)
ROXO_D = (85, 55, 135)
ROXO_BG = (238, 232, 248)
CINZA = (95, 95, 95)
PRETO = (28, 28, 28)

class PDF(FPDF):
    def multi_cell(self, w, h=None, text="", border=0, align="J", fill=False, **kwargs):
        kwargs.setdefault("new_x", "LMARGIN")
        kwargs.setdefault("new_y", "NEXT")
        return super().multi_cell(w, h, text, border, align, fill, **kwargs)
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 6.5)
        self.set_text_color(*CINZA)
        self.cell(0, 5, "Guia completo  |  Parte do Lucas  |  Luminotécnico + QDL/QDGL/QDF  |  Do zero à prova", align="C")
        self.ln(7)
    def footer(self):
        self.set_y(-11)
        self.set_font("DejaVu", "", 7)
        self.set_text_color(*CINZA)
        self.cell(0, 8, f"Página {self.page_no()}/{{nb}}   •   LUM-LUCAS_FINAL_REVISADA + QD-ILUMINAÇÃO", align="C")

pdf = PDF(orientation="P", unit="mm", format="A4")
pdf.alias_nb_pages("{nb}")
pdf.set_auto_page_break(True, margin=14)
pdf.set_margins(14, 14, 14)
pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
pdf.add_font("DejaVuMono", "", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")

def tabela(headers, rows, widths=None, fs=7.5):
    st = FontFace(emphasis="BOLD", color=(255,255,255), fill_color=AZUL_D)
    pdf.set_font("DejaVu", "", fs)
    with pdf.table(col_widths=widths, text_align="CENTER", line_height=5,
                   first_row_as_headings=True, headings_style=st, width=pdf.w-28) as t:
        t.row(headers)
        for r in rows:
            t.row([str(c) for c in r])

def h1(num, titulo, subt=""):
    pdf.add_page()
    # faixa superior
    pdf.set_fill_color(*AZUL_D)
    pdf.set_text_color(255,255,255)
    pdf.set_font("DejaVu", "B", 11)
    pdf.multi_cell(0, 8, f"  {num}   {titulo}", fill=True)
    if subt:
        pdf.set_font("DejaVu", "", 8.5)
        pdf.set_text_color(*CINZA)
        pdf.multi_cell(0, 5, subt)
        pdf.ln(1)
    else:
        pdf.ln(2)

def h2(t):
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(*AZUL_D)
    pdf.multi_cell(0, 6, t)
    pdf.ln(1)

def p(t, bold=False, size=9, color=PRETO):
    pdf.set_font("DejaVu", "B" if bold else "", size)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, 5, t)
    pdf.ln(1)

def bul(t, size=9):
    pdf.set_font("DejaVu", "", size)
    pdf.set_text_color(*PRETO)
    x0 = pdf.get_x()
    pdf.cell(5, 5, "•")
    pdf.multi_cell(0, 5, t)
    pdf.ln(0.5)

def box(titulo, texto, bg, bd, tc, size=8.8):
    pdf.set_fill_color(*bg)
    pdf.set_draw_color(*bd)
    pdf.set_font("DejaVu", "B", size)
    pdf.set_text_color(*tc)
    pdf.multi_cell(0, 5.2, titulo, border="LTR", fill=True)
    pdf.set_font("DejaVu", "", size)
    pdf.multi_cell(0, 5.2, texto, border="LBR", fill=True)
    pdf.ln(2)

def conceito(t): box("CONCEITO — o que é, em 1 frase", t, AZUL_BG, AZUL_D, PRETO)
def origem(t): box("ORIGEM — de onde veio (arquivo + página + célula)", t, VERDE_BG, VERDE_D, PRETO)
def porque(t): box("POR QUÊ — por que é assim e não de outro jeito", t, AMBAR_BG, AMBAR_BD, PRETO)
def prova(t): box("NA PROVA — onde achar em 30 segundos", t, ROXO_BG, ROXO_D, PRETO)
def atencao(t): box("ATENÇÃO — erro clássico que reprova", t, AMBAR_BG, (180,60,30), (120,30,10))
def formula(t):
    pdf.set_fill_color(242,242,242)
    pdf.set_draw_color(150,150,150)
    pdf.set_font("DejaVuMono", "", 8.6)
    pdf.set_text_color(20,20,20)
    pdf.multi_cell(0, 5.8, t, border=1, fill=True, align="C")
    pdf.ln(2)

# ================= CAPA =================
pdf.add_page()
pdf.ln(10)
pdf.set_font("DejaVu", "B", 10)
pdf.set_text_color(*AZUL)
pdf.multi_cell(0, 7, "RECAPADORA DE PNEUS (EEL 2026-2)  •  T1 + T2  •  PARTE DO LUCAS", align="C")
pdf.ln(2)
pdf.set_font("DejaVu", "B", 27)
pdf.set_text_color(*AZUL_D)
pdf.multi_cell(0, 11, "Do zero à prova", align="C")
pdf.set_font("DejaVu", "", 15)
pdf.multi_cell(0, 8, "Luminotécnico + Quadros QDL/QDGL/QDF", align="C")
pdf.ln(3)
pdf.set_fill_color(*AZUL_D)
pdf.set_text_color(255,255,255)
pdf.set_font("DejaVu", "B", 10)
pdf.multi_cell(0, 7, "   Sala de Produtos  •  Controle de Qualidade  •  Banheiro/Vestiário  •  Escritório   ", fill=True, align="C")
pdf.ln(4)
pdf.set_fill_color(*AZUL_BG)
pdf.set_draw_color(*AZUL_D)
pdf.set_font("DejaVu", "", 10)
pdf.set_text_color(*PRETO)
pdf.multi_cell(0, 6.2, "38 luminárias TMS 426  |  3 955,8 W  |  4 560 VA  |  QDL5 (15) + QDL6 (21) + QDL7 (2)\nCircuitos L18/L19/L20/L21  |  MDW-C10 5 kA  |  Quedas < 4%  |  Sinótico < 7%  |  Balanço R6940/S6560/T5880", border=1, fill=True, align="C")
pdf.ln(4)
pdf.set_font("DejaVu", "", 9)
pdf.set_text_color(*PRETO)
pdf.multi_cell(0, 5.2, "Você vai ler este guia sem saber nada e sair entendendo tudo o que já foi feito da sua parte: o que cada número significa, de onde ele veio (aula, página de catálogo, célula de planilha), por que foi escolhido assim, e onde abrir na hora da prova.\n\nRegra de ouro do projeto (aula 27/08, NOTES.txt): usar potência vetorial P+jQ e sempre a condição mais crítica.")
pdf.ln(2)
pdf.set_fill_color(*AMBAR_BG)
pdf.set_draw_color(*AMBAR_BD)
pdf.set_font("DejaVu", "B", 9)
pdf.set_text_color(*AMBAR_D)
pdf.multi_cell(0, 6, "Como ler: siga a ordem. Cada capítulo depende do anterior. Caixas VERDES = origem, AZUIS = conceito, AMARELAS = porquê, ROXAS = onde achar na prova. Tabelas já vêm transcritas + caminho do arquivo.", border=1, fill=True, align="C")
pdf.ln(2)
pdf.set_font("DejaVu", "", 7.5)
pdf.set_text_color(*CINZA)
pdf.multi_cell(0, 4.5, "Bases oficiais: LUM-LUCAS_FINAL_REVISADA.xlsx (aba LUM-LUCAS)  •  QD-ILUMINAÇÃO.xlsx (9 abas)  •  PROJETO INDUSTRIAIS TRABALHO.xlsx (DADOS L11-L14, LUM-SP-CQ-B-E)  •  Dados iniciais 6p  •  PIE 02/04/05/06  •  Prysmian 2010  •  WEG Minidisjuntores  •  A1 P1 Tabelas Auxiliares. Este PDF explica; a planilha prova (fórmulas abertas).", align="C")

# ================= COMO USAR =================
h1("Como usar", "Legenda + mapa em 2 minutos", "Leia esta página e o sumário. Depois vá direto ao capítulo da sua dúvida.")
tabela(["Caixa", "Cor", "Serve para"],
 [["CONCEITO", "Azul", "Entender sem jargão (o que é E, Fu, Ip, Iz')"],
  ["ORIGEM", "Verde", "Rastrear: arquivo + página + aba + célula"],
  ["POR QUÊ", "Amarela", "Justificar a escolha contra alternativas"],
  ["NA PROVA", "Roxa", "Abrir em 30 s: path + onde clicar"],
  ["FÓRMULA", "Cinza mono", "Copiar a conta com números substituídos"]], widths=(28,22,130), fs=8)
pdf.ln(2)
h2("Mapa mental da sua parte (grave isto)")
p("T1 Luminotécnico responde: QUANTAS luminárias para dar luz suficiente? → 38 (3+18+2+15). T2 Quadros responde: QUE FIO E QUE DISJUNTOR aguentam essa carga com segurança e queda aceitável? → 1,5 mm² (L20 2,5 mm²), MDW-C10, alimentadores 6/2,5/1,5 mm². Tudo gira em torno de 120 VA por ponto (TMS 426 2×40W + reator) em 220 V.", bold=True)
prova("Pasta raiz: ProjetosIndustriais/  •  Este guia: T1_T2_LUCAS_Guia_Completo_Prova.pdf  •  Irmãos: T1_LUMINOTECNICO_LUCAS_Passo_a_Passo_FINAL.pdf (14p) + QDL_QDGL_QDF_LUCAS_Passo_a_Passo.pdf (11p)  •  Scripts: tools/gerar_pdf_*.py")

# ================= SUMÁRIO =================
h1("Sumário", "O que há em cada capítulo")
for s in [
 "0. Sua parte no projeto — responsabilidades, DADOS L11-L14, QDL5/6/7 L18-L21",
 "1. O que o enunciado exige — citações literais dos Dados Iniciais (6p)",
 "2. Fundamentos de luz — grandezas, lâmpada × luminária × reator (PIE 02 p39-41)",
 "3. Lógica dos Lumens em 4 passos — Φt, N, Eobt (PIE 02 p60-75)",
 "4. Dados de entrada + índice K — S, Hlp 2,20m, K 1,24/1,24/0,95/1,56",
 "5. Iluminância E — peso soma 0 + MAX → 200/1500/200/750 (a etapa mais crítica)",
 "6. TMS 426 + reator — 6000 lm, 104,1W, 120VA (Tab 2.1/2.9 + reatores)",
 "7. Refletâncias — 50/50, 70/50, 70/35 bege crítico (Tab 2.10)",
 "8. Fu com 4 interpolações abertas número a número (Tab 2.9)",
 "9. Fdl 0,75 + fluxo Φt + Nlu 3/18/2/15",
 "10. Distribuição — grades 3×1/6×3/1×2/3×5, regra 3,30m",
 "11. Carga P+jQ + E obtida 219/1505/209/785 + folgas",
 "12. Ponte T1→T2 — de lúmens para ampères",
 "13. Passo 0 QDL — entradas e critérios (10 itens)",
 "14. Passo 1 Ip=S/220 — L18 8,18 / L19 1,64 / L20 9,82 / L21 1,09 A",
 "15. Passo 2 Ampacidade — Ip', Iz', 1,5mm² (L20 2,5), neutro = fase",
 "16. Passo 3 Disjuntores — Iz'>In>Ip, MDW-C10 5kA curva C",
 "17. Passo 4 Queda L18 2,33% — fórmula completa R/X + L+curva+subida",
 "18. Passo 4 L20 1,50% / L19 0,20% / L21 0,12%",
 "19. Passo 5 Balanço — R6940/S6560/T5880, fase max 31,5A",
 "20. Passo 6 Alimentadores 127m + sinótico 5,8%<7%",
 "21. Passo 7 QDF TUG/TUE + chuveiro 40,9A 16mm²",
 "22. Índice de prova — tabela gigante onde-achar-tudo em 30s",
 "23. Glossário + checklist + premissas + referências com páginas",
]:
    bul(s, size=8.5)

# ================= 0 =================
h1("0. Sua parte", "Sala de Produtos • CQ • Banheiro • Escritório  →  QDL5/6/7 L18-L21")
conceito("Você é dono de 4 ambientes no T1 (luz) e dos 4 circuitos que os alimentam no T2 (fio + proteção). O resto (Caldeiras, Bombas, Depósitos, Raspa, Recapagem, Subestação) é de Dante, Pietro e João.")
origem("Divisão: RESPONSABILIDADES.xlsx aba Página1  •  DADOS: PROJETO INDUSTRIAIS TRABALHO.xlsx aba DADOS linhas 11-14  •  Cálculos luz: LUM-LUCAS_FINAL_REVISADA.xlsx aba LUM-LUCAS A1:J219  •  Quadros: QD-ILUMINAÇÃO.xlsx 9 abas  •  Tudo em DESENVOLVIMENTO/PROJETOS INDUTRIAIS SICA/T1/")
tabela(["Seu ambiente", "DADOS", "LUM-LUCAS", "Circuito", "QDL"],
 [["Sala de Produtos 5×6", "L11", "L3/R22/R82/R103", "L19 3 lum 360VA", "QDL6"],
  ["Controle Qualidade 5×6", "L12", "L4/R23/R83/R104", "L20 18 lum 2160VA", "QDL6"],
  ["Banheiro 5,23×3,5", "L13", "L5/R24/R84/R105", "L21 2 lum 240VA", "QDL7"],
  ["Escritório 8,12×6", "L14", "L6/R25/R85/R106", "L18 15 lum 1800VA", "QDL5"]], widths=(42,18,42,42,36), fs=7.5)
pdf.ln(2)
porque("Sala de Produtos e CQ dividem o QDL6 mas têm circuitos separados (L19 e L20): são salas físicas distintas, com E diferentes (200 vs 1500) e comando independente. Juntar num circuito só estouraria 4500VA? Não (2520VA caberia), mas perderia seletividade de comando — critério do time: 1 sala = 1 circuito.")
prova("Abra: QD-ILUMINAÇÃO.xlsx → abas QDL (R21-R24) / QDGL (R22-R25) / QDF-TOMADAS-LUCAS (R3-R6). Luz: LUM-LUCAS_FINAL_REVISADA.xlsx → coluna A diz o ambiente, resto é fórmula.")

# ================= 1 =================
h1("1. Enunciado", "O que o projeto exige — sem inventar nada")
p("Tudo abaixo é transcrição dos Dados Iniciais (6 páginas). Se o professor perguntar 'por que Lumens?', aponte aqui.")
box("CITAÇÃO 1 — método", "“Para Sala de Caldeiras, Compressor, Depósito, Raspa → método de Lumens. Para Recapagem → Cavidades.” (p5/6). Suas 4 áreas usam Lumens por extensão da mesma regra + memorial do grupo.", AZUL_BG, AZUL_D, PRETO)
box("CITAÇÃO 2 — altura", "“Altura de manuseio 0,80 m.” (p5/6) → Hpp = 0,80 em todas. Com pé-direito 3,00 (DADOS K11:K14) → Hlp = 2,20 m.", AZUL_BG, AZUL_D, PRETO)
box("CITAÇÃO 3 — lâmpada/piso", "“Poderá usar vapor de sódio ou similares (produção alta).” + “Piso concreto (produção) / azulejo cinza (suas áreas).” → fluorescente TMS 426 é o 'similar' permitido para interiores baixos de 3m.", AZUL_BG, AZUL_D, PRETO)
box("CITAÇÃO 4 — quadros e elétrica", "“QDL5 Escritório; QDL6 Sala Produto+CQ; QDL7 Banheiros” (p2/6) • “BT 380/220V 60Hz, 1200m, 45°C” (p1) • “5kA QDL/QDF, 7kA CCM” (p3) • “Queda trecho-a-trecho formulação completa com V/A.km Prysmian” (p6) • “TUG/TUE NBR 5410 + climatizadores SP/CQ/Esc + chuveiro 9kW” (p6) • “Ampacidade pelo catálogo Prysmian” (p6).", VERDE_BG, VERDE_D, PRETO)
porque("Altitude 1200m não corrige ampacidade em BT (só motores); 45°C sim (fator 0,79 PVC). 5kA define Icu do MDW. 127m dos alimentadores é estimativa do time — medir no DWG.")
prova("Dados Iniciais: 05 - Projeto Industrial.../01 - Dados Iniciais/PIE Industria RECAPADORA (EEL_2026-2)....pdf. Plantas: .../02 - Plantas e DWG/*.dwg. Plano ensino T1-T4: 00 - Disciplina e Plano de Ensino/PIE - Plano de Ensino (03AGO).pdf.")

# ================= 2 =================
h1("2. Fundamentos de luz", "PIE 02 p39-41 — entenda em 5 minutos")
conceito("Fluxo Φ (lm) = luz total que sai. Iluminância E (lux = lm/m²) = luz que chega por m². Refletância ρ (%) = quanto teto/parede devolve. Fu = fração que atinge o plano útil. Fdl = desconto sujeira/idade. K = proporção área×altura (diz a linha da tabela).")
tabela(["Grandeza", "Símb", "Unidade", "Analogia simples"],
 [["Fluxo", "Φ", "lm", "Litros que saem da torneira"],
  ["Iluminância", "E", "lux", "Água que chega por m² do balde"],
  ["Área", "S", "m²", "Tamanho do balde (L×C)"],
  ["Fu", "Fu", "0-1", "Quanto espirra fora (parede escura = perde mais)"],
  ["Fdl", "Fdl", "0-1", "Torneira suja com o tempo"],
  ["K", "K", "-", "Balde largo e baixo × estreito e alto"]], widths=(30,14,26,110), fs=8)
pdf.ln(2)
p("Lâmpada = o tubo (40W, 3000lm). Luminária = conjunto (carcaça TMS 426 + 2 tubos + reator). Reator = limitador de corrente que dissipa 24,1W em calor e atrasa a corrente (FP 0,90 → existe Q). Por isso 1 ponto = 104,1W + j50,42var, não só 80W.", bold=True)
origem("Aula: 01 - Aulas e Slides/01 - Slides 01 a 03/PIE 02 - Introducao a Engenharia de Luminotecnica.pdf p39-41 grandezas, p63 reator/lâmpada, p75 reator RVM/FP. Tabelas: 02 - Luminotecnica/A1 P1 - Tabelas Auxiliares....pdf (Tab 2.1 3000lm).")
prova("Esqueceu um símbolo? Volte a esta página. Na prova, E, Φ, Fu, Fdl e K caem no enunciado — sublinhe cada um com a unidade.")

# ================= 3 =================
h1("3. Lógica dos Lumens", "PIE 02 p60-75 — 4 passos que geram todos os números")
p("1) Alvo E × área = fluxo útil que precisa chegar. 2) Divide por Fu×Fdl (perdas) = fluxo que as lâmpadas devem emitir. 3) Divide por 6000 (1 lum) = quantidade teórica → teto. 4) Recalcula E com N instalado (tem que dar ≥ alvo).", bold=True)
formula("Passo 1  Φútil = E × S\nPasso 2  Φt = E × S / (Fu × Fdl)\nPasso 3  Nteo = Φt / (2 × 3000)  →  N = teto(Nteo)\nPasso 4  Eobt = N × 6000 × Fu × Fdl / S   (exigido Eobt ≥ E)\nExtras  Hlp = 3,00 − 0,80 = 2,20 m  |  K = L×C / [Hlp×(L+C)]  |  1 lum = 104,1W + j50,42var = 115,67VA → 120VA")
porque("Arredonda SEMPRE para cima: 2 lum dariam 146 lux < 200 na Sala de Produtos → reprovado. Fdl no denominador: menor Fdl = mais lum exigido = a favor da segurança.")
origem("PIE 02 p60-62 (E), p64-68 (Fu/K), p67 interpolação, p69-70 (Fdl), p73 (Φt/N), p74 (X,Y≤1,5Hlp), p75 (reator). Mamede Tab 2.4/2.5/2.6/2.9/2.10 citadas nos slides.")
atencao("Não confunda Φt (o que precisa emitir) com Φútil (o que precisa chegar). Nem Nteo (2,73) com N (3). A banca adora trocar.")

# ================= 4 =================
h1("4. Dados + índice K", "DADOS L11-L14 — nada é inventado")
tabela(["Ambiente", "L×C [m]", "S [m²]", "Hlp [m]", "K (conta)", "Interpretação"],
 [["Sala Produtos", "5,00×6,00", "30,000", "2,20", "1,2397 =30/24,20", "Média"],
  ["CQ", "5,00×6,00", "30,000", "2,20", "1,2397", "Igual (mesma caixa)"],
  ["Banheiro", "5,23×3,50", "18,305", "2,20", "0,9531 =18,3/19,2", "Mais 'alto' → Fu menor"],
  ["Escritório", "8,12×6,00", "48,720", "2,20", "1,5684 =48,7/31,06", "Mais 'baixo' → Fu maior"]], widths=(32,28,22,18,42,38), fs=7.5)
pdf.ln(2)
conceito("K mede se a sala é compacta e baixa (K grande, luz reaproveita, Fu alto) ou esguia e alta (K pequeno, luz bate na parede, Fu baixo). Mesma área ≠ mesmo K se altura difere; mesma área + mesma altura = mesmo K (SP e CQ).")
origem("Dimensões e Htp 3,00: PROJETO INDUSTRIAIS TRABALHO.xlsx DADOS L11-L14 col D/E/K. Hpp 0,80: Dados Iniciais p5/6. Hlp =E-D (LUM-LUCAS F3:F6). S =B×C. K =(B×C)/(D×(B+C)) (E103:E106). PIE 02 p65.")
prova("DADOS: .../T1/PROJETO INDUSTRIAIS TRABALHO.xlsx aba DADOS. K: LUM-LUCAS col E103:E106. Se mudar dimensão, K e tudo recalcula.")

# ================= 5 =================
h1("5. Iluminância E", "A etapa mais crítica — por que 1500 e 750 e não 500/250")
p("E vem da ATIVIDADE, não da metragem. Duas tabelas: (a) faixa por ambiente + peso (idade/precisão/fundo) e (b) valor específico. Vale o MAIOR (mais crítica, aula 27/08, =MAX na planilha).", bold=True)
tabela(["Critério de peso (Tab 2.5)", "Adotado", "Peso"],
 [["Idade", "41 anos (40-55)", "0"],
  ["Velocidade/precisão", "Importante", "0"],
  ["Refletância fundo", "0,40 (30-70%)", "0"],
  ["SOMA → usa valor MÉDIO da faixa", "—", "0"]], widths=(70,60,50), fs=8)
pdf.ln(1)
tabela(["Ambiente", "Faixa (médio)", "Específica", "ADOTADA = MAX"],
 [["Sala Produtos A depósito", "100-150-200 → 150", "200 grandes vol.", "200"],
  ["CQ B inspeção", "1000-1500-2000 → 1500", "500 (genérico)", "1500"],
  ["Banheiro A curta", "50-75-100 → 75", "200 banheiros", "200"],
  ["Escritório B", "500-750-1000 → 750", "250 (genérico)", "750"]], widths=(50,50,40,40), fs=8)
pdf.ln(2)
porque("Usar 500 no CQ e 250 no Esc (só coluna específica) subdimensiona 3× — erro de versões antigas, corrigido na FINAL_REVISADA. Faixa já pondera o peso; específica é mínimo genérico. MAX protege.")
origem("PIE 02 p60-62 + A1 P1 Tab 2.5/2.6. Planilha LUM-LUCAS R13-R17 (peso), R20-R25 (faixas), R29-R32 nomes, J22:J25 =MAX, B145:B148 E final.")
atencao("Na prova, some os 3 pesos: -2 ou menos = inferior, +2 ou mais = superior, -1 a +1 = médio. Aqui soma 0 → médio. Depois faça MAX com a específica.")
prova("E: LUM-LUCAS H22:J25 e B145:B148. Nomes Tab 2.6: linhas 29-32. Leve Tab 2.5/2.6 impressa.")

# ================= 6 =================
h1("6. Luminária e reator", "TMS 426 2×40W — por que ela")
conceito("TMS 426 = carcaça Philips para 2 fluorescentes de 40W. Cada tubo 3000 lm → 6000 lm/ponto. Reator duplo 220V perde 24,1W e tem FP 0,90 (indutivo → gera Q).")
tabela(["Item", "Valor", "Onde está"],
 [["Luminária", "TMS 426 2×40W Philips", "Tab 2.9 / PIE02 p63"],
  ["Tubo", "Fluor comum 40W 3000 lm", "Tab 2.1"],
  ["Por ponto", "6000 lm", "2×3000"],
  ["Reator", "Duplo 220V 24,1W FP0,90 cat 0,51A", "Tab reatores / p75"],
  ["1 lum", "104,1W + j50,42 =115,67VA →120VA", "B179:B185"]], widths=(36,62,82), fs=8)
pdf.ln(2)
formula("P = 2×40+24,1 = 104,1 W\nQ = 104,1×tan(arccos 0,90) = 104,1×0,4843 = 50,42 var\nS = √(104,1²+50,42²) = 115,67 VA → adot 120 VA/ponto\nI = 115,67/220 = 0,53A (adot 0,55A; cat 0,51A = arredondamento)")
porque("TMS 426 não é única (TMS 500/TCK/HDK existem), mas é a única com Fu + elétrico juntos na tabela → rastreável. LED exigiria trocar Fu e dados por datasheet. 120VA (não 115,67) dá número inteiro por circuito e margem.")
origem("LUM-LUCAS B60:B75 + B179:B185. Catálogos Dra. sala: T1/LAMPADAS/PHILIPS 400W...pdf e T1/REATORES/BHL...pdf (exemplo Dante; o seu é fluor 40W).")
prova("1 lum = 104,1/50,42/120VA/0,55A. Guarde: tudo multiplica por N (3/18/2/15).")

# ================= 7 =================
h1("7. Refletâncias", "O que é dado × premissa — bege 35%")
conceito("ρ = % da luz que teto/parede devolve. Claro devolve mais → Fu maior → menos lum. Tab 2.9 só tem teto 70/50/30, parede 50/30/10, piso 10%.")
tabela(["Amb", "DADO", "Adotado", "Critério"],
 [["SP", "CLARO/CLARA", "50/50", "Qualitativo → coluna clara"],
  ["CQ", "BRANCO/BRANCA", "70/50", "Branco-neve 80% → limite 70% (p67)"],
  ["Banh", "CLARO/CLARA", "50/50", "Igual SP"],
  ["Esc", "BRANCO/BEGE", "70/35", "Bege 35-40% → 35% crítico, interpola colunas"]], widths=(24,44,26,86), fs=8)
pdf.ln(2)
porque("CLARO não é número → 50% é premissa declarada. BRANCO 80% não existe na tabela → usa 70% (regra PIE02 p67: acima do limite, usa a mais próxima). BEGE 35% é pior caso; se usar 45%, Fu sobe ~0,60 e Esc pode cair 15→14 — recalcular.")
origem("Tab reflet (branco-neve 80, marfim 70, bege 45...). LUM-LUCAS B82:H85 (piso 10% fixo, azulejo cinza registrado mas sem coluna). DADOS H/I colunas.")
prova("Reflet: LUM-LUCAS R82-R85. Leve Tab 2.10 + Tab 2.9. Diga em voz alta o que é dado e o que é premissa.")

# ================= 8 =================
h1("8. Fator Fu", "4 interpolações abertas (PIE 02 p67)")
p("Fu = fração que chega ao plano. Lê na Tab 2.9 pela linha K e coluna reflet. K entre linhas → interpola. Parede entre colunas (bege) → interpola de novo.", bold=True)
formula("Fu = Fu_inf + (K−Kinf)/(Ksup−Kinf)×(Fusup−Fuinf)\nEsc: Fu35% = Fu30% + (35−30)/(50−30)×[Fu50%−Fu30%]")
tabela(["Amb", "Vizinhos Tab 2.9", "Conta", "Fu"],
 [["SP 50/50 K1,2397", "1,00→0,44 / 1,25→0,49", "0,44+0,9588×0,05", "0,4879"],
  ["CQ 70/50 K1,2397", "1,00→0,50 / 1,25→0,56", "0,50+0,9588×0,06", "0,5575"],
  ["Banh 50/50 K0,9531", "0,80→0,38 / 1,00→0,44", "0,38+0,7654×0,06", "0,4259"],
  ["Esc dupla K1,5684", "1,5→0,54/0,61 2,0→0,61/0,68", "0,5496/0,6196→0,5671", "0,5671"]], widths=(38,52,52,28), fs=7.5)
pdf.ln(2)
p("Esc aberta: Fu30% =0,54+(0,0684/0,50)×0,07 =0,5496; Fu50% =0,61+idem =0,6196; Fu35% =0,5496+0,25×0,07 =0,5671.", bold=True)
origem("LUM-LUCAS H103:H106 + E103:E106. Tab 2.9 bloco TMS 426 piso 10%. PIE 02 p64-68.")
atencao("Nunca chute Fu visual. Mostre os 2 vizinhos e a conta. Parede 10% é ambiente escuro — trocar de coluna sem motivo derruba Fu.")
prova("Fu: LUM-LUCAS col H. Leve Tab 2.9 + régua para K.")

# ================= 9 =================
h1("9. Fdl + fluxo + Nlu", "Fdl 0,75 → Φt → 3/18/2/15")
conceito("Fdl desconta sujeira/idade. No denominador: menor Fdl = mais fluxo. Comercial = 0,75 (específico prevalece sobre genérico 0,70).")
origem("Fdl: Tabelas Aux quadro Fdl + Mamede Tab 2.9; PIE 02 p69 (0,7 sem dado) p70 (com dado, na dúvida menor). LUM-LUCAS B119:B121 =0,75.")
formula("Φt = E×S/(Fu×Fdl)  |  Nteo = Φt/6000  |  N = teto(Nteo)")
tabela(["Amb", "E×S", "Fu×Fdl", "Φt [lm]", "Nteo → N (grade)"],
 [["SP", "200×30=6000", "0,4879×0,75", "16 395,66", "2,7326 → 3 (3×1)"],
  ["CQ", "1500×30=45000", "0,5575×0,75", "107 619,33", "17,9366 → 18 (6×3)"],
  ["Banh", "200×18,305=3661", "0,4259×0,75", "11 460,51", "1,9101 → 2 (1×2)"],
  ["Esc", "750×48,72=36540", "0,5671×0,75", "85 914,94", "14,3192 → 15 (3×5)"]], widths=(24,38,32,34,52), fs=7.5)
pdf.ln(2)
porque("ROUNDUP (F158:F161): 2 lum na SP dariam 146 lux <200. Fdl 0,70 (+7,1% fluxo) afetaria o CQ primeiro (folga 0,4%).")
prova("Φt: F145:F148. N: E158:H161. Fdl: B121 editável — mostre cenário 0,70 na prova.")

# ================= 10 =================
h1("10. Distribuição", "Grade + regra 1,5×Hlp = 3,30m (PIE 02 p74)")
formula("X,Y ≤ 1,5×Hlp = 3,30 m  |  X1 = X/2, Y1 = Y/2 (bordas)")
tabela(["Amb (L×C)", "Grade", "X/X1", "Y/Y1", "OK?"],
 [["SP 5×6", "3×1=3", "2,00/1,00", "—/2,50", "CERTO"],
  ["CQ 5×6", "6×3=18", "1,00/0,50", "1,67/0,83", "CERTO"],
  ["Banh 5,23×3,5", "1×2=2", "—/1,75", "2,62/1,31", "CERTO"],
  ["Esc 8,12×6", "3×5=15", "2,00/1,00", "1,62/0,81", "CERTO"]], widths=(34,26,32,32,26), fs=8)
pdf.ln(2)
p("Leitura: SP 3×1 = 3 colunas nos 6m (X=6/3=2,00) × 1 fileira nos 5m (Y1=2,50). CQ 6×3: X=1,00 Y=1,67. Banh 1×2: X1=1,75 Y=2,615. Esc 3×5: X=2,00 Y=1,624. Tudo ≤3,30 (J167:J170).", bold=True)
porque("Planilha dá o MÍNIMO normativo; CAD pode exigir +1 por porta/pilar/climatizador — aí recalcula Eobt. Quantidade nunca pode ser menor.")
origem("LUM-LUCAS B167:J170 + G158:H161. DWG: .../02 - Plantas e DWG/*.dwg e .../T1/*CERTO.dwg.")
prova("Grade: LUM-LUCAS linhas 167-170 col J = CERTO. Leve régua + planta.")

# ================= 11 =================
h1("11. Carga e E obtida", "P+jQ (NOTES.txt) + verificação Eobt ≥ E")
formula("P = N×104,1  |  Q = N×50,42  |  S_ex = √(P²+Q²)  |  S_ad = N×120  |  I = S/220  |  Eobt = N×6000×Fu×Fdl/S")
tabela(["Amb", "N", "P [W]", "Q [var]", "S ad [VA]", "I [A]", "Eobt ≥ E"],
 [["SP", "3", "312,3", "151,25", "360", "1,64", "219,6 ≥200 OK"],
  ["CQ", "18", "1873,8", "907,52", "2160", "9,82", "1505,3 ≥1500 OK"],
  ["Banh", "2", "208,2", "100,84", "240", "1,09", "209,4 ≥200 OK"],
  ["Esc", "15", "1561,5", "756,27", "1800", "8,18", "785,7 ≥750 OK"]], widths=(24,14,26,26,28,24,38), fs=7.5)
pdf.ln(2)
p("Ex.: SP Eobt =3×6000×0,4879×0,75/30 =219,57 (+19,6/+9,8%). Folgas: SP +9,8%, CQ +0,4% (ponto de atenção!), Banh +4,7%, Esc +4,8%. CQ 17,94→18 dá só +0,35% real — qualquer revisão mexe nele.", bold=True)
origem("LUM-LUCAS B179:B185 (1 lum), C190:J193 (ambientes), C197:G200 (QDL). Tensão 220: B72. Corrente ainda é referência — dimensiona no T2.")
prova("Carga: LUM-LUCAS R190-R200. Total Lucas: 38 / 3955,8W / 1915,9var / 4560VA.")
tabela(["QDL", "Ambientes", "Lum", "P [W]", "S [VA]", "I [A]"],
 [["QDL5", "Escritório", "15", "1561,5", "1800", "8,18"],
  ["QDL6", "SP+CQ", "21 (3+18)", "2186,1", "2520", "11,45"],
  ["QDL7", "Banheiro", "2", "208,2", "240", "1,09"],
  ["TOTAL", "4 amb", "38", "3955,8", "4560", "20,73*"]], widths=(24,36,26,28,28,28), fs=8)
pdf.ln(1)
p("*20,73 = soma referências. Por fase vem no Passo 5.", size=8)

# ================= 12 =================
h1("12. Ponte T1→T2", "De lúmens para ampères — o mapa")
p("T1 respondeu QUANTOS pontos. T2 responde QUE FIO + DISJUNTOR + QUEDA. A ponte é 120VA/ponto em 220V. A sequência da planilha QD-ILUMINAÇÃO é sempre: Ip → Ip' (fatores) → seção (Iz') → neutro/terra → In (Iz'>In>Ip) → queda trecho-a-trecho → balanço → alimentador → QDGL → QDF.", bold=True)
conceito("Ip = corrente que vai passar. Iz = quanto o fio aguenta na tabela (30°C). Iz' = Iz com calor real (45°C) e agrupamento. Ip' = Ip corrigida para comparar. In = disjuntor comercial. ΔV = queda ao longo do fio.")
origem("Aulas: PIE 04 (ampacidade), PIE 05 (neutro/queda), PIE 06 (proteção). Catálogo obrigatório: Prysmian 2010. WEG MDW para In/Icu.")
prova("Sequência = ordem das abas: QDL → QDL-FATOR → SEÇÃO → DISJUNTORES → QDL-QUEDA → BALANÇOS → QDGL → QDF-TOMADAS-LUCAS.")

# ================= 13 =================
h1("13. Passo 0 — entradas QDL", "10 itens, nenhum inventado")
tabela(["Item", "Adotado", "Fonte (prova)"],
 [["Tensão", "380/220V 60Hz", "Dados Iniciais p1"],
  ["Temp", "45°C → f 0,79 PVC", "Dados + Prysmian Tab6 pdfp57 / PIE04 p52"],
  ["Altitude", "1200m sem correção BT", "Dados p1"],
  ["Curto", "5kA QDL/QDF", "Dados p3 (J48: não é 2kA)"],
  ["Ponto", "120VA FP0,90", "T1 LUM-SP-CQ-B-E"],
  ["Qtd", "15/3/18/2", "T1 Nlu"],
  ["Método", "7 embutido → B1", "Planilha M3 / PIE04 p58"],
  ["Isolação", "PVC comuns", "Planilha Q71"],
  ["Harmônico", "×1,15 descarga", "PIE04 fatores"],
  ["ΔV lim", "4% term / 7% total", "PIE05 p14-19"]], widths=(28,52,100), fs=7.5)
pdf.ln(2)
porque("Método 7 (eletroduto embutido, pé-direito 3m) → referência B1 unipolar. PVC (não EPR) nas suas salas → f 0,79 (EPR seria 0,87). Harmônico 1,15 porque fluorescente deforma corrente. 127m alimentador é estimativa — medir no DWG.")

# ================= 14 =================
h1("14. Passo 1 — Ip", "QDL R21-R24: Ip = S/220")
formula("Ip = Demanda / Vfn = N×120 / 220")
tabela(["Circ", "Área", "N", "Demanda [VA]", "Ip [A]", "Fase (P5)"],
 [["L18 QDL5", "Escritório", "15", "1800", "8,18", "R"],
  ["L19 QDL6", "Sala Produtos", "3", "360", "1,64", "T"],
  ["L20 QDL6", "CQ", "18", "2160", "9,82", "S"],
  ["L21 QDL7", "Banheiro", "2", "240", "1,09", "T"]], widths=(28,40,18,32,28,34), fs=8)
pdf.ln(2)
porque("1 sala = 1 circuito (comando independente). Limite time 4500VA: todos passam folgados. Fase só define no Passo 5; CQ (maior) vai na fase mais vazia S.")
origem("QD-ILUMINAÇÃO aba QDL R21-R24 col G/H/I/J (=H×G, =I/D). PIE 03 demanda.")
prova("Ip: QDL col J. S: col I. N: col G.")

# ================= 15 =================
h1("15. Passo 2 — Ampacidade", "Ip' → seção (Prysmian Tab B1)")
formula("Ip' = Ip×1,15 / (0,79×1,00)  |  Iz' = Iz×0,79×1,00  |  Exigido Iz' ≥ Ip'\nB1 PVC 2CC: 1,5mm²→17,5A / 2,5mm²→24A (Prysmian pdfp53)")
tabela(["Circ", "Ip", "Ip'", "Iz' 1,5", "Seção"],
 [["L18", "8,18", "11,91", "13,83", "1,5 (16%)"],
  ["L19", "1,64", "2,38", "13,83", "1,5"],
  ["L20", "9,82", "14,29", "13,83<14,29!", "2,5 →18,96 (33%)"],
  ["L21", "1,09", "1,59", "13,83", "1,5"]], widths=(24,28,28,36,64), fs=8)
pdf.ln(2)
p("Neutro = fase (descarga com 3º harmônico, NBR 5410 6.2.5 / PIE 05 p39-45). PE = fase até 16mm². Carregados: 2 (F+N).", bold=True)
atencao("Colegas anotaram EPR nos QDL0-4 mas usaram Iz 22A (valor PVC; EPR daria 27A). Nas suas linhas use PVC consistente (0,79 + Tab PVC).")
origem("QDL-FATOR R21-R24 (I/J/K/L/O/P) + SEÇÃO R21-R24 (J/K/L). Prysmian Tab6 pdfp57 (0,79), Tab7-10 fagrup, Tab2 pdfp53 (17,5/24A). PIE 04 p48-67.")
prova("Ip': QDL-FATOR col N. Iz': col P. Seção: SEÇÃO col J/K/L.")

# ================= 16 =================
h1("16. Passo 3 — Disjuntores", "Iz' > In > Ip, MDW-C10 5kA curva C")
formula("Iz' > In > Ip  |  Icu ≥ 5kA (QDL)  |  Curva C = partida de reator")
tabela(["Circ", "Iz'", "In", "Ip", "WEG", "Check"],
 [["L18", "13,83", "10", "8,18", "MDW-C10 1P+N 5kA", "OK"],
  ["L19", "13,83", "10", "1,64", "MDW-C10", "OK"],
  ["L20", "18,96", "10", "9,82", "MDW-C10", "OK"],
  ["L21", "13,83", "10", "1,09", "MDW-C10", "OK"]], widths=(22,24,20,24,48,42), fs=8)
pdf.ln(2)
porque("In comercial 10A (IEC 60898). Curva C (5-10×In) segura inrush do reator; B desarmaria à toa, D só p/ motor. Icu 5kA = curto presumido QDL (Dados p3).")
origem("DISJUNTORES R21-R24 (D/E/F/G). WEG Minidisjuntores p3 (curvas), p5 (MDW 5kA 127/220, In 2-125A). PIE 06 p27-41.")
prova("In: DISJUNTORES col E. Icu: WEG p5 + Dados p3.")

# ================= 17 =================
h1("17. Passo 4 — Queda L18", "Fórmula completa, trecho a trecho")
conceito("Fio tem resistência R e reatância X. Corrente × (R+X) × comprimento = queda. Soma por trecho (jusante diminui) = acumulado <4%.")
formula("ΔV = 2×Ip×L×(R×cosφ + X×senφ), cosφ=0,90 senφ=0,4359\nΔV% = ΔV/220×100  |  L = comp + 1,5m/curva + subida (3,0−1,5)\n1,5mm²: R=14,8137 X=0,1378 mΩ/m | 2,5mm²: R=8,8882 X=0,1345")
p("L18 Escritório (1,5mm², 15 pontos, grade 3×5): QDL5-LU1 (15 lum, L 3,0+2 curvas+subida) → LU1-LU2 (14)... até LU14-LU15* (1). Cada trecho usa Ip dos pontos a jusante (k×120/220). Acumulado final 2,33% <4% OK. Rotas pela grade do memorial — ajustar no DWG.", bold=True)
origem("QD-QUEDA R392-R408 (15 trechos L18). R/X: Prysmian impedância sequência positiva + PIE 05 p24-28. +1,5m/curva (<10mm²) e subida I45: nota R448. Limite 4%: PIE 05 p14-19.")
prova("Queda: QD-QUEDA col H/I/J. R/X no cabeçalho do bloco + Prysmian pdfp61-62.")
tabela(["Trecho tipo", "k lum", "L total", "Ip [A]", "ΔV% trecho", "Acum"],
 [["QDL5-LU1 (chegada)", "15", "7,50", "8,18", "~0,55", "~0,55"],
  ["Meio (ex. LU5-LU6)", "10", "3,50", "5,45", "~0,18", "~1,2"],
  ["Fim LU14-LU15*", "1", "1,62", "0,55", "~0,01", "2,33 OK"]], widths=(48,20,28,24,30,30), fs=8)
pdf.ln(1)
p("Valores ilustrativos do perfil; os centésimos exatos estão na planilha (col I/J) e no PDF irmão p6 (tabela de 15 linhas). O método é o que cai: 2×Ip×L×(Rcos+Xsen).", size=8)

# ================= 18 =================
h1("18. Passo 4 — L20/L19/L21", "Todos <4%")
tabela(["Circ", "Seção", "Trechos", "Acumulado", "Status"],
 [["L20 CQ", "2,5mm²", "18 (QDL6-LU1...LU17-LU18*)", "1,50%", "OK folgado"],
  ["L19 SP", "1,5mm²", "3 (QDL6-LU1/LU1-LU2/LU2-LU3*)", "0,20%", "OK"],
  ["L21 Banh", "1,5mm²", "2 (QDL7-LU1/LU1-LU2*)", "0,12%", "OK"]], widths=(26,26,62,30,36), fs=8)
pdf.ln(2)
porque("L20 precisou 2,5mm² na ampacidade e isso ainda ajudou na queda (R menor). L19/L21 curtos → queda desprezível. Se a rota real no DWG for maior, recalcular só L (fórmula igual).")
origem("QD-QUEDA R412-R416 (L19), R420-R439 (L20), R443-R446 (L21). PDF irmão p7.")
prova("Totais: QD-QUEDA col J última linha de cada bloco.")

# ================= 19 =================
h1("19. Passo 5 — Balanço", "R6940 / S6560 / T5880")
p("QDGL entrega R+S+T+N. Time deixou R5140/S4400/T5280 (14820VA). Você distribui para achatar: CQ 2160 (maior) na fase mais vazia S, Escritório 1800 na R, SP 360 + Banh 240 na T.", bold=True)
tabela(["Item", "R [VA]", "S [VA]", "T [VA]", "Total", "Fase"],
 [["Antes QDL0-4", "5140", "4400", "5280", "14820", "—"],
  ["+L18 Esc", "+1800", "—", "—", "", "R"],
  ["+L20 CQ", "—", "+2160", "—", "", "S"],
  ["+L19 SP", "—", "—", "+360", "", "T"],
  ["+L21 Banh", "—", "—", "+240", "", "T"],
  ["QDGL", "6940", "6560", "5880", "19380", "R 31,5A"]], widths=(32,28,28,28,28,36), fs=8)
pdf.ln(2)
formula("Fase max = MAX(6940,6560,5880)/220 = 6940/220 = 31,55 A  →  base do QDGL (Passo 6)")
porque("Desequilíbrio inevitável em mono; objetivo é minimizar o max (que dimensiona o geral). Correção na planilha: FASE MAX =MAX(E28:G28)/220 (antes só T/220).")
origem("QDL-BALANÇO TOTAL R23-R31 + R33 nota Lucas. QDL-BALANÇO POTENCIAS R281-R295. PIE 03.")
prova("Balanço: QDL-BALANÇO TOTAL. Fase max alimenta QDGL R130.")

# ================= 20 =================
h1("20. Passo 6 — Alimentadores", "127m + sinótico 5,8% <7%")
conceito("Alimentador = fio QDGL→QDL e QDGBT→QDGL. Longo (127m ala administrativa) → queda manda mais que ampacidade. Bandeja perfurada método 13/ref F unipolar, EPR f 0,87, agrup 8 cabos f 0,72 (Tab 9.10 ref 4).")
formula("Ip' = Ip×1,15/(0,87×0,72)\nQDL5 8,18→15,0A | QDL6 2520/380=6,63→12,2A | QDL7 1,09→2,0A")
tabela(["Alimentador", "Sistema", "Ip", "L", "Seção (ΔV manda)", "ΔV", "Disjuntor"],
 [["QDGL-QDL5", "220 R", "8,18", "127", "6mm² (1,5 daria 12,7%!)", "3,20%", "MDWH-C10 5kA"],
  ["QDGL-QDL6", "380 S+T", "6,63", "127", "2,5mm² (1,5 daria 7%!)", "3,57%", "MDWH-C10/2"],
  ["QDGL-QDL7", "220 T", "1,09", "127", "1,5mm² atende", "1,69%", "MDWH-C10"],
  ["QDGBT-QDGL", "380+N", "31,55", "10", "10mm² (ampacidade)", "0,59%", "MDWH-C40 3P"]], widths=(32,24,18,18,44,20,34), fs=7)
pdf.ln(2)
p("QGDL: Ip 31,55 → Ip' 41,7A; Iz' 74×0,87=64,4A (10mm² EPR F 3 cabos); 31,5<40≤64,4 OK. Sinótico trafo→lum: 0,6% + ~3,2% + ~2% ≈5,8% <7% OK.", bold=True)
origem("QDGL R22-R25, R60-R64 (127m AJUSTAR DWG), R126-R134. R/X seq positiva Prysmian. PIE 05 p30 + PIE 04 p58-60.")
atencao("127m é estimativa da equipe. Na prova, se L mudar, ΔV escala linear: dobre L = dobre %. Seção por queda usa V/A.km (Prysmian pdfp61).")
prova("Alimentadores: QDGL R60-R64. Geral: R127-R134.")

# ================= 21 =================
h1("21. Passo 7 — QDF", "TUG/TUE NBR 5410 Tab 9 (Prysmian pdfp48)")
tabela(["Área", "Regra", "TUG", "P TUG", "TUE", "QDF"],
 [["Esc 48,72m²", ">40: 10+1/10m²", "11", "2200", "1 climatizador", "QDF5"],
  ["CQ 30m²", "≤40: max(per/3,área/4)=8", "8", "1600", "1 climatizador", "QDF6"],
  ["SP 30m²", "idem", "8", "1600", "1 climatizador", "QDF6"],
  ["Banh 18,3m²", "1 pia 600VA", "1", "600", "2×chuveiro 9kW+DDR", "QDF7"]], widths=(28,44,18,20,42,28), fs=7.5)
pdf.ln(2)
formula("Chuveiro 9000/220 = 40,91 A\n10mm² PVC B1 Iz'=57×0,79=45,0 <50 → 16mm² Iz'=76×0,79=60,0A\nIn 50A: 40,9<50≤60 OK (ΔV ~0,8% em 15m)")
p("TUG: 2,5mm² MDW-C10 (4-6 tomadas/circ, FP~1 sem harmônico). Gerais: QDF5 C25 / QDF6 C32 / QDF7 C100 (se 1 chuveiro, cai ~50A — confirmar nº).", bold=True)
origem("QDF-TOMADAS-LUCAS A1:I25 (R3-R6 previsão, R10-R17 circuitos, R21-R23 gerais, R25 pendências). Prysmian Tab9 + PIE 05.")
prova("QDF: aba QDF-TOMADAS-LUCAS inteira cabe numa tela. Chuveiro: R16-R17.")

# ================= 22 =================
h1("22. Índice de prova", "Onde achar tudo em 30 segundos")
p("Fotografe esta página. Na prova, ache a informação na coluna 1 e abra o caminho na coluna 2.", bold=True)
tabela(["Preciso de...", "Abra (path curto → aba/página → célula)"],
 [["E 200/1500/200/750", "LUM-LUCAS → H22:J25, B145:B148"],
  ["TMS 6000lm 104W 120VA", "LUM-LUCAS → B60:B75, B179:B185"],
  ["Reflet 50/50 70/35", "LUM-LUCAS → B82:H85"],
  ["K 1,24/0,95/1,56 Fu", "LUM-LUCAS → E103:H106"],
  ["Fdl 0,75", "LUM-LUCAS → B121"],
  ["Φt / N 3/18/2/15", "LUM-LUCAS → F145:H161"],
  ["Grade CERTO 3,30m", "LUM-LUCAS → B167:J170"],
  ["P/Q/S/I/Eobt", "LUM-LUCAS → C190:J200"],
  ["Ip L18-21", "QD-ILUM → QDL R21-R24 col J"],
  ["Ip'/Iz' + seção", "QD-ILUM → QDL-FATOR R21-R24 + SEÇÃO R21-R24"],
  ["Disjuntor C10 5kA", "QD-ILUM → DISJUNTORES R21-R24 + WEG p3-5"],
  ["Queda <4%", "QD-ILUM → QDL-QUEDA R392-R448 col J"],
  ["Balanço 6940/6560/5880", "QD-ILUM → BALANÇO TOTAL R23-R33"],
  ["Alimentador 127m", "QD-ILUM → QDGL R60-R64/R127-R134"],
  ["TUG/TUE + chuveiro", "QD-ILUM → QDF-TOMADAS-LUCAS R3-R23"],
  ["Ampacidade B1 17,5/24A", "Prysmian pdfp53 Tab2 + PIE04 p58-61"],
  ["ftemp 0,79 fagrup", "Prysmian pdfp57-58 + PIE04 p52-66"],
  ["V/A.km queda", "Prysmian pdfp61-62 + PIE05 p24-30"],
  ["Curva C / Icu", "WEG Minidisj p3-5 + PIE06 p27-39"],
  ["Enunciado/DWG", "05-.../01-Dados Iniciais (6p) + 02-Plantas/*.dwg"]], widths=(52,128), fs=7.5)
pdf.ln(2)
prova("Raiz curta: ProjetosIndustriais/  •  T1/: DESENVOLVIMENTO/.../T1/  •  Aulas: 01 - Aulas e Slides/  •  Prysmian: 03 - Cabos.../  •  WEG: 04 - Catalogos.../02 - Protecao.../  •  Tabelas luz: 02 - Luminotecnica/")

# ================= 23 =================
h1("23. Final", "Glossário + checklist + pendências + referências")
h2("Glossário em 10 linhas")
tabela(["Termo", "Em 1 linha"],
 [["E (lux)", "Luz por m² que precisa chegar (alvo da norma)"],
  ["Φt (lm)", "Luz que as lâmpadas devem emitir (E×S/Fu/Fdl)"],
  ["Fu / Fdl / K", "Fração que chega / desconto sujeira / proporção da sala"],
  ["Nteo / N / grade", "Teórico / teto instalado / desenho nx×ny"],
  ["P/Q/S/I", "Ativa/var/aparente/corrente (S=√(P²+Q²), I=S/220)"],
  ["Ip/Ip'/Iz/Iz'/In", "Projeto / corrigida / tabela / corrigida / disjuntor"],
  ["B1 / PVC / 2CC", "Embutido alvenaria / isolação 70°C / fase+neutro"],
  ["MDW-C10 5kA C", "Mini WEG 10A curva C Icu 5kA"],
  ["ΔV 4%/7%", "Queda terminal / total trafo-lum"],
  ["TUG/TUE/DDR", "Tomada geral / específica / protege gente 30mA"]], widths=(36,144), fs=8)
pdf.ln(2)
h2("Checklist de apresentação (fale nesta ordem)")
for s in ["1 Enunciado Lumens + Hpp 0,80.", "2 DADOS L11-L14 + 120VA/ponto.", "3 Peso 0→médio + MAX → 200/1500/200/750.", "4 TMS 6000lm + reator 24,1W FP0,90.", "5 Reflet + bege 35% (dado × premissa).", "6 Hlp 2,20 + K.", "7 2 vizinhos Fu + interpolação ao vivo.", "8 Fdl 0,75 (+ cenário 0,70).", "9 Φt→N→Eobt + total 38/4560VA por QDL.", "10 Ip→seção→C10→queda<4%→balanço→127m→QDF. Feche com sinótico <7%."]:
    bul(s, size=8.5)
h2("Premissas + pendências (diga antes que perguntem)")
for s in ["Pé-direito 3m = instalação no teto; tirante muda Hlp/K.", "BEGE 35% pior caso; 45% muda Esc 15→14.", "Piso 10% (tabela) vs azulejo real — limitação declarada.", "Fdl 0,75 comercial; alternativa 0,70.", "TMS é escolha de cálculo; trocar invalida Fu+carga.", "127m estimativa — MEDIR no DWG (QDGL-QDL5/6/7).", "Confirmar potência climatizadores + nº chuveiros.", "Revisar EPR/PVC QDL0-4 (22A é PVC).", "Transferir tabelas p/ T1-MEMORIAL DE CALCULO.docx."]:
    bul(s, size=8.5)
pdf.add_page()
pdf.set_fill_color(*AZUL_D)
pdf.set_text_color(255,255,255)
pdf.set_font("DejaVu", "B", 11)
pdf.multi_cell(0, 8, "  23. Final (cont.)   Referências + entrega", fill=True)
pdf.ln(2)
h2("Referências completas (com páginas)")
for s in ["Dados Iniciais 6p (p1 BT/alt, p2 QDL5/6/7, p3 5kA, p5-6 Lumens/Hpp/TUG, p6 Prysmian+V/A.km).", "PIE 02 105p (p60-62 E, p64-68 Fu/K, p67 interp, p69-70 Fdl, p73 N, p74 disposição, p75 reator).", "PIE 04 100p (p48-61 B1/ampacidade, p52-66 ftemp/fagrup).", "PIE 05 75p (p14-19 limites, p20-30 queda, p39-45 neutro).", "PIE 06 105p (p27-41 curvas/Icu).", "Prysmian 73p (pdfp53 B1 17,5/24A, pdfp57 0,79/agrup, pdfp61-62 V/A.km, pdfp48 TUG).", "WEG Minidisj 20p (p3 curva C, p5 MDW 5kA, p6-7 MDWH).", "A1 P1 5p scan (2.1/2.5/2.6/2.9/2.10/Fdl/reatores).", "Planilhas: LUM-LUCAS A1:J219 + QD-ILUM 9 abas + DADOS L11-L14 + RESPONSABILIDADES."]:
    bul(s, size=8)
pdf.ln(2)
box("PRONTO PARA ENTREGAR", "Copie as 4 tabelas de luz (E, K/Fu, N/Eobt, QDL) + 4 de quadros (Ip/seção/C10/queda) para o T1-MEMORIAL DE CALCULO.docx na ordem QDL5→QDL6→QDL7→QDF. Leve este guia + FINAL_REVISADA aberta (fórmulas) + Tab 2.9 + Prysmian pdfp53/57/61 + WEG p3-5. Boa prova!", VERDE_BG, VERDE_D, PRETO)

pdf.output(str(OUT))
print(f"OK: {OUT} ({OUT.stat().st_size/1024:.0f} kB)")
