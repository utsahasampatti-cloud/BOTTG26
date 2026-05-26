from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def property_type_kb() -> InlineKeyboardMarkup:
    """
    Крок workflow: Property type.
    Вибір типу нерухомості.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏢 Квартира",
                    callback_data="type_flat",
                ),
                InlineKeyboardButton(
                    text="🏠 Будинок",
                    callback_data="type_house",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🚪 Кімната",
                    callback_data="type_room",
                )
            ],
        ]
    )
