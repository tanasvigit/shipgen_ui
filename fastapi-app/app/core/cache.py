import redis

from app.core.config import settings


_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.DB_HOST,
            port=6379,
            db=0,
            decode_responses=True,
        )
    return _redis_client



