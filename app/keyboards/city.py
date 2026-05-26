from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

KRAKOW_DISTRICTS = [
    "stare-miasto",
    "grzegorzki",
    "pradnik-czerwony",
    "pradnik-bialy",
    "krowodrza",
    "bronowice",
    "zwierzyniec",
    "debniki",
    "lagiewniki-borek-falecki",
    "swoszowice",
    "podgorze-duchackie",
    "biezanow-prokocim",
    "podgorze",
    "czyzyny",
    "mistrzejowice",
    "bienczyce",
    "wzgorza-krzeslawickie",
    "nowa-huta",
]


def _humanize(slug: str) -> str:
    return slug.replace("-", " ").title()


def krakow_districts_kb() -> InlineKeyboardMarkup:
    keyboard = []
    row = []

    for d in KRAKOW_DISTRICTS:
        row.append(
            InlineKeyboardButton(
                text=_humanize(d),
                callback_data=f"district_{d}",
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def city_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Краків",
                    callback_data="city_krakow",
                )
            ]
        ]
    )
