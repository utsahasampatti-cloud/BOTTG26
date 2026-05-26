from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def rooms_kb() -> InlineKeyboardMarkup:
    """
    Крок workflow: Rooms (Apartment / House).
    Кількість кімнат.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="1 кімната",
                    callback_data="rooms_1",
                ),
                InlineKeyboardButton(
                    text="2 кімнати",
                    callback_data="rooms_2",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="3 кімнати",
                    callback_data="rooms_3",
                ),
                InlineKeyboardButton(
                    text="4+ кімнати",
                    callback_data="rooms_4_plus",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Неважливо",
                    callback_data="rooms_any",
                )
            ],
        ]
    )
