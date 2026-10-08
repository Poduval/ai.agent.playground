import fakeredis.aioredis
import pytest

from calculator_agent.memory import InMemoryStore, RedisStore, get_store


@pytest.fixture(params=["memory", "redis"])
def store(request):
    if request.param == "memory":
        return InMemoryStore(max_messages=3)
    return RedisStore(fakeredis.aioredis.FakeRedis(decode_responses=True), max_messages=3, ttl_seconds=60)


async def test_history_roundtrip_and_isolation(store):
    await store.append("s1", "user", "hi")
    await store.append("s2", "user", "other")
    assert await store.history("s1") == [{"role": "user", "content": "hi"}]


async def test_history_is_capped(store):
    for i in range(5):
        await store.append("s", "user", str(i))
    assert [m["content"] for m in await store.history("s")] == ["2", "3", "4"]


async def test_clear(store):
    await store.append("s", "user", "x")
    await store.clear("s")
    assert await store.history("s") == []


def test_get_store_defaults_to_memory():
    assert isinstance(get_store(), InMemoryStore)
