import json
from aiogram.fsm.storage.redis import RedisStorage


def _ads_key(user_id: int) -> str:
    return f"olx:ads:{user_id}"


def _idx_key(user_id: int) -> str:
    return f"olx:ads:index:{user_id}"


def format_ad(ad: dict) -> str:
    return (
        f"🏠 {ad.get('area_m2', '-')}\n"
        f"💰 {ad.get('price', '-')}\n"
        f"🔗 {ad.get('url')}"
    )


async def save_ads(storage: RedisStorage, user_id: int, ads: list[dict]):
    redis = storage.redis
    await redis.set(_ads_key(user_id), json.dumps(ads))
    await redis.set(_idx_key(user_id), 0)


async def get_current_ad(storage: RedisStorage, user_id: int) -> dict | None:
    redis = storage.redis
    raw = await redis.get(_ads_key(user_id))

    if not raw:
        return None

    ads = json.loads(raw)
    idx = int(await redis.get(_idx_key(user_id)) or 0)

    if idx >= len(ads):
        return None

    return ads[idx]


async def next_ad(storage: RedisStorage, user_id: int) -> dict | None:
    redis = storage.redis

    raw = await redis.get(_ads_key(user_id))
    if not raw:
        return None

    ads = json.loads(raw)
    idx = int(await redis.get(_idx_key(user_id)) or 0)

    # ⛔ нічого більше нема
    if idx >= len(ads):
        return None

    ad = ads[idx]

    # 👉 рухаємо індекс ПІСЛЯ отримання
    await redis.set(_idx_key(user_id), idx + 1)

    return ad
