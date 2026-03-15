# Конфигурация приложения. Все параметры берутся из окружения или .env файла

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "Trendsee API"
    API_V1_PREFIX: str = "/api/v1"

    # постгрес
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "trendsee"
    POSTGRES_PASSWORD: str = "trendsee"
    POSTGRES_DB: str = "trendsee"

    # редис
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    JWT_SECRET: str = "super-secret-change-me"
    JWT_ALGORITHM: str = "HS256"

    CACHE_TTL: int = 600       # время жизни кэша — 10 минут (по ТЗ)
    SLOW_DB_DELAY: float = 2.0 # имитация медленного запроса в БД (по ТЗ)

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # URLы собираются из отдельных параметров, чтобы в docker-compose
    # можно было каждый менять отдельно
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# lru_cache чтобы не парсить .env на каждый запрос
@lru_cache
def get_settings() -> Settings:
    return Settings()
