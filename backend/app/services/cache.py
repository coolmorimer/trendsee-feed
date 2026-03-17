# Централизованный сервис кэширования Redis.
# Ключи: user:{id}:posts:{limit}:{offset} и feed:posts:{limit}:{offset}
# TTL = 10 минут (по ТЗ)

import json

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


class CacheService:

    def __init__(self, client: redis.Redis):
        self.client = client

    @staticmethod
    def _posts_key(user_id: int, limit: int, offset: int) -> str:
        return f"user:{user_id}:posts:{limit}:{offset}"

    @staticmethod
    def _posts_pattern(user_id: int) -> str:
        return f"user:{user_id}:posts:*"

    async def get_user_posts(
        self, user_id: int, limit: int, offset: int
    ) -> dict | None:
        key = self._posts_key(user_id, limit, offset)
        data = await self.client.get(key)
        if data is None:
            return None
        return json.loads(data)

    async def set_user_posts(
        self, user_id: int, limit: int, offset: int, payload: dict
    ) -> None:
        key = self._posts_key(user_id, limit, offset)
        await self.client.set(key, json.dumps(payload, default=str), ex=settings.CACHE_TTL)

    async def invalidate_user_posts(self, user_id: int) -> None:
        # ИИ помог с этим паттерном — сам бы долго ковырялся с SCAN/cursor логикой,
        # KEYS нельзя в проде (блокирует весь редис), поэтому SCAN
        pattern = self._posts_pattern(user_id)
        cursor = 0
        while True:
            cursor, keys = await self.client.scan(cursor, match=pattern, count=100)
            if keys:
                await self.client.delete(*keys)
            if cursor == 0:
                break
        # сбрасываем и общую ленту, потому что пост пользователя входит в feed
        await self.invalidate_feed()

    @staticmethod
    def _feed_key(limit: int, offset: int) -> str:
        return f"feed:posts:{limit}:{offset}"

    async def get_feed_posts(self, limit: int, offset: int) -> dict | None:
        data = await self.client.get(self._feed_key(limit, offset))
        if data is None:
            return None
        return json.loads(data)

    async def set_feed_posts(self, limit: int, offset: int, payload: dict) -> None:
        await self.client.set(
            self._feed_key(limit, offset),
            json.dumps(payload, default=str),
            ex=settings.CACHE_TTL,
        )

    async def invalidate_feed(self) -> None:
        cursor = 0
        while True:
            cursor, keys = await self.client.scan(cursor, match="feed:posts:*", count=100)
            if keys:
                await self.client.delete(*keys)
            if cursor == 0:
                break
