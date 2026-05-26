import asyncio
import os
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv
from redis.asyncio import Redis

from bot import register_handlers
from services.radar_worker import radar_loop

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    redis = Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
    )

    storage = RedisStorage(redis)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    register_handlers(dp)

    asyncio.create_task(radar_loop(bot, storage))

    logging.info("🤖 Bot started. Polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
