# Скрипт заполнения БД тестовыми данными.
# Запускается автоматически при старте контейнера, но не дублирует если данные уже есть.

import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.post import Post
from app.models.user import User

settings = get_settings()

engine = create_async_engine(settings.database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

USERS = [
    {"name": "Alice Johnson"},
    {"name": "Bob Smith"},
    {"name": "Charlie Brown"},
]

POSTS = [
    {"title": "Getting Started with FastAPI", "text": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints. It provides automatic interactive API documentation, data validation, serialization, and asynchronous support out of the box."},
    {"title": "Why I Love Vue 3", "text": "Vue 3 brings the Composition API, better TypeScript support, improved reactivity system, and Teleport. The new setup function makes it easier to organize code by feature rather than by option type."},
    {"title": "Docker Best Practices", "text": "Use multi-stage builds, minimize layers, use .dockerignore, run as non-root user, and pin your base image versions. These practices lead to smaller, more secure container images."},
    {"title": "Understanding Redis Caching", "text": "Redis is an in-memory data store that can be used as a cache, message broker, or database. Setting appropriate TTLs, using the right data structures, and implementing cache invalidation are key to effective caching."},
    {"title": "Async Python Deep Dive", "text": "Python asyncio provides infrastructure for writing single-threaded concurrent code using coroutines. With async/await syntax, you can write asynchronous code that looks and behaves like synchronous code."},
    {"title": "PostgreSQL Performance Tips", "text": "Use indexes wisely, analyze your queries with EXPLAIN, batch your inserts, use connection pooling, and keep your statistics up to date. Partitioning large tables can also significantly improve query performance."},
    {"title": "Building RESTful APIs", "text": "Good REST APIs use proper HTTP methods, status codes, and resource naming. Implement pagination, filtering, and sorting. Use versioning from day one and document everything with OpenAPI."},
    {"title": "SQLAlchemy 2.0 Migration Guide", "text": "SQLAlchemy 2.0 introduces a new unified tutorial, declarative mapping with mapped_column, and improved async support. The 2.0 style uses select() instead of Query objects for all queries."},
    {"title": "Frontend State Management", "text": "Managing state in modern frontend applications requires choosing the right tool. Pinia for Vue, Redux for React, or sometimes just composables and reactive refs are enough for smaller apps."},
    {"title": "CI/CD Pipeline Setup", "text": "A good CI/CD pipeline includes linting, testing, building, and deploying stages. Use GitHub Actions or GitLab CI with Docker for reproducible builds and automated deployments."},
    {"title": "JWT Authentication Explained", "text": "JSON Web Tokens encode claims in a compact, URL-safe format. Use short-lived access tokens with refresh tokens for better security. Always validate token signatures server-side."},
    {"title": "Infinite Scroll Implementation", "text": "Infinite scroll loads content dynamically as users scroll down. Use intersection observers or scroll event listeners with debouncing. Track offset, loading state, and has_more flag to prevent unnecessary requests."},
    {"title": "Clean Architecture in Python", "text": "Separate concerns into layers: presentation, business logic, and data access. Use dependency injection, keep framework-specific code at the edges, and design your domain model first."},
    {"title": "WebSocket Real-Time Features", "text": "WebSockets enable bidirectional communication between client and server. They are perfect for chat applications, live notifications, and real-time dashboards. FastAPI supports WebSockets natively."},
    {"title": "Testing Async Code", "text": "Testing async Python code requires pytest-asyncio and proper fixtures. Mock external dependencies, use in-memory databases for speed, and test both happy paths and error scenarios."},
]


async def seed():
    async with session_factory() as session:
        # Check if data already exists
        result = await session.execute(select(User).limit(1))
        if result.scalar():
            print("Database already seeded. Skipping.")
            return

        async with session.begin():
            users = []
            for u in USERS:
                user = User(**u)
                session.add(user)
                users.append(user)
            await session.flush()

            for i, post_data in enumerate(POSTS):
                user = users[i % len(users)]
                post = Post(user_id=user.id, **post_data)
                session.add(post)

    print(f"Seeded {len(USERS)} users and {len(POSTS)} posts.")


if __name__ == "__main__":
    asyncio.run(seed())
