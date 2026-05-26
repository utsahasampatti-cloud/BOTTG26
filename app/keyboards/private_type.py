from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def private_type_kb() -> InlineKeyboardMarkup:
    """
    Крок workflow: Private / Agency.
    Вибір типу оголошення.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Приватна особа",
                    callback_data="private",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏢 Агенція",
                    callback_data="business",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 Усі оголошення",
                    callback_data="all",
                )
            ],
        ]
    )
