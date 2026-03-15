# Репозиторий постов.
# ИИ подсказал комбо joinedload + unique().scalars() —
# без unique() SQLAlchemy ругается на дубли при eager-лоаде связей

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.post import Post


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, title: str, text: str) -> Post:
        post = Post(user_id=user_id, title=title, text=text)
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        # перезапрашиваем с joinedload чтобы в ответе было имя автора
        query = select(Post).options(joinedload(Post.user)).where(Post.id == post.id)
        result = await self.session.execute(query)
        return result.unique().scalars().first()

    async def get_all(
        self, limit: int = 20, offset: int = 0
    ) -> tuple[list[Post], int]:
        # сначала считаем общее кол-во, потом тянем страницу
        count_query = select(func.count()).select_from(Post)
        total = (await self.session.execute(count_query)).scalar() or 0

        query = (
            select(Post)
            .options(joinedload(Post.user))
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        posts = list(result.unique().scalars().all())
        return posts, total

    async def get_by_id(self, post_id: int) -> Post | None:
        query = select(Post).options(joinedload(Post.user)).where(Post.id == post_id)
        result = await self.session.execute(query)
        return result.unique().scalars().first()

    async def get_by_user_id(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> tuple[list[Post], int]:
        count_query = (
            select(func.count()).select_from(Post).where(Post.user_id == user_id)
        )
        total = (await self.session.execute(count_query)).scalar() or 0

        query = (
            select(Post)
            .options(joinedload(Post.user))
            .where(Post.user_id == user_id)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        posts = list(result.unique().scalars().all())
        return posts, total

    async def update(self, post: Post, **kwargs) -> Post:
        for key, value in kwargs.items():
            setattr(post, key, value)
        await self.session.flush()
        await self.session.refresh(post)
        # аналогично create — перезапрашиваем с joinedload
        query = select(Post).options(joinedload(Post.user)).where(Post.id == post.id)
        result = await self.session.execute(query)
        return result.unique().scalars().first()

    async def delete(self, post: Post) -> None:
        await self.session.delete(post)
        await self.session.flush()
