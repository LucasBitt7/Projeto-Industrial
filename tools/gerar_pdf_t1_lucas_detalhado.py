from math import ceil
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "T1_LUCAS_Passo_a_Passo_Detalhado.pdf"

K_VALUES = [0.60, 0.80, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 4.00, 5.00]
FU_70_50 = [0.35, 0.43, 0.50, 0.56, 0.61, 0.68, 0.72, 0.76, 0.80, 0.83]
FU_70_30 = [0.28, 0.36, 0.42, 0.49, 0.54, 0.61, 0.67, 0.71, 0.76, 0.80]

AREAS = [
    {"name": "Sala de Produtos", "w": 5.00, "l": 6.00, "e": 200, "wall": 50, "qdl": "QDL6", "classification": "Armazenamento de grandes volumes"},
    {"name": "Controle de Qualidade", "w": 5.00, "l": 6.00, "e": 500, "wall": 50, "qdl": "QDL6", "classification": "Inspeção"},
    {"name": "Banheiro/Vestiário", "w": 5.23, "l": 3.50, "e": 200, "wall": 50, "qdl": "QDL7", "classification": "Banheiros"},
    {"name": "Escritório", "w": 8.12, "l": 6.00, "e": 250, "wall": 45, "qdl": "QDL5", "classification": "Sala de trabalho"},
]


def interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            return ys[i] + (x - xs[i]) * (ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i])
    return ys[-1]


def calc(area, fdl=0.75):
    s = area["w"] * area["l"]
    hp = 3.00 - 0.80
    k = s / (hp * (area["w"] + area["l"]))
    fu30 = interp(k, K_VALUES, FU_70_30)
    fu50 = interp(k, K_VALUES, FU_70_50)
    fu = fu30 if area["wall"] <= 30 else fu50 if area["wall"] >= 50 else fu30 + (area["wall"] - 30) * (fu50 - fu30) / 20
    flux = area["e"] * s / (fu * fdl)
    n_theory = flux / 6000
    n = ceil(n_theory)
    e_out = n * 6000 * fu * fdl / s
    p = n * (2 * 40 + 24.1)
    apparent = p / 0.90
    current = apparent / 220
    return {**area, "s": s, "hp": hp, "k": k, "fu30": fu30, "fu50": fu50, "fu": fu, "flux": flux, "n_theory": n_theory, "n": n, "e_out": e_out, "p": p, "apparent": apparent, "current": current}


RESULTS = [calc(a) for a in AREAS]


def add_text(ax, text, y, size=11, color="#222222", bold=False, width=108, line_gap=0.042, x=0.01):
    wrapped = fill(text, width=width)
    ax.text(x, y, wrapped, fontsize=size, color=color, fontweight="bold" if bold else "normal", va="top", ha="left")
    return y - line_gap * (wrapped.count("\n") + 1)


def add_quote(ax, quote, source, y, x=0.01, width=104):
    y = add_text(ax, f'"{quote}"', y, size=10.5, color="#1F4E78", width=width, line_gap=0.038, x=x)
    y = add_text(ax, f"Fonte: {source}", y, size=9, color="#666666", width=width, line_gap=0.032, x=x)
    return y - 0.015


def add_equations(ax, equations, y, x=0.045, size=16):
    for equation in equations:
        ax.text(x, y, f"${equation}$", fontsize=size, va="top", color="#111111")
        y -= 0.068
    return y


def add_table(ax, headers, rows, bbox, fontsize=9):
    table = ax.table(cellText=rows, colLabels=headers, bbox=bbox, cellLoc="center", loc="upper left")
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#B7C9D6")
        cell.get_text().set_wrap(True)
        if row == 0:
            cell.set_facecolor("#D9EAF7")
            cell.set_text_props(weight="bold", color="#1F4E78")
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


def page_cover(pdf):
    fig, ax = new_page(pdf, "T1 - Luminotécnico | Parte do Lucas", "Memorial de cálculo detalhado - Método dos Lumens")
    y = 0.83
    y = add_text(ax, "Este documento explica, desde o zero, como foram escolhidos os parâmetros e como foram calculadas as luminárias das quatro áreas atribuídas ao Lucas.", y, size=14, width=100, line_gap=0.05)
    y -= 0.03
    y = add_text(ax, "A sequência é: ler o requisito do projeto, entender os conceitos, identificar os dados de cada ambiente, escolher a iluminância, definir as refletâncias, calcular K, obter Fu, definir Fdl, calcular o fluxo, arredondar a quantidade, verificar a iluminância final e resumir as cargas.", y, size=13, width=100, line_gap=0.05)
    y -= 0.04
    y = add_text(ax, "Luminária principal: TMS 426 fluorescente, com duas lâmpadas de 40 W.", y, size=15, color="#1F4E78", bold=True, width=100, line_gap=0.05)
    y = add_text(ax, "Planilha de origem: PLANILHA_PROJETOS.xlsx, aba DADOS, linhas 11 a 14. A aba LUM-LUCAS recalcula tudo se as premissas mudarem.", y, size=12, width=100, line_gap=0.045)
    y = add_text(ax, "Cada número pode ser rastreado até uma fonte citada ou até uma premissa declarada na parte F.", y, size=12, width=100, line_gap=0.045)
    save(pdf, fig)


def page_how_to_use(pdf):
    fig, ax = new_page(pdf, "1. Como usar este documento")
    y = 0.90
    y = add_text(ax, "O documento está dividido em seis partes, em ordem de leitura:", y, size=12, width=108, line_gap=0.045)
    items = [
        "Parte A - Fundamentos: conceitos de iluminação e a lógica do Método dos Lumens (para quem nunca viu o assunto).",
        "Parte B - Requisitos: o que o enunciado do projeto cobra e de onde vem cada dado usado.",
        "Parte C - Escolhas: luminária TMS 426, iluminâncias-alvo, refletâncias e como ler a Tabela 2.9.",
        "Parte D - Cálculos: K, Fu, Fdl e um exemplo numérico completo para cada uma das quatro salas.",
        "Parte E - Elétrica: como surge a carga (W, VA, A) e o resumo por quadro QDL.",
        "Parte F - Conferência: folgas, sensibilidade ao Fdl, premissas, roteiro de apresentação e glossário.",
    ]
    for item in items:
        y = add_text(ax, item, y, size=11.5, width=106, line_gap=0.045)
        y -= 0.012
    y -= 0.01
    add_text(ax, "Se precisar justificar um valor em aula, siga a cadeia: enunciado -> tabela citada -> fórmula -> número -> verificação. Nenhum resultado foi usado sem origem.", y, size=12, color="#1F4E78", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_concepts(pdf):
    fig, ax = new_page(pdf, "2. A. Conceitos fundamentais")
    y = 0.90
    y = add_text(ax, "Iluminação técnica usa poucas grandezas. Entendê-las torna cada fórmula do memorial óbvia.", y, size=12, width=108, line_gap=0.045)
    rows = [
        ["Fluxo luminoso", "Φ", "lúmen (lm)", "Quantidade total de luz emitida por uma fonte"],
        ["Iluminância", "E", "lux (lx)", "Fluxo que chega a cada m²; 1 lux = 1 lm/m²"],
        ["Refletância", "ρ", "%", "Fração da luz que a superfície devolve ao ambiente"],
        ["Fator de utilização", "Fu", "-", "Fração do fluxo das lâmpadas que atinge o plano útil"],
        ["Fator de depreciação", "Fdl", "-", "Reduz o fluxo por sujeira e envelhecimento"],
        ["Índice do recinto", "K", "-", "Proporção entre área e altura útil da sala"],
    ]
    add_table(ax, ["Grandeza", "Símbolo", "Unidade", "Significado"], rows, bbox=(0.01, 0.32, 0.98, 0.42), fontsize=9)
    y = 0.26
    y = add_text(ax, "Diferenças importantes: a lâmpada é a fonte de luz; a luminária é o conjunto completo (carcaça, lâmpadas e reator); o reator é o acessório que limita a corrente de lâmpadas de descarga e dissipa parte da potência.", y, size=11.5, width=108, line_gap=0.045)
    add_text(ax, "O objetivo do projeto é garantir E (lux) no plano de trabalho. Todo o cálculo existe para descobrir quantas luminárias produzem essa E.", y, size=11.5, color="#1F4E78", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_logic(pdf):
    fig, ax = new_page(pdf, "3. A. A lógica do Método dos Lumens")
    y = 0.88
    y = add_text(ax, "1. A norma ou o enunciado fixa a iluminância alvo E para a atividade do ambiente.", y, size=12, width=108, line_gap=0.045)
    y = add_equations(ax, [r"\Phi_{util}=E\times S"], y)
    y = add_text(ax, "2. Nem toda a luz das lâmpadas chega ao plano de trabalho: parte é absorvida por paredes e teto e parte se perde com sujeira e envelhecimento. Por isso o fluxo útil é dividido por Fu e Fdl.", y, size=12, width=108, line_gap=0.045)
    y = add_equations(ax, [r"\Phi_{lampadas}=\frac{E\times S}{F_u\times F_{dl}}"], y)
    y = add_text(ax, "3. Cada luminária entrega o fluxo fixo das suas lâmpadas. Dividir encontra a quantidade.", y, size=12, width=108, line_gap=0.045)
    y = add_equations(ax, [r"N_{LU}=\frac{\Phi_{lampadas}}{n_{lamp}\times\phi_{lamp}}"], y)
    y = add_text(ax, "4. A quantidade é arredondada sempre para cima e a iluminância obtida é recalculada para confirmar que ficou igual ou acima do alvo.", y, size=12, width=108, line_gap=0.045)
    add_text(ax, "Se o arredondamento fosse para baixo, a iluminância obtida ficaria abaixo do valor exigido pela norma.", y - 0.01, size=11.5, color="#9C6500", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_scope(pdf):
    fig, ax = new_page(pdf, "4. B. O que o projeto exige")
    y = 0.90
    y = add_quote(ax, "Para as áreas Sala de Produto, Controle de Qualidade, Banheiro (Vestuário) e Escritório [...] O método utilizado deverá ser o de Lumens.", "Dados iniciais do projeto, p. 5/6", y)
    y = add_quote(ax, "A altura de manuseio para o trabalho é de 0,8 metros.", "Dados iniciais do projeto, p. 5/6", y)
    y = add_quote(ax, "Essas áreas possuem o piso em azulejo cinza. Poderá ser utilizado lâmpadas fluorescentes, ou similares.", "Dados iniciais do projeto, p. 5/6", y)
    y = add_text(ax, "Conclusão: as quatro áreas do Lucas devem ser calculadas pelo Método dos Lumens. A TMS 426 é uma luminária fluorescente e, portanto, atende diretamente à opção indicada no enunciado.", y, size=12, width=108, line_gap=0.047)
    add_table(ax, ["Área", "Dimensões [m]", "Área [m²]", "Pé-direito [m]", "Linha DADOS"], [[a["name"], f'{a["w"]:.2f} x {a["l"]:.2f}', f'{a["w"]*a["l"]:.3f}', "3,00", f"{i}"] for a, i in zip(AREAS, [11, 12, 13, 14])], bbox=(0.01, 0.10, 0.98, 0.28), fontsize=9.5)
    add_text(ax, "O pé-direito de 3,00 m vem de DADOS!K11:K14.", 0.055, size=9.5, color="#666666", width=108)
    save(pdf, fig)


def page_inputs(pdf):
    fig, ax = new_page(pdf, "5. B. De onde veio cada entrada")
    y = 0.90
    y = add_text(ax, "A planilha separa dados originais, escolhas de projeto e resultados. Isso é importante porque nem tudo possui o mesmo nível de certeza.", y, size=12, width=108, line_gap=0.045)
    rows = [
        ["Dimensões e pé-direito", "DADOS!D11:K14", "Dado informado na planilha"],
        ["Plano de trabalho", "Dados iniciais, p. 5/6", "0,80 m"],
        ["Método", "Dados iniciais, p. 5/6", "Lumens"],
        ["Luminária", "Tabelas auxiliares, Tab. 2.9", "TMS 426"],
        ["Fluxo da lâmpada", "Tabelas auxiliares, Tab. 2.1", "3.000 lm / lâmpada"],
        ["Perdas e FP", "Tabelas auxiliares, tabela de reatores", "24,1 W e FP 0,90"],
        ["Iluminância", "Tabelas auxiliares, Tab. 2.6", "200, 500, 200 e 250 lux"],
        ["Refletâncias", "Tab. de refletâncias + Tab. 2.9", "70%, 50% e 45%"],
        ["Fdl", "Tabela de fatores de depreciação", "0,75 para luminária comercial"],
    ]
    add_table(ax, ["Entrada", "Origem", "Valor/critério"], rows, bbox=(0.01, 0.17, 0.98, 0.55), fontsize=9)
    add_text(ax, "As células amarelas da aba LUM-LUCAS são premissas editáveis. As verdes são calculadas por fórmula.", 0.12, size=11, color="#1F4E78", bold=True, width=108)
    save(pdf, fig)


def page_lamp_choice(pdf):
    fig, ax = new_page(pdf, "6. C. Por que a TMS 426 foi escolhida")
    y = 0.90
    y = add_text(ax, "A escolha não significa que a TMS 426 seja a única luminária possível. Ela foi escolhida porque é a alternativa mais rastreável para a planilha, já que a tabela fornece simultaneamente a luminária, os valores de Fu e os dados elétricos do conjunto.", y, size=12, width=108, line_gap=0.047)
    y = add_quote(ax, "TMS 426 - 2 lâmpadas de 40 W", "Tabelas auxiliares, Tabela 2.9", y)
    y = add_quote(ax, "Fluorescente comum - 40 W - 3.000 lúmens", "Tabelas auxiliares, Tabela 2.1", y)
    y = add_text(ax, "Comparação com as outras opções da tabela:", y, size=12, color="#1F4E78", bold=True, width=108, line_gap=0.047)
    rows = [
        ["TMS 426", "2 x 40 W", "6.000 lm", "Fluxo moderado; adequada às salas pequenas e médias; Fu disponível"],
        ["TMS 500", "2 x 65 W", "Maior que 6.000 lm", "Mais potência; menos flexível em ambientes pequenos"],
        ["TCK 427", "4 x 40 W", "12.000 lm", "Fluxo elevado; menos flexível na distribuição"],
        ["HDK 472", "1 x 400 W", "22.000 lm", "Vapor de mercúrio; adequada a áreas industriais altas"],
    ]
    add_table(ax, ["Opção", "Composição", "Fluxo aprox.", "Análise"], rows, bbox=(0.01, 0.10, 0.98, 0.32), fontsize=8)
    add_text(ax, "Para usar LED seria necessário substituir Fu e os dados elétricos por ficha técnica de fabricante.", 0.055, size=9.5, color="#9C6500", bold=True, width=108)
    save(pdf, fig)


def page_tms_electric(pdf):
    fig, ax = new_page(pdf, "7. C. Dados elétricos da TMS 426")
    y = 0.90
    y = add_text(ax, "Cada luminária TMS 426 possui duas lâmpadas fluorescentes de 40 W (3.000 lm cada) e um reator duplo de 220 V. A tabela de reatores informa 24,1 W de perdas e fator de potência 0,90. Com esses três números, calcula-se a carga de uma luminária:", y, size=12, width=108, line_gap=0.047)
    y = add_equations(ax, [r"P_{lum}=2\times40+24,1=104,1\ W", r"S_{lum}=\frac{104,1}{0,90}=115,7\ VA", r"I_{lum}=\frac{115,7}{220}=0,53\ A"], y - 0.01)
    rows = [["Fluxo por luminária", "6.000 lm"], ["Potência ativa", "104,1 W"], ["Potência aparente", "115,7 VA"], ["Corrente em 220 V", "0,53 A"]]
    add_table(ax, ["Grandeza por luminária", "Valor"], rows, bbox=(0.01, 0.28, 0.60, 0.24), fontsize=9.5)
    add_text(ax, "O catálogo de reatores indica 0,51 A para o conjunto 2 x 40 W em 220 V. A pequena diferença vem de arredondamentos do próprio catálogo; a planilha mantém a corrente calculada para manter consistência interna.", 0.20, size=10.5, color="#9C6500", bold=True, width=108, line_gap=0.042)
    save(pdf, fig)


def page_illuminance(pdf):
    fig, ax = new_page(pdf, "8. C. Escolha da iluminância E")
    y = 0.90
    y = add_quote(ax, "Iluminâncias mínimas em lux, por tipo de atividade (valores médios em serviço)", "Tabelas auxiliares, Tabela 2.6", y)
    y = add_text(ax, "A iluminância não é escolhida pela área física. Ela é escolhida pelo tipo de atividade visual. Por isso cada ambiente precisa ser associado à atividade mais próxima na tabela.", y, size=12, width=108, line_gap=0.047)
    rows = [[a["name"], a["classification"], str(a["e"]), "Tabela 2.6"] for a in AREAS]
    add_table(ax, ["Ambiente", "Classificação", "E [lux]", "Origem"], rows, bbox=(0.01, 0.40, 0.98, 0.21), fontsize=9.5)
    y = 0.36
    y = add_text(ax, "Sala de Produtos: armazenamento de grandes volumes, pois é uma saída/sala de produtos.", y, size=10.5, width=108, line_gap=0.038)
    y = add_text(ax, "Controle de Qualidade: inspeção, que exige maior atenção visual.", y, size=10.5, width=108, line_gap=0.038)
    y = add_text(ax, "Banheiro/Vestiário: linha Banheiros; confirmar se o vestiário é tratado como permanência curta.", y, size=10.5, width=108, line_gap=0.038)
    y = add_text(ax, "Escritório: sala de trabalho; não foi usada a linha Sala de desenho.", y, size=10.5, width=108, line_gap=0.038)
    add_text(ax, "Essas classificações são decisões de engenharia documentadas, não valores fornecidos por sala.", 0.03, size=9.5, color="#9C6500", bold=True, width=108)
    save(pdf, fig)


def page_reflectance(pdf):
    fig, ax = new_page(pdf, "9. C. Origem dos percentuais de teto, parede e piso")
    y = 0.90
    y = add_text(ax, "A refletância é a parcela da luz que uma superfície devolve ao ambiente. Ela influencia o fator de utilização porque paredes e teto claros devolvem mais luz para o plano de trabalho.", y, size=12, width=108, line_gap=0.047)
    y = add_quote(ax, "Branco-neve - 80; Branco-marfim - 70; Creme-claro - 70; Bege - 45; Cinza-claro - 45", "Tabelas auxiliares, tabela de refletâncias", y)
    y = add_text(ax, "A palavra CLARA não é um percentual medido. Por isso 50% é uma premissa compatível com a coluna de parede clara da tabela. Já BEGE possui o valor explícito de 45%.", y, size=10.5, color="#9C6500", bold=True, width=108, line_gap=0.042)
    rows = [
        ["CLARO", "Descrição qualitativa em DADOS", "70%", "Coluna disponível no teto da Tab. 2.9"],
        ["BRANCO", "Branco-neve = 80%", "70%", "A Tab. 2.9 não possui teto 80%; usa-se o limite tabelado"],
        ["CLARA", "Descrição qualitativa em DADOS", "50%", "Coluna de parede adotada para ambiente claro"],
        ["BRANCA", "Branco-neve = 80%", "50%", "A Tab. 2.9 não possui parede 80%; usa-se a maior coluna"],
        ["BEGE", "Bege = 45%", "45%", "Valor diretamente extraído da tabela de refletâncias"],
        ["Azulejo cinza", "Piso informado no projeto", "10%", "A Tab. 2.9 fornecida é publicada para piso de 10%"],
    ]
    add_table(ax, ["Descrição em DADOS", "Origem", "Valor usado", "Justificativa"], rows, bbox=(0.01, 0.06, 0.98, 0.43), fontsize=8)
    save(pdf, fig)


def page_read_table(pdf):
    fig, ax = new_page(pdf, "10. C. Como ler a Tabela 2.9 (fator de utilização)")
    y = 0.90
    y = add_text(ax, "A Tabela 2.9 é organizada em blocos: um bloco por luminária. Dentro do bloco da TMS 426, as colunas são combinações de refletância de teto e parede, e as linhas são valores de K. O cabeçalho informa que os valores foram publicados para piso de 10%.", y, size=12, width=108, line_gap=0.047)
    add_table(ax, ["", "Col. 1", "Col. 2", "Col. 3", "Col. 4", "Col. 5", "Col. 6", "Col. 7", "Col. 8"], [["Teto %", "70", "70", "50", "50", "70", "50", "30", "30"], ["Parede %", "50", "30", "50", "30", "10", "10", "30", "10"]], bbox=(0.01, 0.60, 0.98, 0.14), fontsize=8.5)
    y = 0.54
    steps = [
        "1. Localize o bloco da TMS 426 dentro da tabela.",
        "2. Calcule o K do ambiente (página 11 deste memorial).",
        "3. Escolha a coluna pela refletância do teto; neste projeto, 70% (colunas 1 e 2).",
        "4. Confirme a subcoluna da parede: 50% ou 30%.",
        "5. Leia a linha do K; se K cair entre duas linhas, interpole.",
        "6. Se a parede tiver valor intermediário (bege 45%), interpole entre as duas colunas.",
    ]
    for step in steps:
        y = add_text(ax, step, y, size=11, width=108, line_gap=0.040)
        y -= 0.006
    add_text(ax, "Nas colunas de 10% de parede o ambiente seria mais escuro; por isso nunca se deve trocar de coluna sem justificativa.", y - 0.01, size=10.5, color="#9C6500", bold=True, width=108, line_gap=0.042)
    save(pdf, fig)


def page_geometry(pdf):
    fig, ax = new_page(pdf, "11. D. Cálculo da altura útil e do índice K")
    y = 0.90
    y = add_text(ax, "A altura do plano de trabalho é 0,80 m. Como as linhas 11 a 14 da aba DADOS possuem pé-direito de 3,00 m, a distância entre a luminária no teto e o plano de trabalho é 2,20 m. Se as luminárias forem penduradas abaixo do teto, Hlp passa a usar a altura de instalação.", y, size=12, width=108, line_gap=0.047)
    y = add_equations(ax, [r"H_{lp}=H_{instalacao}-H_{trabalho}=3,00-0,80=2,20\ m", r"K=\frac{L\times C}{H_{lp}\times(L+C)}"], y - 0.02)
    rows = []
    for r in RESULTS:
        rows.append([r["name"], f'{r["s"]:.3f}', f'{r["hp"]:.2f}', f'{r["k"]:.3f}', f'{r["w"]:.2f} + {r["l"]:.2f}'])
    add_table(ax, ["Ambiente", "S [m²]", "Hlp [m]", "K", "Dimensões"], rows, bbox=(0.01, 0.28, 0.98, 0.28), fontsize=9.5)
    add_text(ax, "Interpretação: K representa a proporção geométrica entre a área do ambiente e a altura útil. Ele será usado para localizar os valores vizinhos de Fu na Tabela 2.9.", 0.22, size=11, width=108)
    save(pdf, fig)


def page_k_meaning(pdf):
    fig, ax = new_page(pdf, "12. D. O que o índice K significa")
    y = 0.90
    y = add_text(ax, "K mede o quão 'compacta' a sala é em relação à altura útil. Salas proporcionais retêm e reaproveitam melhor a luz entre teto, paredes e plano de trabalho; salas muito altas em relação à área perdem mais luz para as paredes antes de ela retornar ao plano útil.", y, size=12, width=108, line_gap=0.047)
    y = add_text(ax, "Por isso duas salas com a mesma área podem ter Fu diferentes: o que manda não é a área sozinha, e sim a relação entre área e altura. Compare:", y, size=12, width=108, line_gap=0.047)
    y = add_equations(ax, [r"K_{Sala}=\frac{30,00}{2,20\times11,00}=1,240", r"K_{Banheiro}=\frac{18,31}{2,20\times8,73}=0,953"], y - 0.01)
    y = add_text(ax, "A Sala de Produtos tem 30 m² e K 1,240; o Banheiro tem 18,31 m² e K 0,953. O Banheiro é proporcionalmente mais 'alto', então seu Fu é menor (0,484 contra 0,558) e cada lúmen instalado rende menos.", y, size=12, width=108, line_gap=0.047)
    add_text(ax, "K pequeno (sala 'alta') -> Fu menor -> mais fluxo necessário. K grande (sala 'baixa e compacta') -> Fu maior -> menos fluxo necessário.", y - 0.01, size=11.5, color="#1F4E78", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_fu(pdf):
    fig, ax = new_page(pdf, "13. D. Como o fator Fu é encontrado")
    rows = [[f"{k:.2f}".replace(".", ","), f"{a:.2f}".replace(".", ","), f"{b:.2f}".replace(".", ",")] for k, a, b in zip(K_VALUES, FU_70_50, FU_70_30)]
    add_table(ax, ["K", "Fu 70/50", "Fu 70/30"], rows, bbox=(0.01, 0.10, 0.40, 0.50), fontsize=8.5)
    x = 0.45
    y = 0.90
    y = add_quote(ax, "A interpolação é utilizada para definir um valor indeterminado entre os limites dos tabelados.", "PIE 02, p. 67/105", y, x=x, width=52)
    y = add_text(ax, "A Tabela 2.9 da TMS 426 usa piso de 10% e fornece duas colunas úteis: teto 70% com parede 50% e teto 70% com parede 30%.", y, size=11, width=52, line_gap=0.045, x=x)
    y = add_equations(ax, [r"F_u=F_{u,inf}+\frac{(K-K_{inf})(F_{u,sup}-F_{u,inf})}{K_{sup}-K_{inf}}", r"F_u(45\%)=F_u(30\%)+\frac{45-30}{50-30}[F_u(50\%)-F_u(30\%)]"], y - 0.02, x=x)
    add_text(ax, "Primeiro interpola-se K dentro da coluna escolhida. Se a parede for bege, interpola-se depois entre as colunas de parede 30% e 50%. Isso evita escolher Fu por aproximação visual.", y - 0.03, size=11, width=52, x=x)
    save(pdf, fig)


def page_fu_calcs(pdf):
    fig, ax = new_page(pdf, "14. D. Interpolação numérica de Fu para cada sala")
    y = 0.90
    for r in RESULTS:
        if r["name"] in ("Sala de Produtos", "Controle de Qualidade"):
            text = f'{r["name"]}: K = {r["k"]:.4f}, entre K=1,00 (Fu=0,50) e K=1,25 (Fu=0,56). '
            text += f'Fu = 0,50 + [({r["k"]:.4f}-1,00)/(1,25-1,00)] x (0,56-0,50) = {r["fu"]:.3f}.'
        elif r["name"] == "Banheiro/Vestiário":
            text = f'{r["name"]}: K = {r["k"]:.4f}, entre K=0,80 (Fu=0,43) e K=1,00 (Fu=0,50). '
            text += f'Fu = 0,43 + [({r["k"]:.4f}-0,80)/(1,00-0,80)] x (0,50-0,43) = {r["fu"]:.3f}.'
        else:
            text = f'{r["name"]}: K = {r["k"]:.4f}, entre K=1,50 e K=2,00. '
            text += f'Para parede 30%, Fu varia de 0,54 a 0,61, resultando em {r["fu30"]:.3f}; para parede 50%, varia de 0,61 a 0,68, resultando em {r["fu50"]:.3f}. '
            text += f'Como a parede é 45%, Fu = {r["fu"]:.3f}.'
        y = add_text(ax, text, y, size=11.5, width=108, line_gap=0.046)
        y -= 0.025
    add_text(ax, "Resultados finais de Fu: Sala de Produtos 0,558; Controle de Qualidade 0,558; Banheiro/Vestiário 0,484; Escritório 0,602.", y - 0.01, size=12, color="#1F4E78", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_fdl(pdf):
    fig, ax = new_page(pdf, "15. D. Fator de depreciação Fdl")
    y = 0.90
    y = add_text(ax, "Fdl reduz o fluxo útil considerado no projeto para representar perdas de manutenção, sujeira e envelhecimento do sistema. Como Fdl aparece no denominador, um fator menor exige mais fluxo instalado.", y, size=12, width=108, line_gap=0.047)
    y = add_quote(ax, "Luminária comercial ... 0,75", "Tabelas auxiliares, quadro de fatores de depreciação", y)
    y = add_quote(ax, "Na ausência de dados de manutenção ... Fdl = 0,7", "PIE 02, p. 69/105", y)
    y = add_text(ax, "Critério adotado: a TMS 426 foi tratada como luminária comercial, portanto Fdl = 0,75. O valor genérico 0,70 não foi usado porque existe um valor específico de tabela para o tipo de luminária adotado.", y, size=12, width=108, line_gap=0.047)
    y = add_equations(ax, [r"F_{dl}=0,75", r"\Phi_t=\frac{E\times S}{F_u\times F_{dl}}"], y - 0.02)
    add_text(ax, "Sensibilidade: caso seja exigido Fdl = 0,70, a quantidade pode aumentar, principalmente no Controle de Qualidade. A comparação numérica completa está na página 25.", y - 0.01, size=11, color="#9C6500", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_example_part1(pdf):
    r = RESULTS[0]
    fig, ax = new_page(pdf, "16. D. Exemplo completo - Sala de Produtos, Parte 1", "Fluxo e quantidade")
    y = 0.88
    y = add_text(ax, f'Dados: L = {r["w"]:.2f} m; C = {r["l"]:.2f} m; S = {r["s"]:.2f} m²; E = {r["e"]} lux; teto 70%; parede 50%; Fdl = 0,75.', y, size=11.5, width=108, line_gap=0.045)
    y = add_equations(ax, [r"H_{lp}=3,00-0,80=2,20\ m", r"K=\frac{5,00\times6,00}{2,20\times(5,00+6,00)}=\frac{30,00}{24,20}=1,240", r"F_u=0,50+\frac{1,240-1,00}{1,25-1,00}\times(0,56-0,50)=0,558", r"\Phi_t=\frac{200\times30,00}{0,558\times0,75}=14.349\ lm", r"N_{LU}=\frac{14.349}{2\times3.000}=2,39", r"N_{instalado}=\lceil2,39\rceil=3"], y)
    add_text(ax, "A quantidade é arredondada para cima porque 2 luminárias não atingiriam o fluxo necessário.", y - 0.01, size=11.5, width=108, line_gap=0.044)
    save(pdf, fig)


def page_example_part2(pdf):
    r = RESULTS[0]
    fig, ax = new_page(pdf, "16. D. Exemplo completo - Sala de Produtos, Parte 2", "Verificação e carga")
    y = 0.88
    y = add_equations(ax, [r"E_{obtida}=\frac{3\times2\times3.000\times0,558\times0,75}{30,00}=251\ lux", r"P_{total}=3\times(2\times40+24,1)=312,3\ W", r"S_{total}=\frac{312,3}{0,90}=347,0\ VA", r"I=\frac{347,0}{220}=1,58\ A"], y)
    y = add_text(ax, "A iluminância obtida é recalculada com a quantidade instalada, e não com o número teórico.", y - 0.01, size=11.5, width=108, line_gap=0.045)
    add_text(ax, "Verificação: 251 lux >= 200 lux. Resultado aprovado para a premissa adotada.", y - 0.02, size=12.5, color="#1F4E78", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_example_cq(pdf):
    r = RESULTS[1]
    fig, ax = new_page(pdf, "17. D. Exemplo completo - Controle de Qualidade")
    y = 0.88
    y = add_text(ax, f'Dados: L = {r["w"]:.2f} m; C = {r["l"]:.2f} m; S = {r["s"]:.2f} m²; E = {r["e"]} lux (inspeção); teto 70%; parede 50%; Fdl = 0,75. A geometria é igual à da Sala de Produtos, então K e Fu são os mesmos; o que muda é o alvo E.', y, size=11.5, width=108, line_gap=0.045)
    y = add_equations(ax, [r"K=\frac{5,00\times6,00}{2,20\times(5,00+6,00)}=1,240", r"F_u=0,558", r"\Phi_t=\frac{500\times30,00}{0,558\times0,75}=35.873\ lm", r"N_{LU}=\frac{35.873}{2\times3.000}=5,98", r"N_{instalado}=\lceil5,98\rceil=6", r"E_{obtida}=\frac{6\times6.000\times0,558\times0,75}{30,00}=502\ lux", r"P_{total}=6\times104,1=624,6\ W\quad I=3,15\ A"], y)
    add_text(ax, "Verificação: 502 lux >= 500 lux. Aprovado, com folga pequena (ver página 22).", y - 0.01, size=12, color="#1F4E78", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_example_ban(pdf):
    r = RESULTS[2]
    fig, ax = new_page(pdf, "18. D. Exemplo completo - Banheiro/Vestiário")
    y = 0.88
    y = add_text(ax, f'Dados: L = {r["w"]:.2f} m; C = {r["l"]:.2f} m; S = {r["s"]:.2f} m²; E = {r["e"]} lux; teto 70%; parede 50%; Fdl = 0,75. Sala mais compacta, K menor, Fu menor.', y, size=11.5, width=108, line_gap=0.045)
    y = add_equations(ax, [r"K=\frac{5,23\times3,50}{2,20\times(5,23+3,50)}=\frac{18,31}{19,21}=0,953", r"F_u=0,43+\frac{0,953-0,80}{1,00-0,80}\times(0,50-0,43)=0,484", r"\Phi_t=\frac{200\times18,31}{0,484\times0,75}=10.094\ lm", r"N_{LU}=\frac{10.094}{2\times3.000}=1,68", r"N_{instalado}=\lceil1,68\rceil=2", r"E_{obtida}=\frac{2\times6.000\times0,484\times0,75}{18,31}=238\ lux", r"P_{total}=2\times104,1=208,2\ W\quad I=1,05\ A"], y)
    add_text(ax, "Verificação: 238 lux >= 200 lux. Aprovado. Observação: em banheiro, avaliar luminária com proteção adequada à umidade.", y - 0.01, size=11.5, color="#9C6500", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_example_esc(pdf):
    r = RESULTS[3]
    fig, ax = new_page(pdf, "19. D. Exemplo completo - Escritório (parede bege)")
    y = 0.88
    y = add_text(ax, f'Dados: L = {r["w"]:.2f} m; C = {r["l"]:.2f} m; S = {r["s"]:.2f} m²; E = {r["e"]} lux; teto 70%; parede BEGE 45%; Fdl = 0,75. Como 45% não existe na tabela, faz-se interpolação dupla: primeiro em K, depois entre colunas.', y, size=11.5, width=108, line_gap=0.045)
    y = add_equations(ax, [r"K=\frac{8,12\times6,00}{2,20\times(8,12+6,00)}=1,568", r"F_u(30\%)=0,54+\frac{1,568-1,50}{2,00-1,50}\times(0,61-0,54)=0,550", r"F_u(50\%)=0,61+\frac{1,568-1,50}{2,00-1,50}\times(0,68-0,61)=0,620", r"F_u(45\%)=0,550+\frac{45-30}{50-30}\times(0,620-0,550)=0,602", r"\Phi_t=\frac{250\times48,72}{0,602\times0,75}=26.973\ lm"], y)
    y = add_equations(ax, [r"N_{LU}=\frac{26.973}{2\times3.000}=4,50\ \Rightarrow\ N_{instalado}=5", r"E_{obtida}=\frac{5\times6.000\times0,602\times0,75}{48,72}=278\ lux", r"P_{total}=5\times104,1=520,5\ W\quad I=2,63\ A"], y)
    add_text(ax, "Verificação: 278 lux >= 250 lux. Aprovado.", y - 0.01, size=12, color="#1F4E78", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_all_calcs(pdf):
    fig, ax = new_page(pdf, "20. D. Cálculo resumido das quatro áreas")
    y = 0.90
    y = add_text(ax, "A tabela abaixo mostra o mesmo procedimento aplicado a todos os ambientes, sem esconder os fatores obtidos.", y, size=12, width=108, line_gap=0.045)
    rows = []
    for r in RESULTS:
        rows.append([r["name"], f'{r["k"]:.3f}', f'{r["fu"]:.3f}', f'{r["flux"]:,.0f}'.replace(",", "."), f'{r["n_theory"]:.2f}', str(r["n"]), f'{r["e_out"]:.0f}', f'{r["p"]:.1f}', f'{r["current"]:.2f}'])
    add_table(ax, ["Ambiente", "K", "Fu", "Φt [lm]", "NLU teórico", "NLU", "E obtida [lux]", "P [W]", "I [A]"], rows, bbox=(0.01, 0.44, 0.98, 0.30), fontsize=8.5)
    add_text(ax, "A quantidade de luminárias é sempre a quantidade inteira imediatamente superior ao número teórico. A iluminância obtida é recalculada depois do arredondamento.", 0.37, size=11, width=108, line_gap=0.044)
    add_text(ax, "Somente os resultados da TMS 426 foram usados. Se a lâmpada ou o reator forem substituídos, os parâmetros amarelos da planilha deverão ser atualizados.", 0.20, size=11, color="#9C6500", bold=True, width=108, line_gap=0.044)
    save(pdf, fig)


def page_verification(pdf):
    fig, ax = new_page(pdf, "21. D. Verificação e folgas")
    y = 0.90
    y = add_text(ax, "A folga mostra o quanto a iluminância obtida ultrapassou o alvo. Folga muito pequena significa risco: qualquer mudança de premissa pode derrubar o ambiente abaixo do exigido.", y, size=12, width=108, line_gap=0.045)
    rows = [
        ["Sala de Produtos", "200", "251", "+51", "+25,5%"],
        ["Controle de Qualidade", "500", "502", "+2", "+0,4%"],
        ["Banheiro/Vestiário", "200", "238", "+38", "+19,0%"],
        ["Escritório", "250", "278", "+28", "+11,2%"],
    ]
    add_table(ax, ["Ambiente", "E requerida [lux]", "E obtida [lux]", "Folga [lux]", "Folga [%]"], rows, bbox=(0.01, 0.48, 0.98, 0.28), fontsize=9.5)
    y = 0.42
    y = add_text(ax, "O Controle de Qualidade tem folga de apenas 0,4%. Ele é o ambiente mais sensível do projeto: se o Fdl mudar para 0,70 ou o fluxo da lâmpada for revisado, a quantidade pode subir de 6 para 7 luminárias.", y, size=11.5, width=108, line_gap=0.045)
    add_text(ax, "As folgas grandes (Sala de Produtos e Banheiro) são normais: elas vêm do arredondamento para cima de 2,39 -> 3 e 1,68 -> 2.", y, size=11.5, width=108, line_gap=0.045)
    save(pdf, fig)


def page_electric_logic(pdf):
    fig, ax = new_page(pdf, "22. E. Carga elétrica: por que cada conta")
    y = 0.90
    y = add_text(ax, "A potência ativa (W) soma as lâmpadas e as perdas do reator, porque ambas se transformam em calor na instalação. A potência aparente (VA) é maior que a ativa porque o reator é uma carga indutiva: ele exige corrente adicional para criar o campo magnético. Essa diferença é medida pelo fator de potência.", y, size=12, width=108, line_gap=0.047)
    y = add_equations(ax, [r"P_{total}=N_{LU}\times(2\times40+24,1)", r"S_{total}=\frac{P_{total}}{FP}=\frac{P_{total}}{0,90}", r"I=\frac{S_{total}}{220}"], y - 0.01)
    y = add_text(ax, "A corrente resultante é uma referência para as próximas etapas (condutores e proteção). Ela ainda não dimensiona o circuito: faltam método de instalação, agrupamento, queda de tensão e disjuntor.", y, size=12, width=108, line_gap=0.047)
    rows = [
        ["Sala de Produtos", "3", "312,3", "347,0", "1,58"],
        ["Controle de Qualidade", "6", "624,6", "694,0", "3,15"],
        ["Banheiro/Vestiário", "2", "208,2", "231,3", "1,05"],
        ["Escritório", "5", "520,5", "578,3", "2,63"],
        ["TOTAL", "16", "1.665,6", "1.850,7", "8,41"],
    ]
    add_table(ax, ["Ambiente", "NLU", "P [W]", "S [VA]", "I [A]"], rows, bbox=(0.01, 0.10, 0.90, 0.30), fontsize=9)
    save(pdf, fig)


def page_qdl(pdf):
    fig, ax = new_page(pdf, "23. E. Resumo por quadro de iluminação")
    y = 0.90
    y = add_quote(ax, "QDL5: Escritório; QDL6: Sala de Produto e Controle de Qualidade; QDL7: Banheiros.", "Dados iniciais do projeto, p. 2/6", y)
    rows = [
        ["QDL5", "Escritório", "5", "520,5", "2,63"],
        ["QDL6", "Sala de Produtos + CQ", "9", "936,9", "4,73"],
        ["QDL7", "Banheiro/Vestiário", "2", "208,2", "1,05"],
        ["TOTAL", "Quatro ambientes", "16", "1.665,6", "8,41"],
    ]
    add_table(ax, ["Quadro", "Ambientes", "Luminárias", "P total [W]", "I ref. [A]"], rows, bbox=(0.01, 0.50, 0.98, 0.24), fontsize=9.5)
    y = 0.44
    y = add_text(ax, "A Sala de Produtos e o Controle de Qualidade pertencem ao QDL6, mesmo que sejam ambientes diferentes. O resumo serve para levar a carga total para as etapas posteriores de circuitos, condutores e proteção.", y, size=11.5, width=108, line_gap=0.045)
    y = add_text(ax, "A corrente é uma referência calculada pela potência aparente em 220 V. O dimensionamento definitivo do circuito ainda precisa considerar método de instalação, agrupamento, queda de tensão e proteção.", y, size=11.5, width=108, line_gap=0.045)
    save(pdf, fig)


def page_sensitivity(pdf):
    fig, ax = new_page(pdf, "24. F. Sensibilidade: Fdl 0,75 versus 0,70")
    y = 0.90
    y = add_text(ax, "Se o professor exigir o fator genérico Fdl = 0,70 em vez do 0,75 de luminária comercial, o fluxo exigido aumenta e a quantidade pode mudar. A tabela recalcula os dois cenários:", y, size=12, width=108, line_gap=0.045)
    rows = [
        ["Sala de Produtos", "3", "251", "3", "234"],
        ["Controle de Qualidade", "6", "502", "7", "546"],
        ["Banheiro/Vestiário", "2", "238", "2", "222"],
        ["Escritório", "5", "278", "5", "260"],
    ]
    add_table(ax, ["Ambiente", "NLU (0,75)", "E obt. (0,75)", "NLU (0,70)", "E obt. (0,70)"], rows, bbox=(0.01, 0.50, 0.98, 0.26), fontsize=9.5)
    y = 0.44
    y = add_text(ax, "Único ambiente afetado: Controle de Qualidade, que passa de 6 para 7 luminárias. Os demais continuam aprovados, com folgas reduzidas.", y, size=11.5, width=108, line_gap=0.045)
    add_text(ax, "Na planilha, basta alterar a célula D12 da aba LUM-LUCAS para 0,70 e conferir a coluna de verificação. Essa é a vantagem de ter Fdl como premissa editável e documentada.", y, size=11.5, color="#9C6500", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


def page_spacing(pdf):
    fig, ax = new_page(pdf, "25. F. O que a planilha resolve e o que fica para o CAD")
    y = 0.90
    y = add_text(ax, "Para a planilha, as dimensões e o pé-direito da aba DADOS são suficientes para calcular área, K, Fu, fluxo, quantidade e carga.", y, size=12, width=108, line_gap=0.047)
    y = add_quote(ax, "A planta CAD não é necessária para esta etapa da planilha. Ela será usada depois para validar a disposição física.", "T1 - memorial, parte de checklist", y)
    y = add_text(ax, "A regra de espaçamento apresentada na aula é:", y, size=12, width=108, line_gap=0.045)
    y = add_equations(ax, [r"X,Y\leq1,5\times H_{lp}", r"X_1=\frac{X}{2}\qquad Y_1=\frac{Y}{2}"], y - 0.01)
    y = add_text(ax, "No momento, a aba informa a quantidade de luminárias. O desenho das fileiras, as distâncias reais às paredes, portas e obstáculos devem ser conferidos posteriormente no CAD.", y, size=11.5, width=108, line_gap=0.045)
    add_text(ax, "Se a disposição exigir uma luminária adicional, a iluminância deve ser recalculada.", y, size=11.5, color="#9C6500", bold=True, width=108, line_gap=0.045)
    save(pdf, fig)


ASSUMPTIONS = [
    "Pé-direito de 3,00 m: vem de DADOS!K11:K14 e foi considerado como altura de instalação da luminária.",
    "CLARO/CLARA: descrições qualitativas convertidas para 70% no teto e 50% na parede, colunas compatíveis da Tabela 2.9.",
    "BRANCO/BRANCA: branco-neve aparece como 80% na tabela de refletâncias, mas a Tabela 2.9 não possui coluna 80%; foi adotado o limite tabelado.",
    "BEGE: 45% vem diretamente da tabela de refletâncias e foi interpolado entre parede 30% e 50% na Tabela 2.9.",
    "Azulejo cinza: o material foi registrado, mas a Tabela 2.9 fornecida só disponibiliza valores para piso de 10%.",
    "Fdl = 0,75: corresponde à categoria de luminária comercial. Confirmar se o professor prefere o fator genérico de 0,70.",
    "Iluminâncias: as classificações são interpretações técnicas da Tabela 2.6 e devem ser mantidas no memorial.",
    "TMS 426: é a escolha de cálculo. Caso o grupo adote outra luminária, todo o Fu e os dados elétricos deverão ser substituídos.",
    "A planilha não dimensiona ainda disjuntor, condutor, queda de tensão ou distribuição interna dos circuitos.",
]


def page_assumptions_1(pdf):
    fig, ax = new_page(pdf, "26. F. Premissas e limitações - Parte 1")
    y = 0.88
    for i, item in enumerate(ASSUMPTIONS[:5], 1):
        y = add_text(ax, f"{i}. {item}", y, size=11.5, width=106, line_gap=0.046)
        y -= 0.015
    save(pdf, fig)


def page_assumptions_2(pdf):
    fig, ax = new_page(pdf, "26. F. Premissas e limitações - Parte 2")
    y = 0.88
    for i, item in enumerate(ASSUMPTIONS[5:], 6):
        y = add_text(ax, f"{i}. {item}", y, size=11.5, width=106, line_gap=0.046)
        y -= 0.015
    save(pdf, fig)


CHECKLIST = [
    "Apresente primeiro o trecho do enunciado que exige o Método dos Lumens e permite lâmpadas fluorescentes ou similares.",
    "Mostre que as quatro áreas pertencem às linhas DADOS!11:14 e que o pé-direito é 3,00 m.",
    "Explique a atividade visual e justifique E para cada ambiente pela Tabela 2.6.",
    "Mostre a origem das refletâncias e diga claramente quais valores são dados e quais são premissas.",
    "Calcule Hlp e K para cada ambiente.",
    "Mostre os dois valores vizinhos de Fu na Tabela 2.9 e faça a interpolação com números.",
    "Justifique Fdl = 0,75 e registre a alternativa Fdl = 0,70 caso seja solicitada.",
    "Use os dados da TMS 426: 2 lâmpadas, 40 W cada, 3.000 lm cada, reator de 24,1 W e FP 0,90.",
    "Calcule o fluxo, arredonde o número de luminárias para cima e recalcule a iluminância obtida.",
    "Feche com o resumo por QDL e informe que o CAD será usado apenas para confirmar a disposição física.",
]


def page_checklist_1(pdf):
    fig, ax = new_page(pdf, "27. F. Roteiro para apresentar o cálculo - Parte 1")
    y = 0.88
    for i, item in enumerate(CHECKLIST[:5], 1):
        y = add_text(ax, f"{i}. {item}", y, size=12, width=104, line_gap=0.05)
        y -= 0.01
    save(pdf, fig)


def page_checklist_2(pdf):
    fig, ax = new_page(pdf, "27. F. Roteiro para apresentar o cálculo - Parte 2")
    y = 0.88
    for i, item in enumerate(CHECKLIST[5:], 6):
        y = add_text(ax, f"{i}. {item}", y, size=12, width=104, line_gap=0.05)
        y -= 0.01
    add_text(ax, "Com essa sequência, cada resultado fica ligado a uma fonte ou a uma premissa explicitamente declarada.", 0.12, size=13, color="#1F4E78", bold=True, width=104)
    save(pdf, fig)


GLOSSARY = [
    "Fluxo luminoso (Φ): quantidade total de luz emitida por uma fonte, medida em lúmens (lm).",
    "Iluminância (E): fluxo luminoso que chega a cada metro quadrado, em lux; 1 lux = 1 lm/m².",
    "Lâmpada: a fonte de luz. Luminária: conjunto completo com carcaça, lâmpadas e acessórios.",
    "Reator: acessório da luminária que limita a corrente da lâmpada e dissipa potência (as perdas de 24,1 W).",
    "Fator de potência (FP): razão entre potência ativa (W) e aparente (VA); 0,90 no reator duplo adotado.",
    "Refletância (ρ): percentual da luz que uma superfície devolve; base para escolher a coluna da Tabela 2.9.",
    "Fator de utilização (Fu): fração do fluxo das lâmpadas que atinge o plano útil; depende de K e das refletâncias.",
    "Fator de depreciação (Fdl): corrige o fluxo por sujeira e envelhecimento; 0,75 para luminária comercial.",
    "Índice do recinto (K): proporção entre área e altura útil; define a linha da tabela a ser lida.",
    "Método dos lumens: procedimento que dimensiona o fluxo total necessário para atingir a iluminância alvo.",
]


def page_glossary(pdf):
    fig, ax = new_page(pdf, "28. F. Glossário")
    y = 0.88
    for item in GLOSSARY:
        y = add_text(ax, f"- {item}", y, size=11, width=106, line_gap=0.038)
        y -= 0.008
    add_text(ax, "Com esses dez termos, qualquer página deste memorial pode ser lida de forma independente.", 0.06, size=11.5, color="#1F4E78", bold=True, width=106)
    save(pdf, fig)


def create_pdf():
    with PdfPages(PDF_PATH) as pdf:
        page_cover(pdf)
        page_how_to_use(pdf)
        page_concepts(pdf)
        page_logic(pdf)
        page_scope(pdf)
        page_inputs(pdf)
        page_lamp_choice(pdf)
        page_tms_electric(pdf)
        page_illuminance(pdf)
        page_reflectance(pdf)
        page_read_table(pdf)
        page_geometry(pdf)
        page_k_meaning(pdf)
        page_fu(pdf)
        page_fu_calcs(pdf)
        page_fdl(pdf)
        page_example_part1(pdf)
        page_example_part2(pdf)
        page_example_cq(pdf)
        page_example_ban(pdf)
        page_example_esc(pdf)
        page_all_calcs(pdf)
        page_verification(pdf)
        page_electric_logic(pdf)
        page_qdl(pdf)
        page_sensitivity(pdf)
        page_spacing(pdf)
        page_assumptions_1(pdf)
        page_assumptions_2(pdf)
        page_checklist_1(pdf)
        page_checklist_2(pdf)
        page_glossary(pdf)


if __name__ == "__main__":
    create_pdf()
    print(PDF_PATH)
