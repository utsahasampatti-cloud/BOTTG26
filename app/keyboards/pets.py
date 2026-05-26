from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def pets_kb() -> InlineKeyboardMarkup:
    """
    Крок workflow: Pets.
    Вибір — можна чи не можна з тваринами.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🐶 З тваринами",
                    callback_data="pets_yes",
                ),
                InlineKeyboardButton(
                    text="🚫 Без тварин",
                    callback_data="pets_no",
                ),
            ]
        ]
    )
