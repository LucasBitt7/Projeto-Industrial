from math import sin, acos
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "QDL_QDGL_QDF_LUCAS_Passo_a_Passo.pdf"

SINPHI = sin(acos(0.90))
RX = {1.5: (14.8137e-3, 0.1378e-3, 23), 2.5: (8.8882e-3, 0.1345e-3, 14),
      6.0: (3.7035e-3, 0.1225e-3, None), 10.0: (2.2221e-3, 0.1207e-3, None)}
UNIT = 120  # VA por luminaria (TMS426 2x40W + reator)


def add_text(ax, text, y, size=11, color="#222222", bold=False, width=108, line_gap=0.042, x=0.01):
    from textwrap import fill
    wrapped = fill(text, width=width)
    ax.text(x, y, wrapped, fontsize=size, color=color, fontweight="bold" if bold else "normal", va="top", ha="left")
    return y - line_gap * (wrapped.count("\n") + 1)


def add_quote(ax, quote, source, y, x=0.01, width=104):
    y = add_text(ax, f'"{quote}"', y, size=10.5, color="#1F4E78", width=width, line_gap=0.038, x=x)
    y = add_text(ax, f"Fonte: {source}", y, size=9, color="#666666", width=width, line_gap=0.032, x=x)
    return y - 0.015


def add_equations(ax, equations, y, x=0.045, size=15):
    for equation in equations:
        ax.text(x, y, f"${equation}$", fontsize=size, va="top", color="#111111")
        y -= 0.062
    return y


def add_table(ax, headers, rows, bbox, fontsize=9):
    table = ax.table(cellText=rows, colLabels=headers, bbox=bbox, cellLoc="center", loc="upper left")
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#B7C9D6")
        cell.get_text().set_wrap(True)
        if row == 0:
            cell.set_facecolor("#1F4E78")
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
    return table


def new_page(pdf, title, subtitle=None):
    fig = plt.figure(figsize=(11.69, 8.27))
    ax = fig.add_axes([0.065, 0.06, 0.87, 0.88])
    ax.axis("off")
    ax.text(0, 1.0, title, fontsize=22, color="#1F4E78", fontweight="bold", va="top")
    if subtitle:
        ax.text(0, 0.935, subtitle, fontsize=11, color="#666666", va="top")
    return fig, ax


def save(pdf, fig):
    pdf.savefig(fig)
    plt.close(fig)


# ---------- rotas ----------
def rota_18():
    tr = [("QDL5-LU1", 15, 3.0, 2, 1.5)]
    k = 14
    for f in range(3):
        for c in range(4):
            tr.append((f"LU{f*5+c+1}-LU{f*5+c+2}", k, 1.62, 1 if c == 0 else 0, 0)); k -= 1
        if f < 2:
            tr.append((f"LU{f*5+5}-LU{f*5+6}", k, 2.0, 1, 0)); k -= 1
    tr[-1] = (tr[-1][0] + "*", *tr[-1][1:])
    return tr


def rota_20():
    tr = [("QDL6-LU1", 18, 3.0, 2, 1.5)]
    k = 17
    for f in range(3):
        for c in range(5):
            tr.append((f"LU{f*6+c+1}-LU{f*6+c+2}", k, 1.0, 1 if c == 0 else 0, 0)); k -= 1
        if f < 2:
            tr.append((f"LU{f*6+6}-LU{f*6+7}", k, 1.67, 1, 0)); k -= 1
    tr[-1] = (tr[-1][0] + "*", *tr[-1][1:])
    return tr


def trechos_qt(trechos, sec, unit=UNIT, v=220.0):
    r, x = RX[sec][0], RX[sec][1]
    out, acc = [], 0.0
    for nome, k, L, cv, sb in trechos:
        Ltot = L + cv * 1.5 + sb
        i = k * unit / v
        dv = 2 * i * Ltot * (r * 0.90 + x * SINPHI)
        pct = dv / v * 100
        acc += pct
        out.append((nome, k, round(L, 2), cv, sb, round(Ltot, 2), round(i, 2), round(dv, 3), round(pct, 3), round(acc, 3)))
    return out


def main():
    with PdfPages(PDF_PATH) as pdf:
        # ---------------- capa ----------------
        fig, ax = new_page(pdf, "Quadros QDL5/6/7, QDGL e QDFs - Parte do Lucas",
                           "Memorial de cálculo passo a passo - dimensionamento dos quadros (T1)")
        y = 0.83
        y = add_text(ax, "Este documento explica, desde o zero, como os quadros das áreas do Lucas foram calculados: "
                         "QDL5 (Escritório), QDL6 (Sala de Produtos + Controle de Qualidade), QDL7 (Banheiro/Vestiário), "
                         "o fechamento do QDGL e a previsão de tomadas (QDF5/6/7).", y, size=13, width=100)
        y -= 0.03
        y = add_text(ax, "A sequência é a mesma da planilha QD-ILUMINAÇÃO.xlsx do time: cargas -> Ip -> fatores de correção "
                         "-> seção por ampacidade -> neutro e terra -> disjuntor -> queda de tensão trecho a trecho -> "
                         "balanceamento -> alimentadores -> quadro geral -> TUGs/TUEs.", y, size=13, width=100)
        y -= 0.04
        y = add_text(ax, "Fontes: Dados iniciais do projeto (EEL 2026-2); PIE 03 (demanda), PIE 04 (ampacidade), "
                         "PIE 05 (neutro, queda de tensão), PIE 06 (proteção); Manual Prysmian 2010 (Tabelas 9.5/9.10/9.17 e "
                         "impedância de sequência positiva); catálogo WEG linha MDW.", y, size=12, width=100)
        y = add_text(ax, "Premissas do TIME adotadas (anotações da própria planilha): método 7 (pé-direito 3 m) com referência "
                         "B1; cabos PVC em ambientes comuns; majorante de 3º harmônico 1,15; dividir circuitos acima de 4500 VA; "
                         "margem de segurança de 10 a 30% no Iz'.", y, size=12, width=100, color="#1F4E78")
        save(pdf, fig)

        # ---------------- passo 0: entradas ----------------
        fig, ax = new_page(pdf, "Passo 0 - Dados de entrada e critérios")
        y = 0.88
        y = add_text(ax, "Tudo que o cálculo usa vem destas cinco fontes. Nenhum valor é inventado.", y, size=12, bold=True)
        rows = [
            ["Tensão BT", "380/220 V, 60 Hz", "Dados iniciais"],
            ["Temperatura ambiente", "45 °C (fator 0,79 p/ PVC)", "Dados iniciais + Tabela 9.4"],
            ["Altitude", "1200 m (sem correção de ampacidade p/ BT)", "Dados iniciais"],
            ["Curto-circuito presumido", "5 kA nos QDL/QDF (7 kA só nos CCM)", "Dados iniciais"],
            ["Luminária", "TMS 426 (2x40 W fl.) + reator duplo: S=115,7 -> 120 VA/ponto, FP 0,90", "Memorial T1 (aba LUM-SP-CQ-B-E)"],
            ["Qtd. luminárias", "Escritório 15 | Sala Prod 3 | CQ 18 | Banheiro 2", "Método dos lumens (T1)"],
            ["Método de instalação", "7 = eletroduto embutido (pé-direito 3 m), referência B1 unipolar", "Anotação M3 da planilha"],
            ["Isolação", "PVC (ambientes comuns)", "Anotação Q71 da planilha"],
            ["3º harmônico", "Majorante 1,15 (lâmpadas de descarga)", "Slide fatores de correção (PIE 04)"],
            ["Limite ΔV", "4% circuito terminal | 7% trafo -> luminária (sinótico)", "PIE 05"],
        ]
        add_table(ax, ["Item", "Valor adotado", "Onde está a fonte"], rows, [0.01, 0.30, 0.98, 0.52], fontsize=9)
        save(pdf, fig)

        # ---------------- passo 1: circuitos e Ip ----------------
        fig, ax = new_page(pdf, "Passo 1 - Divisão em circuitos e corrente de projeto")
        y = 0.88
        y = add_text(ax, "Critério do time: circuitos com demanda <= 4500 VA e a grade do memorial define quantas luminárias "
                         "podem ser comandadas juntas. Como a Sala de Produtos e o CQ são salas separadas, cada uma vira um "
                         "circuito próprio dentro do QDL6.", y, size=12)
        y = add_equations(ax, [r"I_p=\frac{S_{demanda}}{V_{fn}}=\frac{n_{lum}\cdot 120\ \mathrm{VA}}{220}",
                               r"S_{demanda}=n\cdot 120\ \mathrm{VA}\ (\mathrm{aparente,\ P+jQ\ do\ memorial})"], 0.74)
        rows = [
            ["QDL5 / L18", "ESCRITÓRIO", "15", "1800", "8,18", "R"],
            ["QDL6 / L19", "SALA DE PRODUTOS", "3", "360", "1,64", "T"],
            ["QDL6 / L20", "CONTROLE DE QUALIDADE", "18", "2160", "9,82", "S"],
            ["QDL7 / L21", "BANHEIRO (VESTIÁRIO)", "2", "240", "1,09", "T"],
        ]
        add_table(ax, ["Quadro / circuito", "Área", "Nº lum.", "Demanda (VA)", "Ip (A)", "Fase (Passo 6)"],
                  rows, [0.01, 0.26, 0.98, 0.32], fontsize=9.5)
        save(pdf, fig)

        # ---------------- passo 2: fatores ----------------
        fig, ax = new_page(pdf, "Passo 2 - Fatores de correção e seção por ampacidade")
        y = 0.88
        y = add_text(ax, "Corrente corrigida de projeto: divide-se Ip pelos fatores de correção e aplica-se o majorante de "
                         "harmônico. A seção é a menor que mantém Iz' >= Ip', com Iz' = Iz x f_t x f_agrup (tabela Prysmian "
                         "9.5 col. B1, PVC 70 °C: 1,5 mm² -> 17,5 A; 2,5 mm² -> 24 A).", y, size=12)
        y = add_equations(ax, [r"I_p'=\frac{I_p\cdot f_{harm}}{f_{temp}\cdot f_{agrup}}\qquad I_z'=I_z\cdot f_{temp}\cdot f_{agrup}",
                               r"f_{temp}=0{,}79\ (\mathrm{PVC},45^{\circ}C)\quad f_{agrup}=1{,}00\quad f_{harm}=1{,}15"], 0.66, size=13)
        rows = [
            ["L18", "8,18", "11,91", "17,5", "13,83", "1,5 mm² (margem 16%)"],
            ["L19", "1,64", "2,38", "17,5", "13,83", "1,5 mm²"],
            ["L20", "9,82", "14,29", "17,5 -> não atende", "13,83 < 14,29", "2,5 mm²: Iz'=18,96 (margem 33%)"],
            ["L21", "1,09", "1,59", "17,5", "13,83", "1,5 mm²"],
        ]
        add_table(ax, ["Circ.", "Ip (A)", "Ip' (A)", "Iz 1,5 mm² (A)", "Iz' (A)", "Seção adotada"],
                  rows, [0.01, 0.26, 0.98, 0.30], fontsize=9)
        y = 0.235
        y = add_text(ax, "Neutro = seção da fase em circuitos de descarga com 3º harmônico (PIE 05 / NBR 5410 6.2.5). "
                         "PE = fase para seções até 16 mm². Condutores carregados: 2 (fase + neutro).", y, size=11, color="#1F4E78")
        y = add_text(ax, "Atenção para revisão do time: os colegas anotaram EPR nas linhas dos QDL0-4 mas usaram Iz=22 A, "
                         "que é o valor da tabela do PVC (EPR daria 27 A). Nas linhas do Lucas foi usado PVC de forma "
                         "consistente (f_t=0,79 e tabela do PVC).", y, size=10.5)
        save(pdf, fig)

        # ---------------- passo 3: disjuntores ----------------
        fig, ax = new_page(pdf, "Passo 3 - Disjuntores dos circuitos terminais")
        y = 0.86
        y = add_text(ax, "Coordenação condutor x proteção: Iz' > In > Ip, com In do valor comercial (IEC 60898 série C). "
                         "Curva C porque reatores fluorescentes têm corrente de entrada na partida.", y, size=12)
        y = add_equations(ax, [r"I_z'>I_n>I_p\qquad I_{cu}\geq 5\ \mathrm{kA}\ (\mathrm{curto\ presumido\ nos\ QDLs})"], 0.68, size=13.5)
        rows = [
            ["L18", "13,83", "10", "8,18", "MDW-C10 1P+N 5 kA", "OK (Iz' 13,83 > 10 > 8,18)"],
            ["L19", "13,83", "10", "1,64", "MDW-C10", "OK"],
            ["L20", "18,96", "10", "9,82", "MDW-C10", "OK"],
            ["L21", "13,83", "10", "1,09", "MDW-C10", "OK"],
        ]
        add_table(ax, ["Circ.", "Iz' (A)", "In (A)", "Ip (A)", "Disjuntor WEG", "Verificação"],
                  rows, [0.01, 0.26, 0.98, 0.32], fontsize=9)
        y = 0.19
        y = add_quote(ax, "Para dimensionamento dos dispositivos instalados nos quadros de luz e de força considerar a "
                          "corrente de curto-circuito presumida de 5 kA.", "Dados iniciais do projeto (responde a dúvida "
                          "J48 da planilha: NÃO é 2 kA).", y)
        save(pdf, fig)

        # ---------------- passo 4: QT L18 + L19 ----------------
        tr18 = trechos_qt(rota_18(), 1.5)
        fig, ax = new_page(pdf, "Passo 4 - Queda de tensão trecho a trecho (fórmula completa)",
                           "I=120 VA -> Ip do trecho = corrente das luminárias a jusante | L = comprimento + 1,5 m/curva + subida (3,0 - 1,5)")
        y = add_equations(ax, [r"\Delta V=2\cdot I_p\cdot L\cdot(R\cos\varphi+X\sin\varphi)\qquad \Delta V\%=\frac{\Delta V}{V_{fn}}"], 0.80, size=14)
        rows18 = [[a, str(k), f"{L}", str(c), f"{s}", f"{Lt}", f"{i:.2f}", f"{dv:.4f}", f"{p:.3f}", f"{ac:.3f}"]
                  for a, k, L, c, s, Lt, i, dv, p, ac in tr18]
        ax.text(0.01, 0.685, "L18 - ESCRITÓRIO (1,5 mm², R=14,8137 mΩ/m, X=0,1378 mΩ/m, FP 0,90)", fontsize=10.5, fontweight="bold")
        add_table(ax, ["Trecho", "n lum.", "L (m)", "curvas", "subida", "L total", "Ip (A)", "ΔV (V)", "ΔV (%)", "ΔV % acum."],
                  rows18, [0.01, 0.30, 0.98, 0.285], fontsize=7.2)
        ax.text(0.01, 0.025, "ΔV acumulado L18 = 2,33% < 4% OK  |  rotas estimadas pela grade do memorial - ajustar no DWG",
                fontsize=9.5, color="#1F4E78")
        save(pdf, fig)

        # ---------------- passo 4b: QT L20 + L19/L21 ----------------
        tr20 = trechos_qt(rota_20(), 2.5)
        fig, ax = new_page(pdf, "Passo 4 (cont.) - Queda de tensão L20, L19 e L21")
        ax.text(0.01, 0.86, "L20 - CONTROLE DE QUALIDADE (2,5 mm²)", fontsize=10.5, fontweight="bold")
        rows20 = [[a, str(k), f"{L}", str(c), f"{s}", f"{Lt}", f"{i:.2f}", f"{dv:.4f}", f"{p:.3f}", f"{ac:.3f}"]
                  for a, k, L, c, s, Lt, i, dv, p, ac in tr20]
        add_table(ax, ["Trecho", "n lum.", "L (m)", "curvas", "subida", "L total", "Ip (A)", "ΔV (V)", "ΔV (%)", "ΔV acum."],
                  rows20, [0.01, 0.56, 0.98, 0.28], fontsize=7.0)
        rows_short = [[a, str(k), f"{L}", str(c), f"{s}", f"{Lt}", f"{i:.2f}", f"{dv:.4f}", f"{p:.3f}", f"{ac:.3f}"]
                      for a, k, L, c, s, Lt, i, dv, p, ac in
                      trechos_qt([("QDL6-LU1", 3, 2.5, 2, 1.5), ("LU1-LU2", 2, 2.0, 1, 0), ("LU2-LU3*", 1, 2.0, 0, 0)], 1.5) +
                      trechos_qt([("QDL7-LU1", 2, 2.5, 2, 1.5), ("LU1-LU2*", 1, 2.62, 1, 0)], 1.5)]
        ax.text(0.01, 0.535, "L19 - SALA DE PRODUTOS e L21 - BANHEIRO (1,5 mm²)", fontsize=10.5, fontweight="bold")
        add_table(ax, ["Trecho", "n lum.", "L (m)", "curvas", "subida", "L total", "Ip (A)", "ΔV (V)", "ΔV (%)", "ΔV acum."],
                  rows_short, [0.01, 0.10, 0.98, 0.42], fontsize=8)
        ax.text(0.01, 0.02, "Totais: L20 = 1,50% | L19 = 0,20% | L21 = 0,12% - todos < 4% (limite PIE 05).",
                fontsize=9.5, color="#1F4E78")
        save(pdf, fig)

        # ---------------- passo 5: balanceamento ----------------
        fig, ax = new_page(pdf, "Passo 5 - Balanceamento de fases dos QDLs")
        y = 0.86
        y = add_text(ax, "O QDGL entrega as três fases (R, S, T) mais neutro. Os circuitos do time já deixaram "
                         "R=5140, S=4400, T=5280 VA. Os circuitos do Lucas foram distribuídos para achatar a fase mais "
                         "carregada: a maior carga (CQ, 2160 VA) vai na fase mais vazia (S), o Escritório (1800 VA) na R, "
                         "e Sala de Produtos + Banheiro (pequenos) completam a T.", y, size=12)
        rows = [
            ["Antes (QDL0-4)", "5140", "4400", "5280", "14820", "—"],
            ["L18 Escritório", "+1800", "—", "—", "", "R"],
            ["L20 CQ", "—", "+2160", "—", "", "S"],
            ["L19 Sala Prod.", "—", "—", "+360", "", "T"],
            ["L21 Banheiro", "—", "—", "+240", "", "T"],
            ["SOMATÓRIO QDGL", "6940", "6560", "5880", "19380", "R (31,5 A)"],
        ]
        add_table(ax, ["Item", "Fase R (VA)", "Fase S (VA)", "Fase T (VA)", "Total (VA)", "Máx"],
                  rows, [0.01, 0.30, 0.98, 0.28], fontsize=9)
        y = 0.245
        y = add_text(ax, "Correção aplicada na planilha: a célula 'FASE MAIS CARREGADA' agora usa =MAX(E28:G28)/220 "
                         "(antes só dividia a coluna T por 220).", y, size=11, color="#1F4E78")
        save(pdf, fig)

        # ---------------- passo 6: alimentadores ----------------
        fig, ax = new_page(pdf, "Passo 6 - Alimentadores QDGL -> QDL5/6/7 (e QDGBT -> QDGL)",
                           "Rota em bandeja perfurada (método 13 / ref. F, cabos unipolares), EPR -> f_t = 0,87; "
                           "agrupamento Tabela 9.10 ref. 4 com 8 alimentadores -> f_agrup = 0,72")
        y = 0.84
        y = add_equations(ax, [r"I_p'=\frac{I_p\cdot 1{,}15}{0{,}87\cdot 0{,}72}",
                               r"QDL5: 8{,}18\Rightarrow I_p'=15{,}0\ \mathrm{A};\quad QDL6{=}\frac{2520}{380}=6{,}63\Rightarrow 12{,}2\ \mathrm{A};\quad QDL7: 1{,}09\Rightarrow 2{,}0\ \mathrm{A}"], 0.74, size=12.5)
        rows = [
            ["QDGL-QDL5", "220 V (R)", "8,18", "127", "1,5 mm²: 12,7% EXCEDE", "6 mm²", "3,20%", "MDWH-C10 5 kA"],
            ["QDGL-QDL6", "380 V (S+T)", "6,63", "127", "1,5 mm²: 7,0% EXCEDE", "2,5 mm²", "3,57%", "MDWH-C10/2"],
            ["QDGL-QDL7", "220 V (T)", "1,09", "127", "1,5 mm² já atende", "1,5 mm²", "1,69%", "MDWH-C10"],
            ["QDGBT-QDGL", "380/220 (4 cabos)", "31,55", "10", "ampacidade domina", "10 mm²", "0,59%", "MDWH-C40 3P"],
        ]
        add_table(ax, ["Alimentador", "Sistema", "Ip (A)", "L (m)", "Critério que define", "Seção", "ΔV (lim. 4%)", "Disjuntor"],
                  rows, [0.01, 0.26, 0.98, 0.34], fontsize=8.5)
        y = 0.235
        y = add_text(ax, "R/X da tabela de impedância de sequência positiva (127 m = valor da equipe p/ rota até a ala "
                         "administrativa - AJUSTAR NO DWG). QGDL: fase mais carregada 6940 VA -> Ip = 6940/220 = 31,5 A; "
                         "Ip' = 31,5x1,15/0,87 = 41,7 A; Iz' = 74x0,87 = 64,4 A (10 mm² EPR ref. F, 3 cabos carregados); "
                         "In = 40 A: 31,5 < 40 <= 64,4 OK.", y, size=11)
        y = add_text(ax, "Sinótico acumulado (trafo -> luminária): 0,6% + 3,2% + ~2% = ~5,8% < 7% OK.", y, size=11.5, bold=True, color="#1F4E78")
        save(pdf, fig)

        # ---------------- passo 7: QDF ----------------
        fig, ax = new_page(pdf, "Passo 7 - Previsão de tomadas TUG/TUE (QDF5/6/7)",
                           "Método comercial/residencial da NBR 5410 (Tabela 9 do Prysmian), como exige o dado inicial")
        y = 0.84
        rows = [
            ["ESCRITÓRIO", "48,72 m² > 40", "10 + 1 p/ 10 m² exced. = 11", "2200", "1 climatizador (pot. a definir)", "QDF5"],
            ["CONTROLE DE QUALIDADE", "30 m² <= 40", "max(perím/3, área/4) = 8", "1600", "1 climatizador", "QDF6"],
            ["SAÍDA DE PRODUTOS", "30 m² <= 40", "idem CQ = 8", "1600", "1 climatizador", "QDF6"],
            ["BANHEIRO", "18,3 m²", "1 TUG junto à pia", "600", "chuveiros 9 kW (2 adotados) + DDR 30 mA", "QDF7"],
        ]
        add_table(ax, ["Área", "Regra (Tabela 9)", "Qtd TUG", "P TUG (VA)", "TUE", "Quadro"],
                  rows, [0.01, 0.52, 0.98, 0.26], fontsize=8.5)
        y = 0.44
        y = add_equations(ax, [r"\mathrm{Chuveiro\ 9\ kW/220\ V}:\ I_p=\frac{9000}{220}=40{,}9\ \mathrm{A}",
                               r"10\ \mathrm{mm}^2\ \mathrm{PVC}\ B1:\ I_z'=57\cdot 0{,}79=45{,}0<50\ \Rightarrow\ 16\ \mathrm{mm}^2:\ I_z'=76\cdot 0{,}79=60{,}0\ \mathrm{A}",
                               r"I_n=50\ \mathrm{A}:\ 40{,}9<50\leq 60\ \checkmark\ \ (\Delta V\approx 0{,}8\%\ \mathrm{a}\ 15\ \mathrm{m})"], 0.40, size=12.5)
        ax.text(0.01, 0.17, "TUGs: circuitos de 2,5 mm² com MDW-C10 (4 a 6 tomadas por circuito), FP~1\n"
                            "sem majorante de harmônico. Gerais propostas: QDF5 C25 | QDF6 C32 | QDF7 C100.",
                fontsize=10.5)
        save(pdf, fig)

        # ---------------- pendencias ----------------
        fig, ax = new_page(pdf, "Resumo, pendências e rastreabilidade")
        y = 0.86
        y = add_text(ax, "RESULTADO FINAL - todos os critérios atendidos: circuito terminal <= 4%, alimentação <= 4%, "
                         "sinótico <= 7%, Iz' > In > Ip, Icu >= 5 kA, neutro = fase, balanceamento R6940/S6560/T5880.",
                     y, size=12.5, bold=True, color="#1F4E78")
        y = add_text(ax, "PENDÊNCIAS (marcadas na planilha como 'ajustar no DWG'):", y, size=12)
        for t in ["1. Medir os comprimentos reais no DWG (rotas QDGL->QDL5/6/7 - os 127 m são estimativa do time; "
                  "trechos internos seguem a grade do memorial).",
                  "2. Confirmar com o grupo a potência dos climatizadores (TUEs) e o número de chuveiros do vestiário.",
                  "3. Revisar com o time a inconsistência EPR/PVC dos QDL0-4 (Iz=22 A é valor do PVC).",
                  "4. Transferir as tabelas deste PDF para o T1-MEMORIAL DE CALCULO.docx, na ordem QDGL -> QDL5 -> QDL6 -> QDL7 -> QDFs.",
                  "5. T2 (15/09): regime e transitório térmico dos condutores usando Ip' e a seção aqui definidas (pot. vetorial P+jQ, condição mais crítica)."]:
            y = add_text(ax, t, y, size=11.5, x=0.03)
        y = add_text(ax, "ONDE ESTÁ CADA NÚMERO: aba QDL (Ip), QDL-FATOR CORREÇÃO (Ip'/Iz'), SEÇÃO CONDUTORES, "
                         "DISJUNTORES, QDL-QUEDA DE TENSÃO (linhas 22-25 e blocos 390-447), QDL-BALANÇO TOTAL, "
                         "QDL-BALANÇO POTENCIAS (281-296), QDGL (linhas 22-25, 60-64 e 126-134) e QDF-TOMADAS-LUCAS.",
                     y, size=11)
        save(pdf, fig)


if __name__ == "__main__":
    main()
    print("PDF gerado:", PDF_PATH)
