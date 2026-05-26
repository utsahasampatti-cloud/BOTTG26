import re
from difflib import get_close_matches


# ======================================================
# CANONICAL DISTRICTS (slug -> human name)
# ======================================================

DISTRICTS = {
    "stare-miasto": "Stare Miasto",
    "grzegorzki": "Grzegórzki",
    "pradnik-czerwony": "Prądnik Czerwony",
    "pradnik-bialy": "Prądnik Biały",
    "krowodrza": "Krowodrza",
    "bronowice": "Bronowice",
    "zwierzyniec": "Zwierzyniec",
    "debniki": "Dębniki",
    "lagiewniki-borek-falecki": "Łagiewniki–Borek Fałęcki",
    "swoszowice": "Swoszowice",
    "podgorze-duchackie": "Podgórze Duchackie",
    "biezanow-prokocim": "Bieżanów–Prokocim",
    "podgorze": "Podgórze",
    "czyzyny": "Czyżyny",
    "mistrzejowice": "Mistrzejowice",
    "bienczyce": "Bieńczyce",
    "wzgorza-krzeslawickie": "Wzgórza Krzesławickie",
    "nowa-huta": "Nowa Huta",
}


# ======================================================
# NORMALIZATION
# ======================================================

def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = text.replace("ł", "l")
    text = text.replace("ś", "s")
    text = text.replace("ż", "z")
    text = text.replace("ź", "z")
    text = text.replace("ć", "c")
    text = text.replace("ń", "n")
    text = text.replace("ą", "a")
    text = text.replace("ę", "e")
    text = text.replace("ó", "o")
    return text


# ======================================================
# PUBLIC API
# ======================================================

def detect_district(text: str) -> dict:
    """
    Detect district from user text input.
    Contract:
      - exact   → {"status": "exact", "district": "<slug>"}
      - suggest → {"status": "suggest", "suggestion": "<slug>"}
      - none    → {"status": "none"}
    """

    if not text:
        return {"status": "none"}

    norm = _normalize(text)

    # exact match (slug or name)
    for slug, name in DISTRICTS.items():
        if norm == slug or norm == _normalize(name):
            return {"status": "exact", "district": slug}

    # partial contains (e.g. "podgorze")
    for slug, name in DISTRICTS.items():
        if norm in slug or norm in _normalize(name):
            return {"status": "exact", "district": slug}

    # fuzzy suggest
    candidates = list(DISTRICTS.keys())
    matches = get_close_matches(norm, candidates, n=1, cutoff=0.6)
    if matches:
        return {"status": "suggest", "suggestion": matches[0]}

    return {"status": "none"}
