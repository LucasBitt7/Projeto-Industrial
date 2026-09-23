"""Semantic CAD intent router. Deterministic classifier: prompt -> routing decision.

Keywords alone are NOT enough: the router combines
  (a) CAD entity/file nouns, (b) action verbs (PT/EN), (c) conceptual-question guards,
  (d) non-CAD engineering guards (pure calc scripts), (e) explicit tool-bypass attempts.
"""
from __future__ import annotations

import re

# (a) nouns: files, entities, disciplines
NOUN_PATTERNS = [
    r"\.dwg\b", r"\.dxf\b", r"autocad", r"\bqcad\b", r"\bdxf\b", r"\bdwg\b",
    r"planta(?:s)?(?:\s+(?:el[eé]trica|baixa|alta|luminot[eé]cnica))?",
    r"luminot[eé]cnico", r"eletroduto", r"eletrocalha", r"\bqdl\b", r"\bqdf\b",
    r"\btug\b", r"\btue\b", r"\btom(?:ada)?s?\b", r"circuito", r"puxados?",
    r"bloco(?:s)?\s+(?:cad|do\s+desenho)", r"\bcallout\b", r"\bchamada\b",
    r"quadro(?:s)?(?:\s+de\s+(?:cargas?|distribui[çc][ãa]o|for[çc]a))?",
    r"eixo\s+do\s+eletroduto", r"diagrama\s+unifilar",
]

# (b) action verbs applied to a drawing/entity (PT/EN, inflected stems)
VERB_PATTERNS = [
    r"mov(?:a|er|endo|e\b)", r"desloc(?:a|ar)", r"arrum(?:a|ar|e)", r"corri(?:gir|ja|gindo|ge)",
    r"colo(?:car|que|cado)", r"reposicion(?:ar|a|e)", r"alinh(?:ar|e|a|ado|a(?:mento)?)",
    r"copi(?:ar|e|a)\b.*(?:padr[ãa]o|bloco|tomada|quadro|sala)",
    r"continu(?:ar|e|a)\b.*(?:planta|desenho|sala)",
    r"rot(?:ear|acionar)", r"ins[ei]r(?:ir|a|e)\b", r"desenh(?:ar|e|a)\b",
    r"conect(?:ar|e)\b", r"rote(?:ar|e)\b", r"alter(?:ar|a|e)\b.*(?:planta|desenho|tomada|circuito|quadro)",
    r"abra\s+o\s+desenho", r"quantas?\s+tomadas", r"cont(?:ar|e|agem)\b.*tomadas",
    r"use\s+ezdxf.*(?:mova|altere|edite|corrija|desenhe|insira)",
    r"\bmove\b", r"\breposition\b", r"\balign\b",
]

# (c) conceptual-question guards: asking ABOUT, not acting ON
CONCEPTUAL_PATTERNS = [
    r"^(o\s+que\s+[ée]|explique|qual\s+a\s+diferen[çc]a|para\s+que\s+serve|como\s+funciona)",
    r"\bo\s+que\s+[ée]\b.{0,60}\?",
    r"^(me\s+explique|explique\s+o\s+que)",
]

# (d) non-CAD engineering: pure calculation/scripting without drawing action
NON_CAD_ENGINEERING = [
    r"script\s+(?:python\s+)?(?:que\s+)?calcul",
    r"calcul(?:ar|e|o)\s+.*(?:queda\s+de\s+tens[ãa]o|corrente|demanda|carga)",
    r"memorial\s+de\s+c[áa]lculo",
    r"dimension(?:ar|amento)\s+de\s+(?:cabos?|condutores?|disjuntores?)\b(?!\s+na\s+planta)",
]

EDIT_VERBS = [  # subset of VERB_PATTERNS that imply drawing MODIFICATION
    r"mov(?:a|er|endo|e\b)", r"desloc(?:a|ar)", r"arrum(?:a|ar|e)", r"corri(?:gir|ja|gindo|ge)",
    r"colo(?:car|que|cado)", r"reposicion(?:ar|a|e)", r"alinh(?:ar|e|a|ado)",
    r"copi(?:ar|e|a)", r"continu(?:ar|e|a)", r"rot(?:ear|acionar)", r"ins[ei]r(?:ir|a|e)",
    r"desenh(?:ar|e|a)", r"conect(?:ar|e)", r"rote(?:ar|e)", r"alter(?:ar|a|e)",
    r"\bmove\b", r"\breposition\b", r"\balign\b",
]


def _hits(text: str, patterns: list) -> list:
    return [p for p in patterns if re.search(p, text, re.IGNORECASE)]


def classify(prompt: str) -> dict:
    """Return {cad_task, route, confidence, reasons}.

    route: 'none' | 'inspect_only' | 'full_pipeline' | 'conceptual'
    """
    t = (prompt or "").strip()
    tl = t.lower()
    nouns = _hits(tl, NOUN_PATTERNS)
    verbs = _hits(tl, VERB_PATTERNS)
    edit_verbs = _hits(tl, EDIT_VERBS)
    conceptual = _hits(tl, CONCEPTUAL_PATTERNS)
    noncad = _hits(tl, NON_CAD_ENGINEERING)

    # Explicit bypass attempt ("use ezdxf e mova...") is still a CAD edit task:
    # bypass phrasing does not change routing; modification intent wins.
    is_question = tl.rstrip().endswith("?") or bool(conceptual)

    reasons = []
    if nouns:
        reasons.append(f"cad_nouns:{len(nouns)}")
    if verbs:
        reasons.append(f"cad_verbs:{len(verbs)}")
    if conceptual:
        reasons.append("conceptual_guard")
    if noncad:
        reasons.append("noncad_engineering_guard")

    # (d) pure engineering calc/scripts with no drawing modification -> not CAD
    if noncad and not edit_verbs and not re.search(r"\.dxf|\.dwg|planta|desenho", tl):
        return {"cad_task": False, "route": "none", "confidence": 0.9,
                "reasons": reasons + ["engineering_calc_no_drawing_action"]}

    # (c) conceptual question even if it names a CAD entity -> answer, no pipeline
    if conceptual and not edit_verbs:
        return {"cad_task": False, "route": "conceptual", "confidence": 0.9,
                "reasons": reasons + ["conceptual_question"]}

    if not nouns and not verbs:
        return {"cad_task": False, "route": "none", "confidence": 0.95, "reasons": reasons + ["no_cad_signals"]}

    # Read-only signals without modification verbs -> inspector only
    readonly = bool(re.search(r"quantas?|cont(?:ar|e|agem)|liste|mostre|veja|abra\s+o\s+desenho|verifique\s+quant", tl))
    if (nouns or verbs) and not edit_verbs:
        if readonly or re.search(r"abra\s+o\s+desenho", tl):
            return {"cad_task": True, "route": "inspect_only", "confidence": 0.85, "reasons": reasons + ["read_only"]}
        # nouns only, no verb: ambiguous mention -> still route to inspector (cheap, safe)
        if nouns and not verbs:
            return {"cad_task": True, "route": "inspect_only", "confidence": 0.6,
                    "reasons": reasons + ["noun_mention_no_action"]}
        return {"cad_task": True, "route": "inspect_only", "confidence": 0.7, "reasons": reasons + ["no_edit_verb"]}

    if edit_verbs and (nouns or verbs):
        conf = 0.95 if nouns else 0.8  # semantic cases like "arrume o quadro" need no keyword AutoCAD
        return {"cad_task": True, "route": "full_pipeline", "confidence": conf,
                "reasons": reasons + ["modification_intent"]}

    return {"cad_task": True, "route": "inspect_only", "confidence": 0.55, "reasons": reasons + ["fallback_inspect"]}


def pipeline_for(route: str) -> list:
    if route == "full_pipeline":
        return ["cad-inspector", "plan_manifest", "cad-executor(dry_run→execute+readback)", "cad-validator", "completion_gate"]
    if route == "inspect_only":
        return ["cad-inspector"]
    return []
