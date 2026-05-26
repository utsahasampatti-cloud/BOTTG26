import asyncio
from pathlib import Path

from aiogram import Router, types, F
from aiogram.types import FSInputFile

from services.session_store import (
    get_next_ad,
    has_active_session,
)
from services.fast_photos import build_composite

from keyboards.ad_nav import ad_nav_kb
from keyboards.main_menu import main_menu_kb

router = Router()


# ======================================================
# INTERNAL: render one ad
# ======================================================
async def _render_ad(
    message: types.Message | types.CallbackQuery,
    ad: dict,
):
    """
    Відображає одне оголошення.
    Без побічних ефектів.
    """

    image_path = await build_composite(ad["url"])
    opis = None


    caption_parts = []
    if opis:
        caption_parts.append(opis)

    caption_parts.append(f"🔗 {ad['url']}")
    caption = "\n\n".join(caption_parts)

    if image_path and Path(image_path).exists():
        await message.answer_photo(
            FSInputFile(image_path),
            caption=caption,
            reply_markup=ad_nav_kb(),
        )
        Path(image_path).unlink(missing_ok=True)
    else:
        await message.answer(
            caption,
            reply_markup=ad_nav_kb(),
        )


# ======================================================
# NEXT AD
# ======================================================
@router.callback_query(F.data == "ad_next")
async def ad_next(callback: types.CallbackQuery, state):
    ad = await get_next_ad(state.storage, callback.from_user.id)

    if not ad:
        await callback.answer()
        await callback.message.answer(
            "🟠 Це були всі оголошення.",
            reply_markup=ad_nav_kb(show_exit=True),
        )
        return

    await callback.answer()
    await _render_ad(callback.message, ad)


# ======================================================
# RESUME BROWSING
# ======================================================
@router.callback_query(F.data == "resume_search")
async def resume_search(callback: types.CallbackQuery, state):
    if not await has_active_session(state.storage, callback.from_user.id):
        await callback.answer()
        await callback.message.answer(
            "❌ Немає активного перегляду",
            reply_markup=main_menu_kb(),
        )
        return

    await callback.answer()
    await ad_next(callback, state)
