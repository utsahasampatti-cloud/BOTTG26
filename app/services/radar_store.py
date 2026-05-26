import json
import time
import uuid
from aiogram.fsm.storage.redis import RedisStorage


def _key(user_id: int) -> str:
    return f"radars:{user_id}"


async def add_radar(
    storage: RedisStorage,
    user_id: int,
    filters: dict,
) -> str:
    radar = {
        "id": str(uuid.uuid4()),
        "filters": filters,
        "started_at": int(time.time()),
    }

    redis = storage.redis
    await redis.rpush(_key(user_id), json.dumps(radar))
    return radar["id"]


async def get_radars(
    storage: RedisStorage,
    user_id: int,
) -> list[dict]:
    redis = storage.redis
    raw = await redis.lrange(_key(user_id), 0, -1)
    return [json.loads(r) for r in raw]


async def remove_radar(
    storage: RedisStorage,
    user_id: int,
    radar_id: str,
):
    redis = storage.redis
    radars = await get_radars(storage, user_id)

    for r in radars:
        if r["id"] == radar_id:
            await redis.lrem(_key(user_id), 1, json.dumps(r))
            return True

    return False
