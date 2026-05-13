"""PulseStack AI — Redis Client."""

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=50,
)


async def get_redis() -> redis.Redis:
    """FastAPI dependency — returns the async Redis client."""
    return redis_client
