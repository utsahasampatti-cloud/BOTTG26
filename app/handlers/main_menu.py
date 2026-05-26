from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu_keyboard
from keyboards.start import start_keyboard

router = Router()


# ======================================================
# ENTRY: MY ACCOUNT (from /start or exit)
# ======================================================
@router.callback_query(F.data == "my_account")
async def my_account(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    await callback.message.answer(
        "👤 Мій кабінет",
        reply_markup=get_main_menu_keyboard(),
    )


# ======================================================
# GO TO MAIN MENU (from ads end)
# ======================================================
@router.callback_query(F.data == "go_main_menu")
async def go_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    await callback.message.answer(
        "👤 Мій кабінет",
        reply_markup=get_main_menu_keyboard(),
    )


# ======================================================
# FALLBACK: /start HANDLER SUPPORT
# ======================================================
async def show_start_menu(message: types.Message):
    """
    Використовується з handlers/start.py
    """
    await message.answer(
        "👋 Вітаю! Оберіть дію:",
        reply_markup=start_keyboard,
    )
