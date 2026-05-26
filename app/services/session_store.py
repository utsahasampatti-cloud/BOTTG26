import json
from aiogram.fsm.storage.redis import RedisStorage


# ======================================================
# KEYS
# ======================================================

def _session_key(user_id: int) -> str:
    return f"session:{user_id}"


# ======================================================
# PUBLIC API
# ======================================================

async def start_session(
    storage: RedisStorage,
    user_id: int,
    ads: list[dict],
):
    """
    Стартує нову browsing-сесію.
    Повністю перезаписує попередню.
    """
    redis = storage.redis

    payload = {
        "ads": json.dumps(ads),
        "index": 0,
        "active": 1,
    }

    await redis.hset(_session_key(user_id), mapping=payload)


async def has_active_session(
    storage: RedisStorage,
    user_id: int,
) -> bool:
    redis = storage.redis
    return await redis.hget(_session_key(user_id), "active") == "1"


async def get_next_ad(
    storage: RedisStorage,
    user_id: int,
) -> dict | None:
    redis = storage.redis
    key = _session_key(user_id)

    raw_ads = await redis.hget(key, "ads")
    if not raw_ads:
        await redis.delete(key)
        return None

    try:
        ads = json.loads(raw_ads)
    except json.JSONDecodeError:
        await redis.delete(key)
        return None

    idx_raw = await redis.hget(key, "index")
    idx = int(idx_raw) if idx_raw and idx_raw.isdigit() else 0

    if idx >= len(ads):
        await redis.delete(key)
        return None

    ad = ads[idx]
    await redis.hincrby(key, "index", 1)
    return ad
