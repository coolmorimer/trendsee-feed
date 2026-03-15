# Роуты постов: лента, создание (нужен токен), редактирование, удаление

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.deps import get_current_user_id, get_post_service
from app.schemas.post import PaginatedPostsResponse, PostCreate, PostResponse, PostUpdate
from app.services.post import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("", response_model=PaginatedPostsResponse)
async def get_all_posts(
    service: Annotated[PostService, Depends(get_post_service)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await service.get_all_posts(limit=limit, offset=offset)


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    body: PostCreate,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    service: Annotated[PostService, Depends(get_post_service)],
):
    return await service.create_post(
        user_id=current_user_id, title=body.title, text=body.text
    )


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    body: PostUpdate,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    service: Annotated[PostService, Depends(get_post_service)],
):
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )
    return await service.update_post(
        post_id=post_id, current_user_id=current_user_id, **update_data
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    service: Annotated[PostService, Depends(get_post_service)],
):
    await service.delete_post(post_id=post_id, current_user_id=current_user_id)
