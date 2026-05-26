from aiogram.fsm.storage.redis import RedisStorage

MAX_FAVORITES = 30


def _key(user_id: int) -> str:
    return f"favorites:{user_id}"


async def is_favorite(
    storage: RedisStorage,
    user_id: int,
    ad_url: str,
) -> bool:
    redis = storage.redis
    return await redis.sismember(_key(user_id), ad_url)


async def add_favorite(
    storage: RedisStorage,
    user_id: int,
    ad_url: str,
) -> bool:
    """
    Повертає:
    - True → додано
    - False → ліміт або вже є
    """
    redis = storage.redis
    key = _key(user_id)

    count = await redis.scard(key)
    if count >= MAX_FAVORITES:
        return False

    added = await redis.sadd(key, ad_url)
    return bool(added)


async def get_favorites(
    storage: RedisStorage,
    user_id: int,
) -> list[str]:
    redis = storage.redis
    return list(await redis.smembers(_key(user_id)))
