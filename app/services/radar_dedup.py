from aiogram.fsm.storage.redis import RedisStorage


def _key(radar_id: str) -> str:
    return f"radar:seen:{radar_id}"


async def is_seen(
    storage: RedisStorage,
    radar_id: str,
    ad_url: str,
) -> bool:
    redis = storage.redis
    return await redis.sismember(_key(radar_id), ad_url)


async def mark_seen(
    storage: RedisStorage,
    radar_id: str,
    ad_url: str,
):
    redis = storage.redis
    await redis.sadd(_key(radar_id), ad_url)
