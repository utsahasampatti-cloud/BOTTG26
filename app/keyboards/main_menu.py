from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard(city_name: str | None = None) -> InlineKeyboardMarkup:
    """
    Головне меню (кабінет користувача).
    city_name залишено для сумісності з handlers/main_menu.py
    """

    keyboard = [
        [
            InlineKeyboardButton(
                text="🏠 Пошук нерухомості",
                callback_data="search_realestate",
            )
        ],
        [
            InlineKeyboardButton(
                text="⏯ Продовжити перегляд",
                callback_data="resume_search",
            )
        ],
        [
            InlineKeyboardButton(
                text="📡 Мої радари",
                callback_data="my_radars",
            )
        ],
        [
            InlineKeyboardButton(
                text="💰 Поповнити баланс",
                callback_data="topup_balance",
            )
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# backward compatibility
def main_menu_kb(city_name: str | None = None) -> InlineKeyboardMarkup:
    return get_main_menu_keyboard(city_name)
