from aiogram.fsm.storage.redis import RedisStorage


def _key(user_id: int) -> str:
    return f"balance:{user_id}"


async def get_balance(storage: RedisStorage, user_id: int) -> int:
    redis = storage.redis
    value = await redis.get(_key(user_id))
    return int(value or 0)


async def add_balance(
    storage: RedisStorage,
    user_id: int,
    amount: int,
):
    redis = storage.redis
    await redis.incrby(_key(user_id), amount)


async def consume_balance(
    storage: RedisStorage,
    user_id: int,
    amount: int = 1,
) -> bool:
    """
    True  -> баланс зменшено
    False -> недостатньо балансу
    """
    redis = storage.redis
    key = _key(user_id)

    current = int(await redis.get(key) or 0)
    if current < amount:
        return False

    await redis.decrby(key, amount)
    return True
