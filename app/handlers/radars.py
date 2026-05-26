from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from services.radar_store import get_radars

router = Router()


@router.callback_query(F.data == "my_radars")
async def my_radars_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    """
    Показує список збережених радарів користувача
    """

    storage = state.storage

    radars = await get_radars(
        storage,
        callback.from_user.id,
    )

    if not radars:
        await callback.answer()
        await callback.message.answer(
            "🛸 **У тебе ще немає радарів**\n\n"
            "Запусти пошук і збережи його 👀"
        )
        return

    lines = ["📡 **Мої радари:**\n"]

    for r in radars:
        f = r.get("filters", {})
        lines.append(
            f"• {f.get('city')} / {f.get('district')} / "
            f"до {f.get('price_to')} PLN"
        )

    await callback.answer()
    await callback.message.answer("\n".join(lines))
