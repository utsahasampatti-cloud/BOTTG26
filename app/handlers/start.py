from aiogram.types import Message, FSInputFile
from pathlib import Path

from keyboards.start import start_keyboard

BASE_DIR = Path(__file__).resolve().parent.parent
PHOTO_PATH = BASE_DIR / "images" / "welcome.png"

GREETING_TEXT = (
    "Привіт! 👋 Я **Звідусіль Бот** 🐝\n\n"
    "Я допоможу знайти житло в Польщі 🇵🇱\n\n"
    "Обери, з чого почнемо 👇"
)


async def start_handler(message: Message):
    if PHOTO_PATH.exists():
        await message.answer_photo(
            photo=FSInputFile(PHOTO_PATH),
            caption=GREETING_TEXT,
            reply_markup=start_keyboard,
        )
    else:
        await message.answer(
            GREETING_TEXT,
            reply_markup=start_keyboard,
        )
