# DI-цепочка: session -> repository -> service
# ИИ помог выстроить эту структуру — сам бы всё в роутерах инлайнил,
# но так проще тестировать и подменять зависимости

from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.db.session import get_async_session
from app.repositories.post import PostRepository
from app.repositories.user import UserRepository
from app.services.cache import CacheService
from app.services.post import PostService
from app.services.user import UserService

security_scheme = HTTPBearer()

# глобальный пул редиса, создаётся один раз
_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        settings = get_settings()
        _redis_pool = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_pool


async def close_redis():
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None


# -- Репозитории --

def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    return UserRepository(session)


def get_post_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PostRepository:
    return PostRepository(session)


# -- Сервисы --

def get_cache_service(
    redis: Annotated[aioredis.Redis, Depends(get_redis)],
) -> CacheService:
    return CacheService(client=redis)


def get_user_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository=repo)


def get_post_service(
    repo: Annotated[PostRepository, Depends(get_post_repository)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> PostService:
    return PostService(repository=repo, cache=cache)


# -- Авторизация: достаём user_id из Bearer-токена --

async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
) -> int:
    return decode_access_token(credentials.credentials)
