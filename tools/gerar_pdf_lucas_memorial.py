#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Memorial explicativo único da parte do Lucas — T1 + T2.
Editorial, tipografia nativa (sem imagens), equações compostas com frações reais."""
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import MethodReturnValue

OUT = Path("/mnt/c/Users/lucas/Desktop/Engenharia/ProjetosIndustriais/T1_T2_LUCAS_Memorial_Explicativo.pdf")

# ---------------- paleta ----------------
NAVY   = (16, 42, 67)
ORANGE = (191, 87, 0)
PAPER  = (252, 250, 246)
INK    = (24, 28, 36)
MUTED  = (96, 104, 118)
RULE   = (219, 211, 197)
GREEN  = (23, 92, 62);  GREEN_BG  = (235, 244, 237)
AMBER  = (146, 96, 8);  AMBER_BG  = (252, 246, 229)
PURP   = (73, 48, 118); PURP_BG   = (240, 236, 248)
RED    = (148, 38, 32); RED_BG    = (250, 233, 231)
BLUE_BG = (233, 239, 247)
HEAD_TXT = (255, 255, 255)

SER = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SAN = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

class PDF(FPDF):
    def multi_cell(self, w, h=None, text="", border=0, align="J", fill=False, **kw):
        kw.setdefault("new_x", "LMARGIN"); kw.setdefault("new_y", "NEXT")
        return super().multi_cell(w, h, text, border, align, fill, **kw)
    def header(self):
        if self.page_no() == 1: return
        self.set_font("San", "", 6.3)
        self.set_text_color(*MUTED)
        self.set_y(7)
        self.cell(0, 4, "PARTE DO LUCAS  ·  T1 + T2  ·  MEMORIAL EXPLICATIVO", align="R")
        self.set_y(13)
    def footer(self):
        self.set_y(-12)
        self.set_draw_color(*RULE); self.set_line_width(0.3)
        self.line(17, self.get_y(), 193, self.get_y())
        self.set_y(-10)
        self.set_font("Ser", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 5, f"—  {self.page_no()}  —", align="C")

pdf = PDF("P", "mm", "A4")
pdf.alias_nb_pages()
pdf.set_auto_page_break(True, margin=15)
pdf.set_margins(17, 15, 17)
pdf.add_font("Ser", "", SER); pdf.add_font("Ser", "B", SERB)
pdf.add_font("San", "", SAN); pdf.add_font("San", "B", SANB)
pdf.set_page_background(PAPER)

def need(h):
    if pdf.get_y() + h > 276:
        pdf.add_page()

# ---------------- estilos ----------------
def chap(kicker, titulo, subt="", nova=True):
    if nova:
        if pdf.get_y() > 40:
            pdf.add_page()
    else:
        need(48)
        pdf.ln(6)
    pdf.set_font("San", "B", 8)
    pdf.set_text_color(*ORANGE)
    pdf.multi_cell(0, 4.6, kicker.upper())
    pdf.ln(0.5)
    pdf.set_font("Ser", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 8, titulo)
    pdf.set_draw_color(*ORANGE); pdf.set_line_width(0.8)
    y = pdf.get_y() + 1
    pdf.line(17, y, 63, y)
    pdf.set_y(y + 2.5)
    if subt:
        pdf.set_font("Ser", "", 9.3)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(0, 5.2, subt)
        pdf.ln(1.5)

def h2(t):
    need(16)
    pdf.ln(1.5)
    pdf.set_font("San", "B", 10.5)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 6, t)
    pdf.ln(0.5)

def p(t, bold=False, size=9.6):
    pdf.set_font("Ser", "B" if bold else "", size)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 5.6, t)
    pdf.ln(1.2)

def bul(t, size=9.4):
    need(10)
    pdf.set_font("San", "B", size)
    pdf.set_text_color(*ORANGE)
    pdf.cell(5.5, 5.6, "–")
    pdf.set_font("Ser", "", size)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 5.6, t)
    pdf.ln(0.8)

def box(label, text, dark, bg):
    need(24)
    y0 = pdf.get_y()
    pdf.set_font("San", "B", 7.8)
    pdf.set_text_color(*dark)
    pdf.multi_cell(0, 4.8, label.upper())
    pdf.ln(0.4)
    pdf.set_font("Ser", "", 9.2)
    pdf.set_text_color(*INK)
    pdf.set_fill_color(*bg)
    pdf.multi_cell(0, 5.6, text, fill=True)
    y1 = pdf.get_y()
    pdf.set_fill_color(*dark)
    pdf.rect(17, y0, 1.7, y1 - y0 - 1, "F")
    pdf.ln(2.6)

def conceito(t): box("Conceito", t, NAVY, BLUE_BG)
def origem(t):   box("Origem — arquivo, página e célula", t, GREEN, GREEN_BG)
def porque(t):   box("Por quê assim", t, AMBER, AMBER_BG)
def prova(t):    box("Na prova — ache em 30 s", t, PURP, PURP_BG)
def alerta(t):   box("Erro que reprova", t, RED, RED_BG)

# ---------------- equações nativas ----------------
_EQN = [0]
def _w(txt, size=11, bold=False):
    pdf.set_font("Ser", "B" if bold else "", size)
    return pdf.get_string_width(txt)

def eq(tokens, leia=None, exemplo=None, size=11):
    """tokens: str (texto simples) OU lista: ('t', txt) | ('f', num, den)"""
    if isinstance(tokens, str):
        tokens = [("t", tokens)]
    EQH_FR = 15.0; EQH_TX = 9.0
    has_frac = any(t[0] == "f" for t in tokens)
    H = EQH_FR if has_frac else EQH_TX
    # larguras
    parts = []
    total = 0
    for tk in tokens:
        if tk[0] == "t":
            w = _w(tk[1] + " ", size)
        else:
            w = max(_w(tk[1], size), _w(tk[2], size)) + 5
        parts.append((tk, w)); total += w
    total -= 1  # espaço extra do último
    num = _EQN[0] + 1; _EQN[0] = num
    no_w = _w(f"({num})", 8.5)
    box_w = min(176, total + 12)
    need(H + 9 + (10 if exemplo else 0) + 4)
    x0 = 17 + (176 - box_w) / 2
    y0 = pdf.get_y()
    pdf.set_fill_color(247, 244, 237)
    pdf.rect(x0, y0, box_w, H + 6, "F")
    pdf.set_fill_color(*ORANGE)
    pdf.rect(x0, y0, 1.4, H + 6, "F")
    x = 17 + (176 - total) / 2
    ymid = y0 + 3 + (H / 2)
    for tk, w in parts:
        if tk[0] == "t":
            pdf.set_font("Ser", "", size)
            pdf.set_text_color(*INK)
            pdf.set_xy(x, ymid - 3)
            pdf.cell(w, 6, tk[1].strip(), align="R")
            x += w
        else:
            pdf.set_font("Ser", "", size)
            pdf.set_text_color(*INK)
            pdf.set_xy(x, ymid - 8.4)
            pdf.cell(w, 5.4, tk[1], align="C")
            pdf.set_draw_color(*INK); pdf.set_line_width(0.35)
            ly = ymid + 0.2
            pdf.line(x + 1, ly, x + w - 1, ly)
            pdf.set_xy(x, ly + 0.6)
            pdf.cell(w, 5.4, tk[2], align="C")
            x += w
    pdf.set_font("San", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(193 - no_w - 2, y0 + 2)
    pdf.cell(no_w + 2, 4.4, f"({num})", align="R")
    pdf.set_xy(17, y0 + H + 6)
    if leia:
        pdf.set_font("Ser", "", 8.6)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(0, 4.8, "Leia assim:  " + leia)
    if exemplo:
        pdf.ln(0.6)
        pdf.set_font("Ser", "B", 9)
        pdf.set_text_color(*INK)
        pdf.set_draw_color(*RULE); pdf.set_line_width(0.3)
        pdf.multi_cell(0, 5.4, exemplo, border=1, fill=True)
    pdf.ln(3)

# ---------------- tabelas ----------------
def tabela(headers, rows, widths, aligns=None, fs=8.4, hi=None, total=False, fonte_nota=None):
    need(16 + 6.4 * (len(rows) + 1))
    if aligns is None:
        aligns = "c" * len(headers)
    xs = [17]
    for w in widths: xs.append(xs[-1] + w)
    # header
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*HEAD_TXT)
    pdf.set_font("San", "B", 7.9)
    hh = 7.2
    pdf.rect(17, pdf.get_y(), sum(widths), hh, "F")
    for i, hd in enumerate(headers):
        pdf.set_xy(xs[i] + 1.5, pdf.get_y() + 1.2)
        pdf.cell(widths[i] - 3, 4.8, hd, align="L")
    pdf.set_y(pdf.get_y() + hh)
    # linhas
    for r, row in enumerate(rows):
        is_total = total and r == len(rows) - 1
        # medir altura
        hmax = 6.2
        for i, cell in enumerate(row):
            pdf.set_font("Ser", "B" if is_total else "", fs)
            h = pdf.multi_cell(widths[i] - 3, 4.6, str(cell), dry_run=True,
                               output=MethodReturnValue.HEIGHT)
            hmax = max(hmax, h + 1.8)
        ytop = pdf.get_y()
        if is_total:
            pdf.set_fill_color(AMBER_BG)
        elif hi is not None:
            pdf.set_fill_color(244, 247, 251)
        else:
            pdf.set_fill_color(248, 246, 241) if r % 2 else pdf.set_fill_color(255, 255, 255)
        pdf.rect(17, ytop, sum(widths), hmax, "F" if (is_total or hi is not None or r % 2) else "")
        if is_total:
            pdf.set_draw_color(*ORANGE); pdf.set_line_width(0.5)
            pdf.line(17, ytop, 17 + sum(widths), ytop)
        for i, cell in enumerate(row):
            a = {"l": "L", "c": "C", "r": "R"}[aligns[i]]
            pdf.set_font("Ser", "B" if is_total else "", fs)
            pdf.set_text_color(*INK)
            pdf.set_xy(xs[i] + 1.5, ytop + 0.9)
            pdf.multi_cell(widths[i] - 3, 4.6, str(cell), align=a)
        pdf.set_draw_color(*RULE); pdf.set_line_width(0.25)
        pdf.line(17, ytop + hmax, 17 + sum(widths), ytop + hmax)
        pdf.set_y(ytop + hmax)
    pdf.ln(2)
    if fonte_nota:
        pdf.set_font("San", "", 7.2)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(0, 4.2, "Fonte: " + fonte_nota)
        pdf.ln(1.5)

# ================= CAPA =================
pdf.add_page()
pdf.ln(16)
pdf.set_font("San", "B", 8.5)
pdf.set_text_color(*ORANGE)
pdf.multi_cell(0, 5, "PROJETO INDUSTRIAL  ·  RECAPADORA DE PNEUS  ·  EEL 2026-2", align="C")
pdf.ln(4)
pdf.set_font("Ser", "B", 27)
pdf.set_text_color(*NAVY)
pdf.multi_cell(0, 11.5, "A parte do Lucas", align="C")
pdf.set_font("Ser", "", 13.5)
pdf.set_text_color(*MUTED)
pdf.multi_cell(0, 7.5, "Luminotécnico e quadros QDL · QDGL · QDF\nMemorial explicativo — do zero à prova", align="C")
pdf.ln(5)
pdf.set_draw_color(*ORANGE); pdf.set_line_width(1)
pdf.line(85, pdf.get_y(), 125, pdf.get_y())
pdf.ln(6)
# cartão de números
nums = [("38", "pontos de luz"), ("4 560", "VA instalados"), ("4 %", "queda máxima"), ("7 %", "sinótico total")]
cw = 42; x = 17 + (176 - 4 * cw) / 2
y = pdf.get_y()
for v, l in nums:
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*RULE); pdf.set_line_width(0.3)
    pdf.rect(x, y, cw - 3, 20, "FD")
    pdf.set_font("Ser", "B", 15)
    pdf.set_text_color(*NAVY)
    pdf.set_xy(x, y + 2.5); pdf.cell(cw - 3, 8, v, align="C")
    pdf.set_font("San", "", 7)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(x, y + 11.5); pdf.cell(cw - 3, 4.5, l, align="C")
    x += cw
pdf.set_y(y + 24)
pdf.ln(4)
p("Um único documento que conta toda a história da sua parte: quanta luz cada sala precisa, quantas luminárias isso dá, que fio e que disjuntor aguentam, e onde cada número mora — na planilha, no catálogo e na aula. As fórmulas são compostas de verdade, com fração desenhada e tradução em português logo abaixo.", size=9.8)
pdf.ln(1)
box("Escopo das entregas (plano de ensino)",
    "T1 — em equipe: memorial de cálculo e planta do luminotécnico (localização, especificação e apresentação dos condutos, das cargas elétricas e dimensionamento e especificação completa dos QDLs e QDFs).   ·   T2 — em equipe: cálculos em regime e transitório térmico e determinação da temperatura dos condutores do circuito especificado.",
    NAVY, BLUE_BG)

# ================= 1. PARTE DO LUCAS =================
chap("Capítulo 1", "O terreno: o que é sua parte", "Quatro salas, quatro circuitos, quatro quadros — e os arquivos que provam tudo.")
conceito("Você entrega luz + fio + proteção de 4 salas. Sala de Produtos e Controle de Qualidade dividem o quadro QDL6, mas com circuitos próprios (L19 e L20). O Escritório é o QDL5 (L18) e o Banheiro é o QDL7 (L21).")
tabela(["Sala", "Medida", "Circuito", "Quadro", "Iluminância-alvo"],
 [["Sala de Produtos", "5,00 × 6,00 m", "L19 — 3 luminárias", "QDL6", "200 lux"],
  ["Controle de Qualidade", "5,00 × 6,00 m", "L20 — 18 luminárias", "QDL6", "1 500 lux"],
  ["Banheiro / Vestiário", "5,23 × 3,50 m", "L21 — 2 luminárias", "QDL7", "200 lux"],
  ["Escritório", "8,12 × 6,00 m", "L18 — 15 luminárias", "QDL5", "750 lux"]],
 widths=[46, 30, 38, 22, 40], aligns="lcccc",
 fonte_nota="RESPONSABILIDADES.xlsx · PROJETO INDUSTRIAIS TRABALHO.xlsx, aba DADOS, linhas 11–14 · LUM-LUCAS_FINAL_REVISADA.xlsx, linhas 190–193")
porque("Cada sala tem circuito próprio porque a iluminância exigida é muito diferente (200 contra 1 500 lux) e o comando precisa ser independente. Mesmo somando 2 520 VA — abaixo do limite de 4 500 VA do grupo — juntar tudo tiraria a seletividade de acionamento.")
origem("Medidas e materiais: DADOS L11–L14 (colunas D, E, K). Divisão do trabalho: RESPONSABILIDADES.xlsx, aba Página1. Toda a luz: LUM-LUCAS_FINAL_REVISADA.xlsx, aba LUM-LUCAS (A1:J219). Todo o fio: QD-ILUMINAÇÃO.xlsx (9 abas). Caminho: DESENVOLVIMENTO/PROJETOS INDUTRIAIS SICA/T1/")

# ================= 2. ENUNCIADO =================
chap("Capítulo 2", "O contrato: o que o enunciado manda", "Quatro frases dos Dados Iniciais decidem todas as outras escolhas. Transcrição literal, sem inventar.")
bul("Método: “o método utilizado deverá ser o de Lumens” para as áreas de produção e, por extensão do memorial do grupo, para as suas salas; a Recapagem usa Cavidades e não é sua (p. 5/6).")
bul("Altura: “a altura de manuseio para o trabalho é de 0,80 metros” — vale para todas as salas (p. 5/6).")
bul("Elétrica: BT 380/220 V, 60 Hz; altitude 1 200 m; 45 °C; curto presumido de 5 kA nos QDL/QDF e 7 kA nos CCM (p. 1 e 3/6).")
bul("Catálogo: ampacidade e queda de tensão trecho a trecho pela formulação completa com o Prysmian (V/A.km); TUG/TUE pela NBR 5410, com climatizadores em Sala de Produto, CQ e Escritório e chuveiros de 9 kW no Banheiro (p. 6/6).")
porque("Altitude não corrige ampacidade em baixa tensão; a temperatura de 45 °C sim — fator 0,79 para PVC. O curto de 5 kA escolhe a capacidade de interrupção do disjuntor. O pé-direito de 3,00 m vem da própria aba DADOS (coluna K, linhas 11–14).")
prova("Dados Iniciais: pasta 05 - Projeto Industrial.../01 - Dados Iniciais/ (6 páginas). Planta: .../02 - Plantas e DWG/. Calendário T1–T4: 00 - Disciplina e Plano de Ensino/PIE - Plano de Ensino (03AGO).pdf.")

# ================= 3. FUNDAMENTOS =================
chap("Capítulo 3", "A luz em quatro passos", "PIE 02, p. 39–75. Toda a sua parte é repetição desta lógica.")
conceito("Fluxo (lm) é a luz que sai da lâmpada. Iluminância (lux) é a luz que pousa em cada m². Fu e Fdl são as perdas do caminho e do tempo; K descreve a forma da sala. Lâmpada é o tubo; luminária é o conjunto com reator.")
eq("Φútil = E × S",
   "o produto do alvo pela área dá a luz que precisa POUSAR no plano de trabalho.")
eq([("t", "Φt  ="), ("f", "E × S", "Fu × Fdl")],
   "para compensar as perdas de utilização e depreciação, o fluxo que as lâmpadas precisam EMITIR divide as perdas no denominador.")
eq([("t", "Nteo  ="), ("f", "Φt", "n × φ"), ("t", "→  N = teto(Nteo)")],
   "com n × φ = 2 × 3 000 = 6 000 lm por luminária, dividir dá a quantidade teórica; instala-se sempre o teto inteiro.")
eq([("t", "Eobt  ="), ("f", "N × n × φ × Fu × Fdl", "S"), ("t", "≥  E")],
   "recalcula-se com o N instalado: a prova dos nove. Se der abaixo do alvo, faltou luminária.")
eq([("t", "Hlp = 3,00 − 0,80 = 2,20 m        K  ="), ("f", "L × C", "Hlp × (L + C)")],
   "altura útil e índice do recinto: K alto é sala compacta (luz rende), K baixo é sala “alta” (luz se perde na parede).")
alerta("Não troque os pares: Φt (emitir) não é Φútil (pousar); Nteo (2,73) não é N (3); E (alvo) não é Eobt (conseguida). A verificação final é sempre Eobt ≥ E.")
origem("PIE 02: p. 39–41 grandezas; p. 60–62 iluminância; p. 64–68 Fu e K; p. 67 interpolação; p. 69–70 Fdl; p. 73 fluxo e N; p. 74 disposição; p. 75 reator. Tabelas de Mamede: 2.4, 2.5, 2.6, 2.9, 2.10 (reproduzidas no A1 P1 — Tabelas Auxiliares).")

# ================= 4. MEDIDAS + E =================
chap("Capítulo 4", "Medidas reais e o alvo E", "DADOS + peso + MAX: a decisão que mais reprova.")
h2("4.1  Geometria das quatro salas")
tabela(["Sala", "L × C", "S", "Hlp", "K (conta)"],
 [["Sala de Produtos", "5,00 × 6,00", "30,000 m²", "2,20", "30,00 / 24,20 = 1,2397"],
  ["Controle de Qualidade", "5,00 × 6,00", "30,000 m²", "2,20", "1,2397 (idêntica)"],
  ["Banheiro", "5,23 × 3,50", "18,305 m²", "2,20", "18,31 / 19,21 = 0,9531"],
  ["Escritório", "8,12 × 6,00", "48,720 m²", "2,20", "48,72 / 31,06 = 1,5684"]],
 widths=[44, 26, 26, 18, 62], aligns="lcccl",
 fonte_nota="LUM-LUCAS: F3:F6 (Hlp) e E103:E106 (K); PIE 02 p. 65.")
h2("4.2  De onde vem o 1 500 e o 750")
p("A iluminância nasce da atividade, não da metragem. Duas tabelas competem: a faixa por ambiente (com peso por idade, precisão e fundo da tarefa) e o valor específico da atividade. Fica o MAIOR dos dois — a condição mais crítica, aula de 27/08.", bold=True)
tabela(["Critério (Tab. 2.5)", "Adotado", "Peso"],
 [["Idade dos observadores", "41 anos (faixa 40–55)", "0"],
  ["Velocidade e precisão", "Importante", "0"],
  ["Refletância do fundo", "0,40 (faixa 30–70%)", "0"],
  ["Soma 0 → usa o valor MÉDIO da faixa", "—", "—"]],
 widths=[86, 56, 34], aligns="lcc")
tabela(["Sala", "Faixa (médio)", "Específica", "Adotada = MAX"],
 [["Sala de Produtos — depósito A", "100-150-200 → 150", "200", "200"],
  ["Controle de Qualidade — inspeção B", "1000-1500-2000 → 1500", "500", "1 500"],
  ["Banheiro — permanência curta A", "50-75-100 → 75", "200", "200"],
  ["Escritório — sala de trabalho B", "500-750-1000 → 750", "250", "750"]],
 widths=[62, 44, 34, 36], aligns="lccc",
 fonte_nota="LUM-LUCAS: R13–R17 (peso), R20–R25 (faixas), J22:J25 (=MAX) e B145:B148 (E final).")
porque("Versões antigas usavam 500 e 250 lux (só a coluna específica) e subdimensionavam CQ e Escritório em 3 vezes. A faixa já carrega o peso da tarefa; o MAX cumpre a regra da condição mais crítica.")
prova("E final: LUM-LUCAS H22:J25 e B145:B148. Leve as Tabelas 2.5 e 2.6 impressas e some os pesos na hora: soma ≤ −2 usa o inferior, ≥ +2 o superior, entre −1 e +1 o médio.")

# ================= 5. LÂMPADA + REFLET =================
chap("Capítulo 5", "A fonte e a parede", "TMS 426: 6 000 lm por ponto · refletâncias: o que é dado e o que é premissa.")
conceito("A TMS 426 abriga 2 tubos fluorescentes de 40 W (3 000 lm cada). O reator duplo de 220 V dissipa 24,1 W e tem fator de potência 0,90 — indutivo, portanto cria potência reativa Q. Parede clara devolve luz (Fu sobe); parede escura engole (Fu cai).")
eq("P = 2 × 40 + 24,1 = 104,1 W        Q = P · tan(arccos 0,90) = 50,42 var        S = √(P² + Q²) = 115,67 VA",
   "potência ativa soma tubos e reator; a reativa nasce do ângulo do reator; a aparente é a hipotenusa. Adota-se 120 VA por ponto (número inteiro, com margem).")
tabela(["Refletância", "Dado da planilha", "Adotada", "Critério"],
 [["Sala de Produtos", "Teto CLARO · parede CLARA", "50 / 50", "descrição qualitativa → coluna clara"],
  ["Controle de Qualidade", "Teto BRANCO · parede BRANCA", "70 / 50", "80% não existe na tabela → limite 70%"],
  ["Banheiro", "Teto CLARO · parede CLARA", "50 / 50", "igual à Sala de Produtos"],
  ["Escritório", "Teto BRANCO · parede BEGE", "70 / 35", "bege 35–40% → 35% (pior caso)"]],
 widths=[40, 50, 24, 62], aligns="llcl",
 fonte_nota="LUM-LUCAS B82:H85 (piso fixo em 10%: azulejo cinza registrado, mas a tabela só publica piso 10%) · Tabela de refletâncias e Tab. 2.9/2.10 · PIE 02 p. 63 e 67.")
porque("A TMS 426 não é a única opção (TMS 500, TCK 427, HDK 472 existem na tabela), mas é a única que fornece luminária, Fu e dados elétricos juntos — cálculo rastreável ponta a ponta. LED exigiria substituir Fu e a carga por datasheet de fabricante.")
prova("Luminária e reator: LUM-LUCAS B60:B75 e B179:B185. Refletâncias: B82:H85. Na apresentação, diga em voz alta o que é dado e o que é premissa.")

# ================= 6. FU =================
chap("Capítulo 6", "Fu: a interpolação aberta", "Tabela 2.9 da TMS 426 — linha do K, coluna da refletância. Sem chute visual.")
eq([("t", "Fu  =  Fu(inf)  +"), ("f", "K − K(inf)", "K(sup) − K(inf)"), ("t", "× [ F(sup) − F(inf) ]")],
   "anda do vizinho de baixo pelo caminho até o de cima. Se a parede cai entre duas colunas (bege 35%), interpola-se de novo entre colunas.")
eq([("t", "Fu(35%)  =  Fu(30%)  +"), ("f", "35 − 30", "50 − 30"), ("t", "× [ Fu(50%) − Fu(30%) ]")],
   "a interpolação dupla do Escritório: primeiro em K (1,5684 entre 1,50 e 2,00), depois entre parede 30% e 50%."),
tabela(["Sala", "Vizinhos na Tab. 2.9", "Conta", "Fu"],
 [["Sala de Produtos — 50/50, K 1,2397", "K 1,00 → 0,44  ·  K 1,25 → 0,49", "0,44 + 0,9588 × 0,05", "0,4879"],
  ["Controle de Qualidade — 70/50", "K 1,00 → 0,50  ·  K 1,25 → 0,56", "0,50 + 0,9588 × 0,06", "0,5575"],
  ["Banheiro — 50/50, K 0,9531", "K 0,80 → 0,38  ·  K 1,00 → 0,44", "0,38 + 0,7654 × 0,06", "0,4259"],
  ["Escritório — dupla, K 1,5684", "1,5 → 0,54/0,61  ·  2,0 → 0,61/0,68", "0,5496 / 0,6196 → 35%", "0,5671"]],
 widths=[52, 50, 42, 32], aligns="llcc",
 fonte_nota="LUM-LUCAS: E103:E106 (K) e H103:H106 (Fu). PIE 02 p. 67: “a interpolação define um valor entre os limites tabelados”.")
alerta("Nunca escolha Fu “no olho”. Mostre os dois vizinhos e a conta. Trocar de coluna de refletância sem justificativa derruba o Fu e infla o projeto.")

# ================= 7. FLUXO E N =================
chap("Capítulo 7", "Do fluxo à quantidade", "Fdl 0,75 → Φt → 3 · 18 · 2 · 15 luminárias.")
p("Fator de depreciação: a planilha adota 0,75 — “luminária comercial”, valor específico da tabela de Fdl (Mamede, Tab. 2.9), que prevalece sobre o genérico 0,70 da aula (PIE 02 p. 69). Sendo denominador, Fdl menor pede mais fluxo: ficar com o específico documentado é a escolha defensável.", bold=True)
tabela(["Sala", "E × S", "Fu × Fdl", "Φt [lm]", "Nteo → N (grade)"],
 [["Sala de Produtos", "200 × 30,00 = 6 000", "0,4879 × 0,75", "16 395,66", "2,7326 → 3  (3 × 1)"],
  ["Controle de Qualidade", "1 500 × 30,00 = 45 000", "0,5575 × 0,75", "107 619,33", "17,9366 → 18  (6 × 3)"],
  ["Banheiro", "200 × 18,305 = 3 661", "0,4259 × 0,75", "11 460,51", "1,9101 → 2  (1 × 2)"],
  ["Escritório", "750 × 48,72 = 36 540", "0,5671 × 0,75", "85 914,94", "14,3192 → 15  (3 × 5)"]],
 widths=[40, 42, 30, 30, 34], aligns="lcccl",
 fonte_nota="LUM-LUCAS: Fdl B121 · Φt F145:F148 · N E158:H161 (ROUNDUP) e grades G158:H161.")
porque("Arredonda sempre para cima: com 2 luminárias a Sala de Produtos ficaria em 146 lux, abaixo dos 200. A sensibilidade do Fdl mora no CQ: com 0,70 o fluxo sobe 7,1% e a folga de 0,4% pode pedir a 19ª luminária — deixe a célula B121 editável e mostre os dois cenários.")
prova("Fdl: B121 · Φt: F145:F148 · N e grade: E158:H161. Na prova, cite a alternativa 0,70 como análise de sensibilidade — demonstra domínio.")

# ================= 8. DISTRIBUIÇÃO + CARGA =================
chap("Capítulo 8", "Planta e carga elétrica", "Grades dentro do limite 3,30 m · potência vetorial P + jQ · a folga apertada do CQ.")
p("Regra de disposição da aula: o espaçamento entre luminárias não pode passar de 1,5 × Hlp = 3,30 m, com meia-distância nas bordas. A quantidade calculada é o mínimo normativo; o CAD pode exigir um ponto extra por porta ou pilar — e aí se recalcula a E obtida.", bold=True)
tabela(["Sala", "Grade", "X / X1 (m)", "Y / Y1 (m)", "≤ 3,30?"],
 [["Sala de Produtos", "3 × 1 = 3", "2,00 / 1,00", "— / 2,50", "SIM"],
  ["Controle de Qualidade", "6 × 3 = 18", "1,00 / 0,50", "1,67 / 0,83", "SIM"],
  ["Banheiro", "1 × 2 = 2", "— / 1,75", "2,62 / 1,31", "SIM"],
  ["Escritório", "3 × 5 = 15", "2,00 / 1,00", "1,62 / 0,81", "SIM"]],
 widths=[44, 28, 34, 34, 22], aligns="lcccl",
 fonte_nota="LUM-LUCAS B167:J170 (coluna J = “CERTO”) · PIE 02 p. 74.")
eq([("t", "P = N × 104,1 W        Q = N × 50,42 var        S = √(P² + Q²)        I = S / 220")],
   "a nota do projeto exige potência vetorial: o reator é indutivo, então existe Q e a corrente cresce — ignorá-la subdimensionaria fio e disjuntor.")
tabela(["Sala", "N", "P [W]", "Q [var]", "S [VA]", "I [A]", "E obtida"],
 [["Sala de Produtos", "3", "312,3", "151,3", "360", "1,64", "219,6 ≥ 200"],
  ["Controle de Qualidade", "18", "1 873,8", "907,5", "2 160", "9,82", "1 505,3 ≥ 1 500"],
  ["Banheiro", "2", "208,2", "100,8", "240", "1,09", "209,4 ≥ 200"],
  ["Escritório", "15", "1 561,5", "756,3", "1 800", "8,18", "785,7 ≥ 750"]],
 widths=[44, 12, 22, 22, 22, 18, 36], aligns="lcccccc", hi=True,
 fonte_nota="LUM-LUCAS: B179:B185 (por ponto), C190:J193 (por sala), C197:G200 (por quadro).")
tabela(["Quadro", "Salas", "Luminárias", "P [W]", "S [VA]"],
 [["QDL5", "Escritório", "15", "1 561,5", "1 800"],
  ["QDL6", "Sala de Produtos + CQ", "21 (3 + 18)", "2 186,1", "2 520"],
  ["QDL7", "Banheiro", "2", "208,2", "240"],
  ["TOTAL — parte do Lucas", "4 salas", "38", "3 955,8", "4 560"]],
 widths=[40, 56, 30, 26, 24], aligns="llccc", total=True)
alerta("A folga do Controle de Qualidade é de apenas +0,4% (1 505 contra 1 500). É consequência natural do 17,94 → 18, mas qualquer revisão de Fdl ou de fluxo mexe nele. Apresente como ponto de atenção, não como erro.")
prova("Carga por sala: C190:J193 · resumo por quadro: C197:G200 · E obtida: coluna J190:J193. Total do Lucas: 38 pontos · 3 955,8 W · 1 915,9 var · 4 560 VA.")

# ================= 9. QUADROS: IP =================
chap("Capítulo 9", "Quadros I — da carga à corrente", "A ponte entre o T1 e o fio é simples: 120 VA por ponto em 220 V.")
conceito("Ip é a corrente que vai circular. Iz é quanto o condutor aguenta na tabela (a 30 °C). Iz' é esse valor corrigido para o calor real. Ip' é a corrente de projeto já corrigida, para comparar. In é o disjuntor de prateleira.")
tabela(["Parâmetro do passo 0", "Valor adotado", "Onde está"],
 [["Tensão · temperatura", "220 V · 45 °C → fator 0,79 (PVC)", "Dados p. 1 + Prysmian pdf p. 57"],
  ["Curto presumido", "5 kA nos QDL/QDF", "Dados p. 3 (anotação J48: não é 2 kA)"],
  ["Instalação · isolação", "método 7 → referência B1 · PVC", "planilha M3 e Q71 · PIE 04 p. 58"],
  ["Harmônico", "× 1,15 (lâmpada de descarga)", "PIE 04, fatores de correção"],
  ["Limite de queda", "4% terminal · 7% trafo → luminária", "PIE 05 p. 14–19"]],
 widths=[46, 60, 70], aligns="lll")
eq([("t", "Ip  ="), ("f", "S = N × 120 VA", "220 V")],
   "corrente de projeto de cada circuito: a demanda dividida pela tensão de fase.")
tabela(["Circuito", "Sala", "N → demanda", "Ip", "Fase (cap. 12)"],
 [["L18 — QDL5", "Escritório", "15 → 1 800 VA", "8,18 A", "R"],
  ["L19 — QDL6", "Sala de Produtos", "3 → 360 VA", "1,64 A", "T"],
  ["L20 — QDL6", "Controle de Qualidade", "18 → 2 160 VA", "9,82 A", "S"],
  ["L21 — QDL7", "Banheiro", "2 → 240 VA", "1,09 A", "T"]],
 widths=[30, 46, 34, 22, 24], aligns="llccc",
 fonte_nota="QD-ILUMINAÇÃO, aba QDL, linhas 21–24 (colunas G, I, J).")
prova("Ip: aba QDL, coluna J. Demanda: coluna I. A fase só se define no capítulo 12 — aqui é só anotação.")

# ================= 10. AMPACIDADE =================
chap("Capítulo 10", "Quadros II — o fio aguenta?", "Ampacidade pelo catálogo obrigatório: B1 em eletroduto embutido, PVC a 45 °C.")
eq([("t", "Ip'  ="), ("f", "Ip × 1,15", "0,79 × 1,00"), ("t", "        Iz'  =  Iz × 0,79 × 1,00")],
   "a corrente é inflada pelo harmônico e corrigida pelos fatores de temperatura e agrupamento; do lado do fio, a tabela perde 21% com o calor de 45 °C.")
tabela(["Circuito", "Ip [A]", "Ip' [A]", "Iz' em 1,5 mm²", "Seção de fase (F = N = PE)"],
 [["L18", "8,18", "11,91", "13,83 ≥ 11,91", "1,5 mm² (folga 16%)"],
  ["L19", "1,64", "2,38", "13,83", "1,5 mm²"],
  ["L20", "9,82", "14,29", "13,83 < 14,29 — não serve", "2,5 mm² → Iz' 18,96 (folga 33%)"],
  ["L21", "1,09", "1,59", "13,83", "1,5 mm²"]],
 widths=[20, 20, 22, 44, 56], aligns="lcccl", hi=True,
 fonte_nota="QD-ILUMINAÇÃO: QDL-FATOR R21–R24 (Ip', Iz') · SEÇÃO CONDUTORES R21–R24 · Prysmian pdf p. 53 (B1 PVC: 1,5 → 17,5 A; 2,5 → 24 A) e p. 57 (fatores).")
p("Neutro com a mesma seção da fase (circuito de descarga com 3º harmônico — NBR 5410 6.2.5, PIE 05 p. 39–45); proteção igual à fase até 16 mm²; dois condutores carregados. Nas linhas dos colegas (QDL0–4) há EPR anotado com Iz de PVC: nas suas linhas o PVC é consistente.", bold=True)
prova("Ip': aba QDL-FATOR coluna N · Iz': coluna P · seções: aba SEÇÃO, colunas J–L · tabela B1: Prysmian pdf p. 53.")

# ================= 11. DISJUNTOR =================
chap("Capítulo 11", "Quadros III — a proteção", "Um disjuntor entre o fio e a carga, com memória de curto.")
eq("Iz'  >  In  >  Ip        ·        Icu ≥ 5 kA",
   "o disjuntor protege o fio (In abaixo de Iz') sem desarmar no trabalho (In acima de Ip), e aguenta o curto presumido do quadro.")
tabela(["Circuito", "Verificação", "Especificação WEG"],
 [["L18", "13,83 > 10 > 8,18", "MDW-C10 1P+N, Icu 5 kA, curva C"],
  ["L19", "13,83 > 10 > 1,64", "MDW-C10"],
  ["L20", "18,96 > 10 > 9,82", "MDW-C10 (fio 2,5 mm²)"],
  ["L21", "13,83 > 10 > 1,09", "MDW-C10"]],
 widths=[26, 52, 62], aligns="lcl", hi=True,
 fonte_nota="QD-ILUMINAÇÃO, aba DISJUNTORES, R21–R24 · WEG Minidisjuntores: curva C p. 3, MDW 5 kA p. 5 · PIE 06 p. 27–41.")
porque("Curva C (5 a 10 × In) absorve o pico de magnetização dos reatores fluorescentes sem nuisance trip; a curva B desarmaria na partida e a D é para motor. O In comercial de 10 A já atende os quatro circuitos.")
prova("In: aba DISJUNTORES coluna E · Icu: WEG p. 5 + Dados p. 3. Se o professor trocar o curto para 7 kA, a família sobe para MDWH (Icn 10 kA, p. 6–7).")

# ================= 12. QUEDA =================
chap("Capítulo 12", "Quadros IV — queda de tensão", "O cálculo mais temido, destrinchado trecho a trecho.")
conceito("O fio resiste e reage: cada metro soma R e X. A corrente que passa multiplica essa impedância pelo comprimento — e diminui a cada luminária que fica para trás. Soma-se tudo e compara com 4%.")
eq([("t", "ΔV  =  2 · Ip · L · ( R · cos φ  +  X · sen φ )")],
   "com cos φ = 0,90 e sen φ = 0,4359; o fator 2 é o caminho de ida e volta. L soma o reto, 1,5 m por curva e a subida de 1,5 m (3,00 − 1,50).")
eq([("t", "ΔV%  ="), ("f", "ΔV", "220 V"), ("t", "× 100        ·        limite 4%")],
   "a queda de cada trecho soma no acumulado; o último trecho fecha a conta do circuito.")
tabela(["Circuito", "Fio", "Trechos", "Acumulado", "Status"],
 [["L18 — Escritório", "1,5 mm² (R 14,81 · X 0,14 mΩ/m)", "15: QDL5-LU1 … LU14-LU15*", "2,33%", "OK"],
  ["L20 — CQ", "2,5 mm² (R 8,89 · X 0,13 mΩ/m)", "18 trechos", "1,50%", "OK"],
  ["L19 — Sala de Produtos", "1,5 mm²", "3 trechos", "0,20%", "OK"],
  ["L21 — Banheiro", "1,5 mm²", "2 trechos", "0,12%", "OK"]],
 widths=[38, 52, 42, 24, 20], aligns="llccc",
 fonte_nota="QD-ILUMINAÇÃO, aba QDL-QUEDA DE TENSÃO: R392–R408 (L18), R412–R416 (L19), R420–R439 (L20), R443–R446 (L21), nota R448 · Prysmian pdf p. 61–62 · PIE 05 p. 24–30.")
porque("O L20 já precisava de 2,5 mm² na ampacidade — e o menor R ajudou na queda. Os circuitos curtos (L19, L21) têm queda desprezível. As rotas seguem a grade do memorial: são estimativas até a medição no DWG; se o comprimento mudar, a queda escala proporcionalmente.")
prova("Queda por trecho: colunas I/J de cada bloco · R e X no cabeçalho do bloco e no Prysmian pdf p. 61. Na prova, refaça um trecho qualquer com a fórmula: é isso que ela cobra.")

# ================= 13. BALANÇO =================
chap("Capítulo 13", "Quadros V — balanço de fases", "Distribuir para a fase mais carregada doer menos.")
p("O time deixou as fases assim: R 5 140 · S 4 400 · T 5 280 VA (total 14 820). Sua parte entra para achatar a curva: o CQ — sua maior carga, 2 160 VA — vai para a fase mais vazia (S); o Escritório reforça a R; Sala de Produtos e Banheiro completam a T.", bold=True)
tabela(["Lançamento", "Fase R", "Fase S", "Fase T"],
 [["Estado anterior (QDL0–4)", "5 140", "4 400", "5 280"],
  ["L18 — Escritório", "+1 800", "—", "—"],
  ["L20 — Controle de Qualidade", "—", "+2 160", "—"],
  ["L19 — Sala de Produtos", "—", "—", "+360"],
  ["L21 — Banheiro", "—", "—", "+240"],
  ["QDGL fechado", "6 940", "6 560", "5 880"]],
 widths=[70, 30, 30, 30], aligns="lccc", total=True,
 fonte_nota="QD-ILUMINAÇÃO: QDL-BALANÇO TOTAL R23–R33 · QDL-BALANÇO POTENCIAS R281–R295 · PIE 03.")
eq([("t", "I(QDGL)  ="), ("f", "máx (6 940 · 6 560 · 5 880)", "220 V"), ("t", "= 31,6 A")],
   "o geral dimensiona pela fase mais cheia — por isso o balanceamento importa: cada VA fora da fase máxima é economia.")
prova("Balanço: aba QDL-BALANÇO TOTAL (a nota da célula R33 documenta a sua distribuição) · corrente do geral alimenta o capítulo 14.")

# ================= 14. ALIMENTADORES =================
chap("Capítulo 14", "Quadros VI — alimentadores", "127 m mudam tudo: a queda passa a mandar mais que a ampacidade.")
conceito("Alimentador é o fio do QDGL até cada QDL (e do transformador ao QDGL). Em bandeja perfurada (método 13, referência F), cabos unipolares EPR: fator de temperatura 0,87 e agrupamento 0,72 para 8 circuitos (Tabela 9.10, ref. 4).")
tabela(["Alimentador", "Sistema", "Ip", "L", "Seção que atende", "ΔV", "Disjuntor"],
 [["QDGL → QDL5", "220 V (R)", "8,18 A", "127 m", "6 mm² (1,5 mm² daria 12,7%)", "3,20%", "MDWH-C10"],
  ["QDGL → QDL6", "380 V (S+T)", "6,63 A", "127 m", "2,5 mm² (1,5 mm² daria 7,0%)", "3,57%", "MDWH-C10/2"],
  ["QDGL → QDL7", "220 V (T)", "1,09 A", "127 m", "1,5 mm² já atende", "1,69%", "MDWH-C10"],
  ["QDGBT → QDGL", "380/220 V", "31,6 A", "10 m", "10 mm² (mandou ampacidade)", "0,59%", "MDWH-C40 3P"]],
 widths=[34, 26, 18, 18, 48, 16, 26], aligns="llccccl", fs=8,
 fonte_nota="QD-ILUMINAÇÃO, aba QDGL: R22–R25, R60–R64 (127 m = estimativa da equipe, ajustar no DWG), R127–R134 (geral).")
p("Fechamento do geral: Ip' = 31,6 × 1,15 / 0,87 ≈ 41,7 A; Iz' = 74 × 0,87 = 64,4 A em 10 mm² EPR; 31,6 < 40 ≤ 64,4 — MDWH-C40 OK. Sinótico transformador → luminária: 0,6% + ~3,2% + ~2% ≈ 5,8% < 7%. Se a rota real for maior, a queda escala linearmente com o comprimento.", bold=True)
prova("Alimentadores: aba QDGL R60–R64 · gerenciais: R127–R134 · V/A.km: Prysmian pdf p. 61–62 · limite 7%: PIE 05 p. 14–19.")

# ================= 15. QDF =================
chap("Capítulo 15", "Quadros VII — tomadas e chuveiro", "QDF5/6/7 pela regra residencial da NBR 5410 (Tabela 9 do Prysmian).")
tabela(["Área", "Regra aplicada", "TUG", "TUE", "Quadro"],
 [["Escritório — 48,72 m²", "acima de 40 m²: 10 + 1 por 10 m² excedente", "11 / 2 200 VA", "1 climatizador", "QDF5"],
  ["Controle de Qualidade — 30 m²", "maior entre perímetro/3 e área/4", "8 / 1 600 VA", "1 climatizador", "QDF6"],
  ["Sala de Produtos — 30 m²", "mesma regra do CQ", "8 / 1 600 VA", "1 climatizador", "QDF6"],
  ["Banheiro — 18,3 m²", "1 TUG junto à pia (600 VA)", "1 / 600 VA", "2 × chuveiro 9 kW + DDR 30 mA", "QDF7"]],
 widths=[42, 54, 30, 38, 22], aligns="llccl", fs=8,
 fonte_nota="QD-ILUMINAÇÃO, aba QDF-TOMADAS-LUCAS A1:I25 (previsão R3–R6, circuitos R10–R17, gerais R21–R23) · Prysmian Tabela 9, pdf p. 48.")
eq([("t", "Ip(chuveiro)  ="), ("f", "9 000 W", "220 V"), ("t", "= 40,9 A   →   16 mm²   →   In 50 A")],
   "10 mm² daria Iz' = 57 × 0,79 = 45 A (< 50); o 16 mm² dá 76 × 0,79 = 60 A: 40,9 < 50 ≤ 60. Queda ≈ 0,8% em 15 m.")
p("Circuitos de TUG em 2,5 mm² com MDW-C10 (4 a 6 tomadas por circuito, FP ≈ 1, sem majorante). Disjuntores gerais propostos: QDF5 C25 · QDF6 C32 · QDF7 C100 (com um chuveiro só, cai para ~50 A — confirmar a quantidade no DWG).", bold=True)
prova("A aba QDF-TOMADAS-LUCAS inteira cabe numa tela: chuveiro nas linhas R16–R17, pendências na R25.")

# ================= 16. T2 =================
chap("Capítulo 16", "O que vem: T2", "Regime e transitório térmico — a temperatura do condutor do circuito especificado.")
p("O T2 fecha a física do fio que o T1 escolheu: com a seção definida (1,5 mm² nos terminais, 2,5 mm² no L20, alimentadores 6/2,5/1,5/10 mm²) e as correntes de projeto (Ip'), calcula-se o equilíbrio térmico em regime permanente e o transitório da partida, determinando a temperatura do condutor do circuito especificado — aula PIE 04 e Manual Prysmian.", bold=False)
tabela(["Insumo já pronto do T1", "Onde está", "Uso no T2"],
 [["Seções por ampacidade", "SEÇÃO CONDUTORES R21–R24", "resistência térmica do condutor"],
  ["Ip' por circuito", "QDL-FATOR R21–R24 (col. N)", "perda Joule I²R"],
  ["Fatores 0,79 / 0,87 / 0,72", "Prysmian pdf p. 57–58", "temperatura de regime"],
  ["Correntes de partida", "curva C · inrush do reator", "transitório térmico"]],
 widths=[56, 62, 58], aligns="lll", fs=8)
bul("Regra da aula de 27/08: sempre a condição mais crítica — potência vetorial P + jQ, pior fase do balanço.")
bul("Pendências que alimentam o T2: medir os 127 m no DWG, confirmar climatizadores e nº de chuveiros, revisar EPR/PVC dos QDL0–4.")
prova("PIE 04 p. 48–66 (ampacidade e térmica) · Prysmian pdf p. 53–62. Entrega T2 em 15/09 (plano de ensino).")

# ================= 17. PROVA =================
chap("Capítulo 17", "O índice da prova", "Fotografe esta página: informação → arquivo → onde clicar.")
tabela(["Quero…", "Abra…"],
 [["E 200/1500/200/750", "LUM-LUCAS → H22:J25 · B145:B148"],
  ["TMS 426 · 6 000 lm · 120 VA", "LUM-LUCAS → B60:B75 · B179:B185"],
  ["Refletâncias 50/50 · 70/35", "LUM-LUCAS → B82:H85"],
  ["K e Fu", "LUM-LUCAS → E103:H106"],
  ["Fdl 0,75", "LUM-LUCAS → B121"],
  ["Φt · N 3/18/2/15", "LUM-LUCAS → F145:H161"],
  ["Grades (CERTO)", "LUM-LUCAS → B167:J170"],
  ["Carga P/Q/S/I e E obtida", "LUM-LUCAS → C190:J200"],
  ["Ip dos circuitos", "QD-ILUM → QDL R21–R24, col. J"],
  ["Ip' e Iz'", "QD-ILUM → QDL-FATOR R21–R24, col. N/P"],
  ["Seção dos fios", "QD-ILUM → SEÇÃO R21–R24"],
  ["Disjuntores C10", "QD-ILUM → DISJUNTORES R21–R24 + WEG p. 3–5"],
  ["Queda < 4%", "QD-ILUM → QDL-QUEDA R392–R448, col. J"],
  ["Balanço de fases", "QD-ILUM → BALANÇO TOTAL R23–R33"],
  ["127 m e geral", "QD-ILUM → QDGL R60–R64 · R127–R134"],
  ["TUG/TUE e chuveiro", "QD-ILUM → QDF-TOMADAS-LUCAS R3–R23"],
  ["B1 17,5/24 A · f 0,79 · V/A.km", "Prysmian pdf p. 53 · 57 · 61–62"],
  ["Curva C e Icu", "WEG p. 3–5 · PIE 06 p. 27–41"],
  ["Enunciado e planta", "05-.../01-Dados Iniciais · 02-Plantas e DWG"]],
 widths=[62, 114], aligns="ll", fs=7.8)
h2("Glossário de bolso")
tabela(["Termo", "Em uma linha"],
 [["E · Φt · Fu · Fdl · K", "alvo de lux · luz a emitir · fração que pousa · desconto do tempo · forma da sala"],
  ["Nteo · N · grade", "quantidade teórica · teto instalado · desenho colunas × fileiras"],
  ["P · Q · S · I", "ativa · reativa · aparente (hipotenusa) · corrente S/220"],
  ["Ip · Ip' · Iz · Iz' · In", "que passa · corrigida · que a tabela dá · corrigida · disjuntor"],
  ["B1 · PVC · 2CC", "embutido na alvenaria · isolação 70 °C · fase + neutro carregados"],
  ["MDW-C10 · 5 kA · C", "minidisjuntor WEG 10 A · capacidade de curto · curva para reator"],
  ["4% · 7%", "queda máxima do terminal · do transformador à luminária"]],
 widths=[46, 130], aligns="ll", fs=8)
h2("Roteiro de 5 minutos (se pedir para apresentar)")
bul("Abra pelo enunciado: Lumens + Hpp 0,80. Depois DADOS L11–L14 e 120 VA por ponto.")
bul("E: peso soma 0 → médio, MAX contra a específica → 200 / 1 500 / 200 / 750. Aqui mora a diferença do projeto.")
bul("TMS 426: 6 000 lm · 104,1 W + j50,4 var · 120 VA. Refletâncias: bege 35% é pior caso declarado.")
bul("Hlp 2,20 → K → dois vizinhos de Fu → interpolação ao vivo → Fdl 0,75 → Φt → N 3/18/2/15 → total 38 e 4 560 VA.")
bul("Quadros: Ip → fio (1,5; L20 2,5) → C10 5 kA → queda < 4% → balanço R6 940/S6 560/T5 880 → 127 m → QDF e chuveiro 40,9 A.")
bul("Feche: sinótico 5,8% < 7% e as pendências do DWG.")
origem("Referências com página: Dados Iniciais 6 p. · PIE 02 (p. 60–75) · PIE 04 (p. 48–66) · PIE 05 (p. 14–45) · PIE 06 (p. 27–41) · Prysmian (pdf p. 53, 57, 61–62) · WEG Minidisjuntores (p. 3–7) · A1 P1 Tabelas Auxiliares (5 p.) · LUM-LUCAS A1:J219 · QD-ILUMINAÇÃO (9 abas) · RESPONSABILIDADES.xlsx.")
box("Pronto para entregar",
    "Copie as tabelas (E · K/Fu · N/E obtida · QDL · Ip/fio/disjuntor/queda) para o T1-MEMORIAL DE CALCULO.docx na ordem QDL5 → QDL6 → QDL7 → QDF. Leve este documento, a FINAL_REVISADA aberta (fórmulas à vista), a Tab. 2.9, o Prysmian nas páginas 53/57/61 e o WEG p. 3–5.",
    GREEN, GREEN_BG)

pdf.output(str(OUT))
print(f"OK: {OUT} ({OUT.stat().st_size/1024:.0f} kB)")
