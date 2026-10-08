"""Short-term conversation memory keyed by session id.

Both stores keep the latest N chat messages (`{"role": ..., "content": ...}`).
Redis adds persistence across restarts and sharing between processes.
"""

import json
from collections import defaultdict, deque
from typing import Protocol

from calculator_agent.config import Settings, get_settings


class MemoryStore(Protocol):
    async def history(self, session_id: str) -> list[dict]: ...
    async def append(self, session_id: str, role: str, content: str) -> None: ...
    async def clear(self, session_id: str) -> None: ...


class InMemoryStore:
    """Dictionary-backed memory. Lost when the process stops."""

    def __init__(self, max_messages: int = 20):
        self._sessions: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_messages))

    async def history(self, session_id: str) -> list[dict]:
        return list(self._sessions[session_id])

    async def append(self, session_id: str, role: str, content: str) -> None:
        self._sessions[session_id].append({"role": role, "content": content})

    async def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


class RedisStore:
    """One Redis list per session: RPUSH to add, LTRIM to cap, EXPIRE to forget idle chats."""

    def __init__(self, client, max_messages: int = 20, ttl_seconds: int = 3600):
        self._redis = client  # a redis.asyncio.Redis (or a compatible fake in tests)
        self._max = max_messages
        self._ttl = ttl_seconds

    @staticmethod
    def _key(session_id: str) -> str:
        return f"calculator_agent:memory:{session_id}"

    async def history(self, session_id: str) -> list[dict]:
        items = await self._redis.lrange(self._key(session_id), 0, -1)
        return [json.loads(item) for item in items]

    async def append(self, session_id: str, role: str, content: str) -> None:
        key = self._key(session_id)
        await self._redis.rpush(key, json.dumps({"role": role, "content": content}))
        await self._redis.ltrim(key, -self._max, -1)
        await self._redis.expire(key, self._ttl)

    async def clear(self, session_id: str) -> None:
        await self._redis.delete(self._key(session_id))


def get_store(settings: Settings | None = None) -> MemoryStore:
    """Redis if REDIS_URL is configured, otherwise a process-local store."""
    settings = settings or get_settings()
    if settings.redis_url:
        import redis.asyncio as redis

        client = redis.from_url(settings.redis_url, decode_responses=True)
        return RedisStore(client, settings.memory_max_messages, settings.memory_ttl_seconds)
    return InMemoryStore(settings.memory_max_messages)
