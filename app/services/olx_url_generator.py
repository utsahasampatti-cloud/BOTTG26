from urllib.parse import urlencode


BASE_FLATS_URL = (
    "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/krakow/"
)

BASE_ROOMS_URL = (
    "https://www.olx.pl/nieruchomosci/stancje-pokoje/krakow/"
)


ROOMSIZE_MAP = {
    "roomsize_one": ["one"],
    "roomsize_two": ["two"],
    "roomsize_three": ["three"],
    "roomsize_multi": ["two", "three"],
}

PREFERENCES_MAP = {
    "pref_women": "women",
    "pref_man": "man",
    "pref_student": "student",
    "pref_working": "working",
}


def build_olx_url(filters: dict) -> str:
    property_type = filters.get("property_type")

    if property_type == "type_room":
        return _build_rooms_url(filters)

    return _build_flats_url(filters)


def _build_flats_url(filters: dict) -> str:
    params = {}

    district = filters.get("district")
    base = BASE_FLATS_URL
    if district:
        base = f"{base}q-{district}/"

    if filters.get("price_to"):
        params["search[filter_float_price:to]"] = filters["price_to"]

    if filters.get("area_from"):
        params["search[filter_float_m:from]"] = filters["area_from"]

    params["search[order]"] = "created_at:desc"

    return _final_url(base, params)


def _build_rooms_url(filters: dict) -> str:
    params = {}

    district = filters.get("district")
    base = BASE_ROOMS_URL
    if district:
        base = f"{base}q-{district}/"

    if filters.get("price_to"):
        params["search[filter_float_price:to]"] = filters["price_to"]

    # ROOM SIZE
    roomsize = filters.get("roomsize")
    if roomsize in ROOMSIZE_MAP:
        for idx, val in enumerate(ROOMSIZE_MAP[roomsize]):
            params[f"search[filter_enum_roomsize][{idx}]"] = val

    # PREFERENCES
    preferences = filters.get("preferences", [])
    for idx, p in enumerate(preferences):
        if p in PREFERENCES_MAP:
            params[
                f"search[filter_enum_preferences][{idx}]"
            ] = PREFERENCES_MAP[p]

    if filters.get("area_from"):
        params["search[filter_float_m:from]"] = filters["area_from"]

    params["search[order]"] = "created_at:desc"

    return _final_url(base, params)


def _final_url(base: str, params: dict) -> str:
    if not params:
        return base
    return f"{base}?{urlencode(params, doseq=True)}"
