from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def krakow_districts_kb() -> InlineKeyboardMarkup:
    """
    Крок workflow: District selection (Kraków).
    Список районів міста.
    """

    districts = [
        ("Stare Miasto", "stare-miasto"),
        ("Grzegórzki", "grzegorzki"),
        ("Prądnik Czerwony", "pradnik-czerwony"),
        ("Prądnik Biały", "pradnik-bialy"),
        ("Krowodrza", "krowodrza"),
        ("Bronowice", "bronowice"),
        ("Zwierzyniec", "zwierzyniec"),
        ("Dębniki", "debniki"),
        ("Łagiewniki–Borek Fałęcki", "lagiewniki-borek-falecki"),
        ("Swoszowice", "swoszowice"),
        ("Podgórze Duchackie", "podgorze-duchackie"),
        ("Bieżanów–Prokocim", "biezanow-prokocim"),
        ("Podgórze", "podgorze"),
        ("Czyżyny", "czyzyny"),
        ("Mistrzejowice", "mistrzejowice"),
        ("Bieńczyce", "bienczyce"),
        ("Wzgórza Krzesławickie", "wzgorza-krzeslawickie"),
        ("Nowa Huta", "nowa-huta"),
    ]

    keyboard = []
    row = []

    for idx, (label, slug) in enumerate(districts, start=1):
        row.append(
            InlineKeyboardButton(
                text=label,
                callback_data=f"district_{slug}",
            )
        )
        if idx % 2 == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
