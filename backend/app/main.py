# Точка входа приложения — здесь собираем FastAPI, миддлвары и роутеры

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import posts, users
from app.core.config import get_settings
from app.dependencies.deps import close_redis, get_redis

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # при старте прогреваем пул редиса, чтобы первый запрос не тормозил
    await get_redis()
    yield
    # при остановке закрываем соединение
    await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

# CORS — разрешаем фронту ходить на API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# все роуты живут под /api/v1
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(posts.router, prefix=settings.API_V1_PREFIX)


# healthcheck для docker-compose — проверяет что бэкенд вообще живой
@app.get("/health")
async def health():
    return {"status": "ok"}
