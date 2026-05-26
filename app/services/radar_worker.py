import asyncio
import logging
import time

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage

from services.radar_store import get_radars
from services.radar_dedup import is_seen, mark_seen
from services.olx_url_generator import build_olx_url
from services.olx_search import search_olx_ads

logger = logging.getLogger(__name__)


SCAN_INTERVAL = 300  # 5 хв


async def radar_loop(bot: Bot, storage: RedisStorage):
    logger.info("📡 Radar worker started")

    while True:
        try:
            # ⚠️ беремо ВСІ ключі radars:*
            redis = storage.redis
            keys = await redis.keys("radars:*")

            for key in keys:
                user_id = int(key.split(":")[1])
                radars = await get_radars(storage, user_id)

                for radar in radars:
                    radar_id = radar["id"]
                    filters = radar["filters"]
                    started_at = radar["started_at"]

                    try:
                        url = build_olx_url(filters)
                        ads = await search_olx_ads(url)
                    except Exception:
                        logger.exception("Radar search failed")
                        continue

                    for ad in ads:
                        ad_url = ad.get("url")
                        created_at = ad.get("created_at")

                        if not ad_url or not created_at:
                            continue

                        if created_at <= started_at:
                            continue

                        if await is_seen(storage, radar_id, ad_url):
                            continue

                        await mark_seen(storage, radar_id, ad_url)

                        await bot.send_message(
                            user_id,
                            "📡 Знайдено нове оголошення!\n" f"🔗 {ad_url}",
                        )

                        # rate limit
                        await asyncio.sleep(1)

            await asyncio.sleep(SCAN_INTERVAL)

        except Exception:
            logger.exception("Radar loop crashed")
            await asyncio.sleep(10)
