from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states.search import SearchFSM

from keyboards.districts_krakow import krakow_districts_kb
from keyboards.property_type import property_type_kb
from keyboards.room_type import room_type_kb
from keyboards.room_preferences import room_preferences_kb
from keyboards.rooms import rooms_kb
from keyboards.pets import pets_kb
from keyboards.private_type import private_type_kb
from keyboards.main_menu import main_menu_kb

from services.district_normalizer import detect_district
from services.olx_url_generator import build_olx_url
from services.olx_http_scraper import search_olx_http
from services.session_store import start_session

from handlers.ads import ad_next

router = Router()

# ======================================================
# 1. START SEARCH
# ======================================================
@router.callback_query(F.data == "search_realestate")
async def start_search(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SearchFSM.district)

    await callback.answer()
    await callback.message.answer(
        "📍 Введи район або обери зі списку 👇",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="📍 Обрати район",
                        callback_data="district_choose",
                    )
                ]
            ]
        ),
    )

# ======================================================
# 2. DISTRICT — TEXT
# ======================================================
@router.message(SearchFSM.district)
async def district_text(message: types.Message, state: FSMContext):
    result = detect_district(message.text)

    if result["status"] == "exact":
        await state.update_data(district=result["district"])
        await state.set_state(SearchFSM.property_type)
        await message.answer(
            f"📍 Район: {result['district']}\n\n"
            "🏠 Обери тип нерухомості:",
            reply_markup=property_type_kb(),
        )
        return

    if result["status"] == "suggest":
        await message.answer(
            f"❓ Ви мали на увазі **{result['suggestion']}**?",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text=result["suggestion"],
                            callback_data=f"district_confirm:{result['suggestion']}",
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="📍 Обрати район",
                            callback_data="district_choose",
                        )
                    ],
                ]
            ),
        )
        return

    await message.answer(
        "❌ Не вдалося розпізнати район",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="📍 Обрати район",
                        callback_data="district_choose",
                    )
                ]
            ]
        ),
    )

# ======================================================
# 2. DISTRICT — CONFIRM
# ======================================================
@router.callback_query(F.data.startswith("district_confirm:"))
async def district_confirm(callback: types.CallbackQuery, state: FSMContext):
    district = callback.data.split(":", 1)[1]
    await state.update_data(district=district)
    await state.set_state(SearchFSM.property_type)

    await callback.answer()
    await callback.message.answer(
        f"📍 Район: {district}\n\n"
        "🏠 Обери тип нерухомості:",
        reply_markup=property_type_kb(),
    )

# ======================================================
# 2. DISTRICT — LIST
# ======================================================
@router.callback_query(F.data == "district_choose")
async def district_choose(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📍 Обери район:",
        reply_markup=krakow_districts_kb(),
    )

@router.callback_query(F.data.startswith("district_"))
async def district_from_list(callback: types.CallbackQuery, state: FSMContext):
    district = callback.data.replace("district_", "")
    await state.update_data(district=district)
    await state.set_state(SearchFSM.property_type)

    await callback.answer()
    await callback.message.answer(
        f"📍 Район: {district.replace('-', ' ').title()}\n\n"
        "🏠 Обери тип нерухомості:",
        reply_markup=property_type_kb(),
    )

# ======================================================
# 3. PROPERTY TYPE (BRANCH)
# ======================================================
@router.callback_query(
    SearchFSM.property_type,
    F.data.in_({"type_flat", "type_house", "type_room"})
)
async def property_type(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(property_type=callback.data)

    # ---------- BRANCH B: ROOM ----------
    if callback.data == "type_room":
        await state.set_state(SearchFSM.rooms)
        await callback.answer()
        await callback.message.answer(
            "🚪 Обери тип кімнати:",
            reply_markup=room_type_kb(),
        )
        return

    # ---------- BRANCH A: FLAT / HOUSE ----------
    await state.set_state(SearchFSM.price_to)
    await callback.answer()
    await callback.message.answer("💰 Введи максимальну ціну (PLN):")

# ======================================================
# B1. ROOM TYPE
# ======================================================
@router.callback_query(SearchFSM.rooms, F.data.startswith("roomsize_"))
async def room_type(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(roomsize=callback.data, preferences=[])
    await state.set_state(SearchFSM.preferences)

    await callback.answer()
    await callback.message.answer(
        "👥 Для кого кімната?",
        reply_markup=room_preferences_kb(),
    )

# ======================================================
# B2. ROOM PREFERENCES (MULTI)
# ======================================================
@router.callback_query(SearchFSM.preferences, F.data.startswith("pref_"))
async def add_preference(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    prefs = set(data.get("preferences", []))
    prefs.add(callback.data)

    await state.update_data(preferences=list(prefs))
    await callback.answer("➕ Додано")

@router.callback_query(SearchFSM.preferences, F.data == "prefs_done")
async def preferences_done(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SearchFSM.price_to)
    await callback.answer()
    await callback.message.answer("💰 Введи максимальну ціну (PLN):")

# ======================================================
# A1 / B3. PRICE
# ======================================================
@router.message(SearchFSM.price_to)
async def price_to(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи число")
        return

    await state.update_data(price_to=int(message.text))
    await state.set_state(SearchFSM.area_from)

    await message.answer("📐 Введи мінімальну площу (м²):")

# ======================================================
# A2 / B4. AREA
# ======================================================
@router.message(SearchFSM.area_from)
async def area_from(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введи число")
        return

    await state.update_data(area_from=int(message.text))
    data = await state.get_data()

    # ---------- BRANCH A: FLAT / HOUSE ----------
    if data.get("property_type") != "type_room":
        await state.set_state(SearchFSM.rooms)
        await message.answer(
            "🚪 Скільки кімнат?",
            reply_markup=rooms_kb(),
        )
        return

    # ---------- BRANCH B: ROOM ----------
    await state.set_state(SearchFSM.pets)
    await message.answer(
        "🐶 Можна з тваринами?",
        reply_markup=pets_kb(),
    )

# ======================================================
# A3. ROOMS (APARTMENT / HOUSE)
# ======================================================
@router.callback_query(SearchFSM.rooms, F.data.startswith("rooms_"))
async def rooms(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(rooms=callback.data)
    await state.set_state(SearchFSM.pets)

    await callback.answer()
    await callback.message.answer(
        "🐶 Можна з тваринами?",
        reply_markup=pets_kb(),
    )

# ======================================================
# A4 / B5. PETS
# ======================================================
@router.callback_query(SearchFSM.pets, F.data.startswith("pets_"))
async def pets(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(pets=callback.data)
    await state.set_state(SearchFSM.private_type)

    await callback.answer()
    await callback.message.answer(
        "👤 Тип оголошення:",
        reply_markup=private_type_kb(),
    )

# ======================================================
# A5 / B6. PRIVATE TYPE → SEARCH
# ======================================================
@router.callback_query(
    SearchFSM.private_type,
    F.data.in_({"private", "business", "all"})
)
async def private_type(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(private_type=callback.data)
    filters = await state.get_data()
    await state.clear()

    await callback.answer()
    await callback.message.answer("🔍 Шукаю оголошення…")

    ads = await search_olx_http(build_olx_url(filters))

    if not ads:
        await callback.message.answer(
            "😕 Нічого не знайдено",
            reply_markup=main_menu_kb(),
        )
        return

    await start_session(state.storage, callback.from_user.id, ads)
    await ad_next(callback, state)
