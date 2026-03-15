# Бизнес-логика постов: CRUD + кэширование через Redis

import asyncio

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.repositories.post import PostRepository
from app.schemas.post import PaginatedPostsResponse, PostResponse
from app.services.cache import CacheService

settings = get_settings()


class PostService:
    def __init__(self, repository: PostRepository, cache: CacheService):
        self.repository = repository
        self.cache = cache

    async def create_post(
        self, user_id: int, title: str, text: str
    ) -> PostResponse:
        post = await self.repository.create(user_id=user_id, title=title, text=text)
        # сбрасываем кэш после создания, иначе лента не обновится
        await self.cache.invalidate_user_posts(user_id)
        return PostResponse.model_validate(post)

    async def update_post(
        self, post_id: int, current_user_id: int, **kwargs
    ) -> PostResponse:
        post = await self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        # редактировать можно только свои посты
        if post.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own posts",
            )
        post = await self.repository.update(post, **kwargs)
        await self.cache.invalidate_user_posts(current_user_id)
        return PostResponse.model_validate(post)

    async def delete_post(self, post_id: int, current_user_id: int) -> None:
        post = await self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        if post.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own posts",
            )
        await self.repository.delete(post)
        await self.cache.invalidate_user_posts(current_user_id)

    async def get_all_posts(
        self, limit: int = 20, offset: int = 0
    ) -> PaginatedPostsResponse:
        # сначала пробуем из кэша
        cached = await self.cache.get_feed_posts(limit, offset)
        if cached is not None:
            return PaginatedPostsResponse(**cached)

        # кэша нет — имитируем медленный запрос (по ТЗ нужна задержка 2с)
        await asyncio.sleep(settings.SLOW_DB_DELAY)

        posts, total = await self.repository.get_all(limit=limit, offset=offset)
        has_more = (offset + limit) < total
        items = [PostResponse.model_validate(p) for p in posts]

        response = PaginatedPostsResponse(
            items=items, total=total, has_more=has_more
        )
        await self.cache.set_feed_posts(
            limit, offset, response.model_dump(mode="json")
        )
        return response

    async def get_user_posts(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> PaginatedPostsResponse:
        cached = await self.cache.get_user_posts(user_id, limit, offset)
        if cached is not None:
            return PaginatedPostsResponse(**cached)

        # кэша нет — задержка перед запросом
        await asyncio.sleep(settings.SLOW_DB_DELAY)

        posts, total = await self.repository.get_by_user_id(
            user_id, limit=limit, offset=offset
        )
        has_more = (offset + limit) < total
        items = [PostResponse.model_validate(p) for p in posts]

        response = PaginatedPostsResponse(
            items=items, total=total, has_more=has_more
        )
        await self.cache.set_user_posts(
            user_id, limit, offset, response.model_dump(mode="json")
        )
        return response
