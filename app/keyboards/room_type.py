from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def room_type_kb() -> InlineKeyboardMarkup:
    """
    Крок workflow: Room type (stancja / pokój).
    Тип кімнати.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛏 Одномісна",
                    callback_data="roomsize_one",
                ),
                InlineKeyboardButton(
                    text="🛏🛏 Двомісна",
                    callback_data="roomsize_two",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🛏🛏🛏 Тримісна",
                    callback_data="roomsize_three",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Кілька / комбінована",
                    callback_data="roomsize_multi",
                )
            ],
        ]
    )
