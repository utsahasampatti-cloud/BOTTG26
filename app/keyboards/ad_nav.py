from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ad_nav_kb(show_exit: bool = False) -> InlineKeyboardMarkup:
    """
    Навігація під час перегляду оголошень.
    """

    keyboard = [
        [
            InlineKeyboardButton(
                text="➡️ Наступне",
                callback_data="ad_next",
            )
        ]
    ]

    if show_exit:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="⬅️ Мій кабінет",
                    callback_data="go_main_menu",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
