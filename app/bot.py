from aiogram import Dispatcher
from aiogram.filters import CommandStart
from handlers.balance import router as balance_router
from handlers.start import start_handler
from handlers.main_menu import router as main_menu_router
from handlers.search import router as search_router
from handlers.ads import router as ads_router
from handlers.radars import router as radars_router


def register_handlers(dp: Dispatcher):
    # /start
    dp.message.register(start_handler, CommandStart())

    # routers
    dp.include_router(main_menu_router)
    dp.include_router(search_router)
    dp.include_router(ads_router)
    dp.include_router(balance_router)
    dp.include_router(radars_router)
