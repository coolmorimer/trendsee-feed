# Pydantic-схемы для постов

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    text: str = Field(..., min_length=1)


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    text: str | None = Field(None, min_length=1)


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    author_name: str = ""
    title: str
    text: str
    created_at: datetime
    updated_at: datetime

    # ИИ подсказал model_validator — в доках pydantic v2 это не сразу нашлось,
    # нужно было аккуратно вытащить имя из связанной ORM-модели до сериализации
    @model_validator(mode="before")
    @classmethod
    def extract_author_name(cls, data):
        if hasattr(data, "user") and data.user is not None:
            data.author_name = data.user.name
        return data


class PaginatedPostsResponse(BaseModel):
    items: list[PostResponse]
    total: int
    has_more: bool
