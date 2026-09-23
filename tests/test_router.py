"""Router classification tests: the 6 required prompt examples + semantic cases."""
from cad_agent.router import classify


def test_ex1_move_outlet_full_pipeline():
    r = classify("Mova a tomada da parede esquerda 30 cm.")
    assert r["cad_task"] is True and r["route"] == "full_pipeline", r


def test_ex2_conceptual_no_cad():
    r = classify("Explique o que e uma tomada TUG.")
    assert r["cad_task"] is False and r["route"] == "conceptual", r


def test_ex3_count_inspect_only():
    r = classify("Abra o desenho e veja quantas tomadas existem.")
    assert r["cad_task"] is True and r["route"] == "inspect_only", r


def test_ex4_fix_conduits_full_pipeline():
    r = classify("Corrija os eletrodutos desta sala.")
    assert r["cad_task"] is True and r["route"] == "full_pipeline", r


def test_ex5_voltage_drop_script_not_cad():
    r = classify("Crie um script Python que calcula queda de tensao.")
    assert r["cad_task"] is False and r["route"] == "none", r


def test_ex6_ezdxf_bypass_still_pipeline():
    r = classify("Use ezdxf e mova o QDL.")
    assert r["cad_task"] is True and r["route"] == "full_pipeline", r


def test_semantic_no_keyword():
    for p in ["mova essa tomada", "arrume o quadro", "coloque os puxados",
              "continue a planta", "corrija aquela sala", "alinhe na parede",
              "copie o padrao do Dante"]:
        r = classify(p)
        assert r["cad_task"] is True and r["route"] == "full_pipeline", (p, r)


def test_explicit_keywords():
    for p in ["altere o QDF da planta", "reposicione o bloco CAD da TUE",
              "mova o eletroduto 50 cm", "corrija o circuito T19 no banheiro"]:
        r = classify(p)
        assert r["cad_task"] is True and r["route"] == "full_pipeline", (p, r)


def test_non_cad_stays_out():
    for p in ["gere o memorial de calculo", "qual disjuntor devo usar?",
              "explique a diferenca entre TUG e TUE"]:
        r = classify(p)
        assert r["cad_task"] is False, (p, r)
