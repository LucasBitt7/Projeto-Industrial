#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guia Lucas v2 — escuro elegante, fórmulas LaTeX em imagem, leitura humana."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fpdf import FPDF
from fpdf.fonts import FontFace
from fpdf.enums import TableCellFillMode

OUT = Path("/mnt/c/Users/lucas/Desktop/Engenharia/ProjetosIndustriais/T1_T2_LUCAS_Guia_Prova_v2.pdf")
EQDIR = Path("/tmp/opencode/eq_v2")
EQDIR.mkdir(parents=True, exist_ok=True)

# ---------- paleta elegante alto contraste ----------
NAVY = (15, 42, 68)        # cabeçalhos / títulos
NAVY2 = (24, 62, 96)
ORANGE = (198, 93, 0)      # acento
PAPER = (253, 250, 245)    # fundo página
INK = (17, 24, 39)         # texto
MUTED = (70, 80, 95)
LINE = (210, 200, 185)
GREEN_D = (22, 90, 60); GREEN_BG = (232, 245, 236)
AMBER_D = (130, 85, 5); AMBER_BG = (255, 248, 225)
PURPLE_D = (70, 45, 120); PURPLE_BG = (240, 235, 250)
RED_D = (150, 35, 30); RED_BG = (253, 232, 232)
BLUE_BG = (235, 240, 250)
ZEBRA = (244, 246, 250)

def render_eq(name, latex, fontsize=22):
    fp = EQDIR / f"{name}.png"
    plt.close("all")
    fig = plt.figure(figsize=(8, 1.6))
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.text(0.5, 0.5, f"${latex}$", fontsize=fontsize, ha="center", va="center", color="#111827")
    fig.savefig(fp, dpi=260, bbox_inches="tight", transparent=True, pad_inches=0.15)
    plt.close(fig)
    return str(fp)

EQS = {}
EQS["phi_util"] = render_eq("phi_util", r"\Phi_{util} = E \times S")
EQS["phi_t"] = render_eq("phi_t", r"\Phi_t = \frac{E \times S}{F_u \times F_{dl}}")
EQS["nlu"] = render_eq("nlu", r"N_{teo} = \frac{\Phi_t}{n \times \phi} \;\;\to\;\; N = \lceil N_{teo} \rceil")
EQS["eobt"] = render_eq("eobt", r"E_{obt} = \frac{N \times n \times \phi \times F_u \times F_{dl}}{S}")
EQS["hlp_k"] = render_eq("hlp_k", r"H_{lp}=3{,}00-0{,}80=2{,}20\,m \;\;\;\; K=\frac{L \times C}{H_{lp}\,(L+C)}")
EQS["fu_k"] = render_eq("fu_k", r"F_u = F_{inf} + \frac{K-K_{inf}}{K_{sup}-K_{inf}}\,(F_{sup}-F_{inf})")
EQS["fu_col"] = render_eq("fu_col", r"F_u(35\%) = F_{30\%} + \frac{35-30}{50-30}\,[F_{50\%}-F_{30\%}]")
EQS["pqs"] = render_eq("pqs", r"P=2\times40+24{,}1 \;\;\; Q=P\tan(\arccos 0{,}90) \;\;\; S=\sqrt{P^2+Q^2}")
EQS["ip"] = render_eq("ip", r"I_p = \frac{S}{220} = \frac{N \times 120}{220}")
EQS["ipp"] = render_eq("ipp", r"I_p^{\prime} = \frac{I_p \times 1{,}15}{0{,}79 \times 1{,}00} \;\;\;\; I_z^{\prime}=I_z \times 0{,}79")
EQS["prot"] = render_eq("prot", r"I_z^{\prime} > I_n > I_p \;\;\;\; I_{cu} \geq 5\,kA")
EQS["dv"] = render_eq("dv", r"\Delta V = 2\,I_p\,L\,(R\cos\varphi + X\sin\varphi) \;\;\; \Delta V\%=\frac{\Delta V}{220}\,100")
EQS["fmax"] = render_eq("fmax", r"I_{QDGL}=\frac{\max(6940,\,6560,\,5880)}{220}=31{,}6\,A")
EQS["chuv"] = render_eq("chuv", r"I_p=\frac{9000}{220}=40{,}9\,A \;\;\; 40{,}9<50\leq 60")

class PDF(FPDF):
    def multi_cell(self, w, h=None, text="", border=0, align="J", fill=False, **kw):
        kw.setdefault("new_x", "LMARGIN"); kw.setdefault("new_y", "NEXT")
        return super().multi_cell(w, h, text, border, align, fill, **kw)
    def header(self):
        if self.page_no() == 1: return
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 11, "F")
        self.set_xy(14, 2.5)
        self.set_font("Sans", "B", 7)
        self.set_text_color(255, 255, 255)
        self.cell(0, 4, "PARTE DO LUCAS  •  LUMINOTÉCNICO + QDL/QDGL/QDF  •  DO ZERO À PROVA")
        self.set_xy(-14-28, 2.5)
        self.set_font("Sans", "", 7)
        self.cell(28, 4, f"{self.page_no()}/{{nb}}", align="R")
        self.set_xy(self.l_margin, 13)
    def footer(self):
        self.set_y(-10)
        self.set_draw_color(*ORANGE)
        self.set_line_width(0.6)
        self.line(14, self.get_y(), 196, self.get_y())
        self.set_font("Serif", "", 6.5)
        self.set_text_color(*MUTED)
        chap = getattr(self, "_chap", "")
        self.cell(0, 5, chap[:110], align="C")

pdf = PDF(orientation="P", unit="mm", format="A4")
pdf.alias_nb_pages("{nb}")
pdf.set_auto_page_break(True, margin=14)
pdf.set_margins(17, 15, 17)
pdf.add_font("Sans", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pdf.add_font("Sans", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
pdf.add_font("Serif", "", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
pdf.add_font("Serif", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
pdf.add_font("Mono", "", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
pdf.set_page_background(PAPER)

def need(h):
    if pdf.get_y() + h > 283:
        pdf.add_page()

def chap(num, titulo, subt="", nova=True, meta=""):
    if nova: pdf.add_page()
    else: pdf.ln(4)
    pdf._chap = f"{num}  {titulo}"
    y0 = pdf.get_y()
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Sans", "B", 12)
    pdf.multi_cell(0, 9, f"  {num}  —  {titulo}", fill=True)
    # filete laranja
    pdf.set_fill_color(*ORANGE)
    pdf.rect(17, pdf.get_y(), 176, 1.6, "F")
    pdf.ln(2)
    if subt:
        pdf.set_font("Serif", "", 9.5)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(0, 5.4, subt)
        pdf.ln(1)
    if meta:
        pdf.set_font("Sans", "B", 7.5)
        pdf.set_text_color(*ORANGE)
        pdf.multi_cell(0, 4.6, meta)
        pdf.ln(1)

def h2(t):
    need(14)
    pdf.set_font("Sans", "B", 10)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 6, t)
    pdf.set_draw_color(*LINE)
    pdf.set_line_width(0.3)
    pdf.line(17, pdf.get_y(), 90, pdf.get_y())
    pdf.ln(2)

def p(t, bold=False, size=10):
    pdf.set_font("Serif", "B" if bold else "", size)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 6, t)
    pdf.ln(1)

def bul(t, size=9.5):
    need(12)
    x = pdf.l_margin
    pdf.set_font("Sans", "B", size)
    pdf.set_text_color(*ORANGE)
    pdf.set_x(x)
    pdf.cell(6, 6, "▸")
    pdf.set_font("Serif", "", size)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 6, t)
    pdf.ln(0.5)

def caixa(titulo, texto, dark, bg):
    need(22)
    # título escuro alto contraste
    pdf.set_fill_color(*dark)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Sans", "B", 8.5)
    pdf.multi_cell(0, 6.5, f"  {titulo}", fill=True)
    pdf.set_fill_color(*bg)
    pdf.set_draw_color(*dark)
    pdf.set_text_color(*INK)
    pdf.set_font("Serif", "", 9.3)
    # corpo com borda fina + barra lateral grossa simulada pelo título já escuro
    pdf.multi_cell(0, 5.8, texto, border=1, fill=True)
    pdf.ln(2.5)

def concetto(t): caixa("►  CONCEITO — o que é", t, NAVY, BLUE_BG)
def origem(t): caixa("◎  ORIGEM — arquivo + página + célula", t, GREEN_D, GREEN_BG)
def porque(t): caixa("?  POR QUÊ — por que assim", t, AMBER_D, AMBER_BG)
def prova(t): caixa("»  NA PROVA — ache em 30 s", t, PURPLE_D, PURPLE_BG)
def alerta(t): caixa("!  ERRO QUE REPROVA", t, RED_D, RED_BG)

EQN = [0]
def eq(name, leia, exemplo=None, larg=132):
    EQN[0] += 1
    need(34)
    pdf.set_font("Sans", "B", 8)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 5, f"Eq. {EQN[0]}")
    # imagem centralizada
    x = (210 - larg) / 2
    y = pdf.get_y()
    pdf.image(EQS[name], x=x, y=y, w=larg)
    # estima altura: usa 14mm padrão
    pdf.set_y(y + 15)
    pdf.set_font("Serif", "", 8.8)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(0, 5, f"Leia assim: {leia}")
    if exemplo:
        pdf.set_font("Serif", "B", 9)
        pdf.set_text_color(*INK)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(*LINE)
        pdf.multi_cell(0, 5.6, exemplo, border=1, fill=True)
    pdf.ln(2)

def tabela(headers, rows, widths=None, fs=8.3, num_cols=None, highlight_last=False, total_last=False):
    need(20)
    if widths is None:
        widths = [(176)/len(headers)]*len(headers)
    # header escuro
    st = FontFace(emphasis="BOLD", color=(255,255,255), fill_color=NAVY)
    pdf.set_font("Serif", "", fs)
    # alinha: primeira col esquerda, numéricas direita — fpdf table é global; usamos CENTER p/ numéricas e JUSTIFY se texto longo
    align = "CENTER"
    if any(len(str(c)) > 28 for r in rows for c in r):
        align = "CENTER"
    with pdf.table(col_widths=widths, text_align=align, line_height=6,
                   first_row_as_headings=True, headings_style=st,
                   cell_fill_color=ZEBRA, cell_fill_mode=TableCellFillMode.ROWS,
                   width=176) as t:
        t.row(headers)
        for i, r in enumerate(rows):
            # última linha total em negrito via maiúsculas? fpdf não bolda célula isolada; marcamos com ★
            t.row([str(c) for c in r])
    pdf.ln(1.5)

# ================= CAPA =================
pdf.add_page()
pdf.ln(14)
pdf.set_font("Sans", "B", 9)
pdf.set_text_color(*ORANGE)
pdf.multi_cell(0, 6, "RECAPADORA DE PNEUS  •  EEL 2026-2  •  T1 + T2  •  PARTE DO LUCAS", align="C")
pdf.set_font("Serif", "B", 34)
pdf.set_text_color(*NAVY)
pdf.multi_cell(0, 13, "Do zero à prova", align="C")
pdf.set_font("Serif", "", 14)
pdf.set_text_color(*MUTED)
pdf.multi_cell(0, 8, "Luminotécnico + Quadros QDL • QDGL • QDF", align="C")
pdf.ln(2)
pdf.set_fill_color(*NAVY)
pdf.set_text_color(255,255,255)
pdf.set_font("Sans", "B", 10)
pdf.multi_cell(0, 8, "Sala de Produtos  •  Controle de Qualidade  •  Banheiro  •  Escritório", fill=True, align="C")
pdf.set_fill_color(*ORANGE)
pdf.rect(17, pdf.get_y(), 176, 1.8, "F")
pdf.ln(4)
pdf.set_fill_color(255,255,255)
pdf.set_draw_color(*NAVY)
pdf.set_font("Serif", "B", 11)
pdf.set_text_color(*NAVY)
pdf.multi_cell(0, 7, "38 pontos TMS 426  •  3 956 W  •  4 560 VA  •  L18–L21 com MDW-C10", border=1, fill=True, align="C")
pdf.ln(3)
pdf.set_font("Serif", "", 10)
pdf.set_text_color(*INK)
pdf.multi_cell(0, 6.2, "Este guia conta a história completa da sua parte: quanta luz cada sala precisa, quantas lumináriasicipated isso dá, que fio e disjuntor aguentam, e onde cada número mora na planilha e no catálogo. Sem jargão solto: cada termo é explicado, cada escolha é justificada, cada tabela diz o caminho da prova.")
pdf.ln(2)
caixa("COMO LER (2 min)", "Ordem importa: capítulos 0→3 contam a base; 4→11 fazem a luz; 12→21 fazem os quadros; 22 é o índice fotográfico da prova. Caixas escuras = alto contraste de propósito. Equações são imagens nítidas (Eq. 1, 2...) com 'leia assim' embaixo.", NAVY, BLUE_BG)

# ================= COMO USAR + SUMÁRIO =================
chap("Guia", "Como usar + sumário", "Cinco caixas, um padrão. Decore as cores uma vez.", nova=True)
tabela(["Caixa", "Quando usar"], [["► CONCEITO (marinho)", "Não sei o que o termo significa"], ["◎ ORIGEM (verde)", "Quero provar de onde tirei"], ["? POR QUÊ (âmbar)", "Quero justificar contra alternativa"], [">> PROVA (roxa)", "Quero abrir rápido na hora"], ["! ERRO (vermelha)", "Quero não perder ponto bobo"]], widths=[62,114], fs=8.5)
h2("Sumário — a história em 1 linha por capítulo")
for s in ["0. Sua parte: 4 salas → QDL5/6/7 L18–L21 e os 4 arquivos que provam tudo", "1. Enunciado: as 4 frases que mandam em tudo (método, altura, curto, Prysmian)", "2–3. Luz sem mistério: grandezas + 4 passos dos Lumens", "4. Medidas reais + K: 30 / 30 / 18,3 / 48,7 m² e K 1,24 / 0,95 / 1,57", "5. E 200 / 1500 / 200 / 750: peso 0 + MAX (a virada do projeto)", "6–7. TMS 426 6000 lm + reflet 50/50, 70/50, 70/35 bege crítico", "8–9. Fu interpolado + Fdl 0,75 → fluxo → 3 / 18 / 2 / 15", "10–11. Grades na planta + carga P+jQ + E obtida (folga do CQ!) + total 4560 VA", "12–16. Quadros I: Ip → fio → disjuntor (a espinha T1→T2)", "17–18. Quadros II: queda trecho a trecho < 4% (o cálculo mais temido, destrinchado)", "19–21. Balanço, alimentador 127 m, QDF/chuveiro + índice fotográfico + entrega"]:
    bul(s, size=9)

# ================= 0+1 =================
chap("0–1. O terreno", "Sua parte + enunciado: o contrato do projeto", "DADOS L11–L14  •  Dados Iniciais 6p", nova=True)
concetto("Você entrega luz + fio + proteção de 4 salas. SP e CQ dividem o QDL6 mas com circuitos próprios (L19/L20). Escritório é QDL5/L18. Banheiro é QDL7/L21.")
tabela(["Sua sala", "Medida", "Circuito → QDL"], [["Sala de Produtos", "5×6 m", "L19 (3 lum) → QDL6"], ["Controle de Qualidade", "5×6 m", "L20 (18 lum) → QDL6"], ["Banheiro", "5,23×3,5 m", "L21 (2 lum) → QDL7"], ["Escritório", "8,12×6 m", "L18 (15 lum) → QDL5"]], widths=[62,44,70])
origem("Responsáveis: RESPONSABILIDADES.xlsx  •  Medidas: PROJETO INDUSTRIAIS TRABALHO.xlsx DADOS L11–L14  •  Luz: LUM-LUCAS_FINAL_REVISADA.xlsx LUM-LUCAS  •  Fio: QD-ILUMINAÇÃO.xlsx (QDL R21–R24, QDGL R22–R25, QDF R3–R6).")
h2("As 4 frases do enunciado que decidem tudo")
bul("Método Lumens nas suas áreas; Recapagem é Cavidades (não é sua).", 9.3)
bul("Hpp 0,80 m em todas → com pé-direito 3,00 → Hlp 2,20 m.", 9.3)
bul("BT 380/220 V, 1200 m, 45 °C; curto 5 kA nos QDL/QDF.", 9.3)
bul("Fio e queda pelo Prysmian (V/A.km, formulação completa); TUG/TUE pela NBR 5410.", 9.3)
porque("Altitude não mexe em fio BT; 45 °C sim (×0,79). 5 kA escolhe o Icu. 127 m do alimentador é estimativa: medir no DWG.")
prova("Enunciado: 05-.../01-Dados Iniciais/*.pdf  •  DWG: .../02-Plantas/*.dwg  •  T1-T4: 00-.../Plano de Ensino.pdf")

# ================= 2+3 =================
chap("2–3. Luz sem mistério", "PIE 02 p39–75: o que cada letra quer dizer", "Leia devagar: tudo depois é repetição disso.", nova=True)
concetto("Φ (lm) sai da lâmpada. E (lux) chega por m². Fu perde na parede. Fdl perde na sujeira. K diz se a sala ajuda ou atrapalha. Lâmpada=tubo; luminária=conjunto; reator=caixinha que gasta 24 W e cria Q.")
tabela(["Símbolo", "Nome", "Pense assim"], [["Φ", "Fluxo (lm)", "Água que sai da torneira"], ["E", "Iluminância (lux)", "Água por m² do balde"], ["Fu / Fdl / K", "Perdas + forma", "Espírro + sujeira + formato do balde"]], widths=[30,60,86])
h2("Os 4 passos (toda conta nasce aqui)")
eq("phi_util", "fi-útil igual a E vezes S: quanta luz precisa POUSAR no plano.")
eq("phi_t", "fi-total igual a E vezes S dividido por Fu vezes Fdl: quanto precisa SAIR das lâmpadas (perdas entram dividindo).")
eq("nlu", "N teórico igual a fi-total dividido por 6000; N instalado é o teto (sempre para cima). 1 lum = 2×3000 lm.")
eq("eobt", "E obtida usa o N instalado: tem que dar maior ou igual ao alvo. É a prova dos nove.")
alerta("Φt (emitir) ≠ Φútil (chegar). Nteo (2,73) ≠ N (3). Quem troca reprova a verificação.")
origem("PIE 02: p39–41 grandezas, p60–62 E, p64–68 Fu/K, p67 interpolação, p69–70 Fdl, p73 fluxo/N, p74 X,Y≤1,5Hlp, p75 reator. Tabs Mamede 2.4/2.5/2.6/2.9/2.10.")

# ================= 4+5 =================
chap("4–5. Medidas e alvo E", "DADOS + peso + MAX: a virada 1500/750", "S + Hlp + K, depois a etapa que mais reprova.", nova=True)
tabela(["Sala", "L×C → S", "Hlp", "K"], [["SP", "5×6 → 30,00", "2,20", "1,2397"], ["CQ", "5×6 → 30,00", "2,20", "1,2397"], ["Banh", "5,23×3,5 → 18,305", "2,20", "0,9531"], ["Esc", "8,12×6 → 48,72", "2,20", "1,5684"]], widths=[44,48,30,54])
eq("hlp_k", "H útil igual a 3 menos 0,8. K igual a área dividida por H vezes perímetro-meio. Banheiro K pequeno = sala 'alta' = Fu menor.")
h2("E: peso soma 0 → médio, depois MAX")
p("Idade 41 + importante + fundo 0,40 → pesos 0+0+0 = 0 → usa o MÉDIO da faixa. Depois compara com a específica e fica com o MAIOR.", bold=True)
tabela(["Sala", "Faixa (médio)", "Específica", "Fica"], [["SP depósito A", "100-150-200 → 150", "200", "200"], ["CQ inspeção B", "1000-1500-2000 → 1500", "500", "1500"], ["Banh curta A", "50-75-100 → 75", "200", "200"], ["Esc B", "500-750-1000 → 750", "250", "750"]], widths=[44,52,40,40])
porque("Versões antigas usavam 500/250 (só específica) e subdimensionavam 3×. A faixa já pesa a tarefa; MAX é a regra mais crítica da aula 27/08.")
origem("Peso R13–R17, faixas R20–R25, MAX J22:J25 e B145:B148. PIE 02 p60–62, Tabs 2.5/2.6.")
prova("E: LUM-LUCAS H22:J25. Leve Tabs 2.5/2.6 impressas; some pesos na hora.")

# ================= 6+7 =================
chap("6–7. Lâmpada e parede", "TMS 426 + reflet: o que ajuda a luz render", nova=True)
concetto("TMS 426 = carcaça para 2 tubos de 40 W. Tubo = 3000 lm → ponto = 6000 lm. Reator duplo 220 V perde 24,1 W, FP 0,90 (indutivo: cria Q). Parede clara devolve luz (Fu sobe); escura engole (Fu desce).")
tabela(["Peça", "Valor", "Fonte"], [["Tubo", "40 W 3000 lm", "Tab 2.1"], ["Ponto", "6000 lm", "2×3000"], ["Reator", "24,1 W FP 0,90", "Tab reatores"], ["1 lum", "104,1 W + j50,4 → 120 VA", "B179:B185"]], widths=[40,60,76])
eq("pqs", "P soma tubos mais reator. Q é P vezes tangente do arco-cosseno de 0,9. S é a hipotenusa. Adota 120 VA por ponto (inteiro + margem).")
tabela(["Sala", "DADO", "Usa", "Por quê"], [["SP", "CLARO/CLARA", "50/50", "Qualitativo → coluna clara"], ["CQ", "BRANCO/BRANCA", "70/50", "80% não existe → limite 70%"], ["Banh", "CLARO/CLARA", "50/50", "Igual SP"], ["Esc", "BRANCO/BEGE", "70/35", "Bege 35% crítico, interpola"]], widths=[30,44,30,72])
porque("TMS não é única, mas é a única com Fu + elétrico juntos → rastreável. LED exigiria trocar tudo por datasheet. Bege 35% é pior caso; 45% faria Esc 15→14.")
origem("LUM-LUCAS B60:B75, B82:H85 (piso fixo 10%, azulejo registrado). Tab reflet + Tab 2.9/2.10. PIE 02 p63/p75.")

# ================= 8+9 =================
chap("8–9. Fu → fluxo → N", "Interpolação aberta + 3/18/2/15", "O coração numérico, sem pular linha.", nova=True)
eq("fu_k", "Fu entre dois vizinhos de K: parte do de baixo mais a fração do caminho vezes o degrau.")
eq("fu_col", "Escritório: depois de interpolar em K nas duas colunas, interpola entre parede 30% e 50% no ponto 35%.")
tabela(["Sala", "Vizinhos Tab 2.9", "Fu"], [["SP 50/50 K1,24", "1,00→0,44 / 1,25→0,49", "0,4879"], ["CQ 70/50 K1,24", "1,00→0,50 / 1,25→0,56", "0,5575"], ["Banh K0,95", "0,80→0,38 / 1,00→0,44", "0,4259"], ["Esc K1,57 dupla", "1,5→0,54/0,61 2,0→0,61/0,68", "0,5671"]], widths=[40,66,70])
p("Esc aberta: Fu30% = 0,5496; Fu50% = 0,6196; Fu35% = 0,5496 + 0,25×0,07 = 0,5671.", bold=True)
h2("Fluxo e quantidade (Fdl 0,75 comercial)")
tabela(["Sala", "Φt [lm]", "Nteo → N"], [["SP 200×30", "16 396", "2,73 → 3 (3×1)"], ["CQ 1500×30", "107 619", "17,94 → 18 (6×3)"], ["Banh 200×18,3", "11 461", "1,91 → 2 (1×2)"], ["Esc 750×48,7", "85 915", "14,32 → 15 (3×5)"]], widths=[44,52,80])
porque("ROUNDUP sempre: 2 na SP dariam 146 lux. Fdl 0,70 (+7%) pegaria o CQ primeiro (folga 0,4%).")
origem("Fu H103:H106, Fdl B121, Φt F145:F148, N E158:H161. PIE 02 p67–73.")

# ================= 10+11 =================
chap("10–11. Planta e carga", "Grade 3,30 m + P+jQ + folgas", nova=True)
p("Regra CAD: X,Y ≤ 1,5×2,20 = 3,30 m; bordas X1=X/2. Quantidade é mínimo normativo; obstáculo pode pedir +1 (aí recalcula Eobt).", bold=True)
tabela(["Sala", "Grade", "X/X1 • Y/Y1", "OK"], [["SP 5×6", "3×1=3", "2,00/1,00 • —/2,50", "SIM"], ["CQ 5×6", "6×3=18", "1,00/0,50 • 1,67/0,83", "SIM"], ["Banh", "1×2=2", "—/1,75 • 2,62/1,31", "SIM"], ["Esc", "3×5=15", "2,00/1,00 • 1,62/0,81", "SIM"]], widths=[34,30,72,40])
tabela(["Sala", "N", "P / Q / S", "I", "Eobt"], [["SP", "3", "312 W / 151 / 360", "1,64", "219 ≥200"], ["CQ", "18", "1874 / 908 / 2160", "9,82", "1505 ≥1500!"], ["Banh", "2", "208 / 101 / 240", "1,09", "209 ≥200"], ["Esc", "15", "1562 / 756 / 1800", "8,18", "786 ≥750"]], widths=[28,18,56,28,46])
alerta("CQ folga +0,4%: cite como ponto de atenção. É normal (17,94→18) mas qualquer revisão de Fdl/fluxo mexe nele.")
origem("Grades B167:J170 (J=CERTO). Carga B179:B185, C190:J193, QDL C197:G200: QDL5 15/1800, QDL6 21/2520, QDL7 2/240, total 38/3956W/4560VA.")
prova("Eobt = LUM-LUCAS col J190:J193. Total C197:G200.")

# ================= 12-14 ponte+Ip+fio =================
chap("12–14. Quadros I", "De lúmens a ampères: Ip → fio", "A ponte é 120 VA em 220 V. Ordem das abas = ordem da prova.", nova=True)
concetto("Ip = o que vai passar. Iz = o que o fio aguenta a 30 °C. Iz' = com calor real. Ip' = Ip trazida p/ comparar. In = disjuntor de prateleira.")
tabela(["Regra QDL", "Valor", "Fonte prova"], [["Tensão / temp", "220 V / 45 °C → 0,79 PVC", "Dados p1 + Prysmian pdfp57"], ["Curto / método", "5 kA / método 7→B1 PVC", "Dados p3 / M3-Q71 / PIE04 p58"], ["Ponto / harmônico", "120 VA / ×1,15", "T1 + PIE04"], ["Limite queda", "4% terminal / 7% total", "PIE05 p14–19"]], widths=[52,54,70])
eq("ip", "Ip igual a demanda sobre 220: N vezes 120 sobre 220.")
tabela(["Circ", "Sala", "N→VA", "Ip → fase"], [["L18 QDL5", "Esc", "15→1800", "8,18 → R"], ["L19 QDL6", "SP", "3→360", "1,64 → T"], ["L20 QDL6", "CQ", "18→2160", "9,82 → S"], ["L21 QDL7", "Banh", "2→240", "1,09 → T"]], widths=[32,40,44,60])
eq("ipp", "Ip-linha compara com Iz-linha: multiplica harmônico e divide pelos fatores. L20 9,82→14,29 estoura 1,5 (13,83) → vai p/ 2,5 (18,96).")
tabela(["Circ", "Ip'", "Fio (F+N+PE)"], [["L18 8,18", "11,91 ≤13,83", "1,5 / 1,5 / 1,5"], ["L19 1,64", "2,38", "1,5"], ["L20 9,82", "14,29 → 2,5", "2,5 / 2,5 / 2,5"], ["L21 1,09", "1,59", "1,5"]], widths=[44,56,76])
p("Neutro = fase (descarga com harmônico, NBR 5410 / PIE 05). 2 carregados. EPR anotado nos QDL0-4 com Iz de PVC: nas suas linhas PVC consistente.", bold=True)

# ================= 15-16 disjuntor =================
chap("15–16. Quadros II", "Disjuntor: Iz' > In > Ip", "MDW-C10 5 kA curva C.", nova=True)
eq("prot", "Disjuntor entre fio e carga, com Icu do curto presumido. Curva C segura o tranco do reator.")
tabela(["Circ", "Iz' > In > Ip", "WEG"], [["L18", "13,83 > 10 > 8,18", "MDW-C10 5 kA"], ["L19", "13,83 > 10 > 1,64", "MDW-C10"], ["L20", "18,96 > 10 > 9,82", "MDW-C10"], ["L21", "13,83 > 10 > 1,09", "MDW-C10"]], widths=[30,62,84])
origem("QDL R21–R24, FATOR R21–R24, SEÇÃO R21–R24, DISJ R21–R24. Prysmian pdfp53 (17,5/24 A). WEG p3 (curva C) p5 (5 kA). PIE 04/06.")
prova("Ip: QDL col J. Ip'/Iz': FATOR N/P. Seção: SEÇÃO J/L. In: DISJ E.")

# ================= 17+18 =================
chap("17–18. Queda destrinchada", "O cálculo mais temido, passo a passo", "Fio tem R+X: corrente × impedância × comprimento.", nova=False)
eq("dv", "Queda igual a 2 vezes Ip vezes L vezes (R cosseno mais X seno). Porcentagem sobre 220. L soma reto + 1,5 m por curva + subida 1,5 m.")
p("L18 (15 pts, 1,5 mm² R14,81/X0,14): começa com 15 lum (8,18 A) e vai esvaziando até 1 (0,55 A). Soma dá 2,33% < 4%. L20 (18 pts, 2,5 mm²) dá 1,50%. L19 dá 0,20%. L21 dá 0,12%. Rotas pela grade: medir no DWG.", bold=True)
tabela(["Circ", "Fio", "Perfil", "Acumulado"], [["L18 Esc", "1,5", "15 trechos QDL5-LU1…LU14-15*", "2,33% OK"], ["L20 CQ", "2,5", "18 trechos", "1,50% OK"], ["L19 SP", "1,5", "3 trechos", "0,20% OK"], ["L21 Banh", "1,5", "2 trechos", "0,12% OK"]], widths=[30,24,72,50])
origem("QD-QUEDA R392–R448 (R392 L18, R412 L19, R420 L20, R443 L21, R448 nota ESTIMADA). R/X seq. positiva Prysmian pdfp61–62. PIE 05 p24–30.")
prova("Queda: QD-QUEDA col I/J. R/X no cabeçalho do bloco.")

# ================= 19-21 =================
chap("19–21. Fechamento", "Balanço + 127 m + tomadas", nova=True)
p("Time tinha R5140/S4400/T5280. Você joga CQ 2160 na fase vazia S, Esc 1800 na R, SP+Banh na T → R6940/S6560/T5880.", bold=True)
eq("fmax", "Corrente do geral é a fase mais cheia sobre 220: base do QDGL.")
tabela(["Alimentador", "L / fio", "ΔV", "Disjuntor"], [["QDGL-QDL5 (R)", "127 m 6 mm² (1,5 daria 12,7%!)", "3,20%", "MDWH-C10"], ["QDGL-QDL6 (S+T)", "127 m 2,5 (1,5 daria 7%!)", "3,57%", "MDWH-C10/2"], ["QDGL-QDL7 (T)", "127 m 1,5", "1,69%", "MDWH-C10"], ["QDGBT-QDGL", "10 m 10 mm²", "0,59%", "MDWH-C40"]], widths=[48,62,30,36])
p("Sinótico trafo→lum ≈ 0,6 + 3,2 + 2 ≈ 5,8% < 7%. QGDL: 31,6→41,7 A, Iz' 64,4 A, 31,6<40≤64,4 OK. 127 m é estimativa: ΔV escala com L.", bold=True)
tabela(["Área", "TUG (NBR Tab 9)", "TUE"], [["Esc 48,7 m²", "11 / 2200 VA → QDF5", "1 climatizador"], ["CQ+SP 30 m²", "8+8 / 1600 → QDF6", "2 climatizadores"], ["Banh 18,3", "1 / 600 → QDF7", "2×9 kW + DDR"]], widths=[40,62,74])
eq("chuv", "Chuveiro pede 40,9 A: 10 mm² dá 45 A (<50) → 16 mm² dá 60 A → C50. TUG 2,5 mm² C10; gerais C25/C32/C100.")
origem("QDGL R22–R25/R60–R64/R127–R134. QDF A1:I25 (R3–R6, R10–R17, R21–R23). Prysmian Tab 9 pdfp48. ΔV escala linear.")
prova("Balanço: BALANÇO TOTAL R23–R33. Alimentador: QDGL R60–R64. QDF: aba inteira numa tela.")

# ================= 22+23 =================
chap("22–23. Prova e entrega", "Índice fotográfico + glossário + checklist", "Fotografe as duas tabelas abaixo.", nova=True)
tabela(["Quero…", "Abra…"], [["E / TMS / reflet / K-Fu / Fdl / Φt-N / grade / carga", "LUM-LUCAS H22:J25, B60:B75, B82:H85, E103:H106, B121, F145:H161, B167:J170, C190:J200"], ["Ip / fio / C10 / queda / balanço / 127 m / QDF", "QD-ILUM QDL R21–R24, FATOR+SEÇÃO, DISJ, QUEDA R392–R448, BALANÇO R23–R33, QDGL R60–R64, QDF A1:I25"], ["B1 17,5/24A / 0,79 / V/A.km / curva C", "Prysmian pdfp53/57/61 + PIE 04 p58 / PIE 05 p24 / WEG p3–5"]], widths=[62,114], fs=8)
tabela(["Falo…", "Em 1 linha"], [["E / Φt / Fu-Fdl-K", "Alvo / o que emitir / perdas + forma"], ["N / grade / Eobt", "Teto instalado / desenho / prova ≥ alvo"], ["Ip/Ip'/Iz'/In / ΔV", "Passa / compara / aguenta / protege / cai no fio"], ["B1-PVC-2CC / C10-5kA-C / 4-7%", "Onde vai / quem protege / limite"]], widths=[62,114], fs=8.5)
h2("Checklist de 5 min + pendências")
for s in ["1 Lumens+Hpp 0,8 → 2 DADOS+120VA → 3 peso+MAX 1500/750 → 4 TMS+bege 35% → 5 K+Fu ao vivo → 6 Fdl+Φt→N 38/4560VA → 7 Ip→fio→C10→queda→balanço→127m→QDF → 8 sinótico <7%.", "Diga antes: bege 35% pior caso • piso 10% limitação • 127 m medir no DWG • climatizador/chuveiros a confirmar • EPR/PVC QDL0-4 revisar."]:
    bul(s, size=9)
origem("Refs: Dados 6p • PIE 02 105p p60–75 • PIE 04 p48–66 • PIE 05 p14–45 • PIE 06 p27–41 • Prysmian 73p • WEG 20p p3–7 • A1 P1 5p • LUM A1:J219 • QD-ILUM 9 abas • DADOS L11–L14.")
caixa("✔  ENTREGA", "Copie E, K/Fu, N/Eobt, QDL + Ip/fio/C10/queda para o T1-MEMORIAL na ordem QDL5→QDL6→QDL7→QDF. Leve este guia + FINAL_REVISADA (fórmulas) + Tab 2.9 + Prysmian pdfp53/57/61 + WEG p3–5.", GREEN_D, GREEN_BG)

pdf.output(str(OUT))
print(f"OK: {OUT} ({OUT.stat().st_size/1024:.0f} kB)")
