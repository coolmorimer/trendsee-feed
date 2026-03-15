# Роуты пользователей: регистрация, токен, обновление, удаление, посты юзера

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.deps import get_post_service, get_user_service
from app.schemas.post import PaginatedPostsResponse
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithToken,
)
from app.services.post import PostService
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserWithToken,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    body: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    user, token = await service.create_user(name=body.name)
    return UserWithToken(user=user, token=token)


@router.get("/{user_id}/token", response_model=TokenResponse)
async def get_token(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    token = await service.get_token(user_id)
    return TokenResponse(token=token)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.update_user(user_id, name=body.name)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    await service.delete_user(user_id)


@router.get("/{user_id}/posts", response_model=PaginatedPostsResponse)
async def get_user_posts(
    user_id: int,
    service: Annotated[PostService, Depends(get_post_service)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await service.get_user_posts(user_id, limit=limit, offset=offset)
