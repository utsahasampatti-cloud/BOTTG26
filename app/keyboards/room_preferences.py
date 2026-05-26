from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def room_preferences_kb() -> InlineKeyboardMarkup:
    """
    Крок workflow: Room preferences (multi-select).
    Для кого кімната.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👩 Жінки",
                    callback_data="pref_women",
                ),
                InlineKeyboardButton(
                    text="👨 Чоловіки",
                    callback_data="pref_man",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎓 Студенти",
                    callback_data="pref_student",
                ),
                InlineKeyboardButton(
                    text="💼 Працюючі",
                    callback_data="pref_working",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Готово",
                    callback_data="prefs_done",
                )
            ],
        ]
    )
