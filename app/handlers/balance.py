from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from services.balance_store import add_balance

router = Router()


@router.callback_query(F.data == "topup_balance")
async def topup_balance_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    """
    MVP: просто додаємо баланс користувачу
    """

    storage = state.storage

    await add_balance(
        storage,
        callback.from_user.id,
        amount=3,  # умовно +3 пошуки
    )

    await callback.answer()
    await callback.message.answer(
        "💰 **Баланс поповнено!**\n\n"
        "Додано **+3 пошуки** ✅\n\n"
        "Можеш продовжувати пошук 🐝"
    )
