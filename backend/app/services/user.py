# Бизнес-логика пользователей: регистрация, токены, обновление, удаление

from app.core.security import create_access_token
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse
from fastapi import HTTPException, status


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, name: str) -> tuple[UserResponse, str]:
        user = await self.repository.create(name=name)
        token = create_access_token(user.id)
        return UserResponse.model_validate(user), token

    async def get_user_or_404(self, user_id: int):
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.get_user_or_404(user_id)
        return UserResponse.model_validate(user)

    async def get_token(self, user_id: int) -> str:
        user = await self.get_user_or_404(user_id)
        return create_access_token(user.id)

    async def update_user(self, user_id: int, name: str) -> UserResponse:
        user = await self.get_user_or_404(user_id)
        user = await self.repository.update(user, name=name)
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user_or_404(user_id)
        await self.repository.delete(user)
