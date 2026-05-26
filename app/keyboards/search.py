from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def property_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏢 Квартира", callback_data="type_flat"),
                InlineKeyboardButton(text="🏠 Будинок", callback_data="type_house"),
            ]
        ]
    )
