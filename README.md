# Trendsee

Тестовое задание: fullstack-приложение на FastAPI + Vue 3 + PostgreSQL + Redis.
Лента публикаций с кэшированием, авторизацией и бесконечным скроллом.

---

## Стек

**Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Redis, Alembic, PyJWT, Pydantic v2  
**Frontend:** Vue 3 (Composition API), Vite, Axios, Vue Router, чистый CSS (токены через custom properties)  
**Инфраструктура:** Docker + docker-compose, Nginx, PostgreSQL 16, Redis 7

---

## Как запустить

```bash
docker-compose up --build
```

- Фронтенд: http://localhost:3000
- API: http://localhost:8000/docs
- При первом запуске БД автоматически мигрируется и заполняется тестовыми данными

## Как запустить тесты

```bash
docker-compose exec backend python -m pytest tests/ -v
```

---

## Структура

```
backend/
  app/
    api/v1/routers/   # роуты (users, posts)
    core/             # конфиг, JWT
    db/               # движок SQLAlchemy, сессии
    models/           # ORM-модели (User, Post)
    repositories/     # слой доступа к данным
    services/         # бизнес-логика + кэш
    schemas/          # Pydantic-схемы
    dependencies/     # DI через FastAPI Depends
  tests/              # pytest + FakeRedis
  seed.py             # сидер тестовых данных

frontend/
  src/
    pages/            # AuthPage, FeedPage, ProfilePage
    components/       # PostCard, PostModal, AppLoader, EmptyState, ErrorState
    composables/      # useInfiniteScroll, useTheme
    services/         # API-клиент (Axios)
    assets/           # глобальные стили + дизайн-токены
```

---

## Что реализовано

- Регистрация и вход по user ID
- CRUD постов (создание, редактирование, удаление — только свои)
- Лента всех публикаций (доступна без авторизации)
- Профиль автора со всеми его постами
- Бесконечный скролл (порог 500px, через requestAnimationFrame)
- Кэширование в Redis (TTL 10 минут, имитация медленного запроса 2с при промахе)
- Инвалидация кэша при создании/редактировании/удалении поста
- Тёмная и светлая тема (переключатель в шапке)
- Полная DI-цепочка: session -> repository -> service (через Depends)
- 10 тестов: юзеры, посты, кэш-хит, инвалидация, права доступа

---

## Использование ИИ

В некоторых местах использовал ИИ как помощника — отмечено в комментариях к коду.
В основном для вещей, где нужно знать неочевидные детали библиотек:
- `model_validator` в Pydantic v2 (вытащить данные из ORM-связи перед сериализацией)
- SCAN/cursor паттерн для инвалидации ключей в Redis (вместо KEYS, который блокирует)
- `joinedload` + `unique().scalars()` в SQLAlchemy 2.0 (eager load без дублей)
- Структура DI-зависимостей в FastAPI
- RAF + passive listener для скролла
- Русская плюрализация
- FakeRedis для тестов
- meta[theme-color] для мобильных браузеров

---

## Quick Start

### Run the whole project:

```bash
docker-compose up --build
```

That's it. Services:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Apply migrations manually (if needed):

```bash
docker-compose exec backend alembic upgrade head
```

### Seed test data:

```bash
docker-compose exec backend python seed.py
```

The seed script creates 3 users and 15 posts automatically on first startup.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `postgres` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `trendsee` | Database user |
| `POSTGRES_PASSWORD` | `trendsee` | Database password |
| `POSTGRES_DB` | `trendsee` | Database name |
| `REDIS_HOST` | `redis` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `JWT_SECRET` | `change-me-in-production` | JWT signing secret |
| `CACHE_TTL` | `600` | Redis cache TTL in seconds |
| `SLOW_DB_DELAY` | `2.0` | Simulated DB delay for cache misses (seconds) |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |
| `VITE_API_URL` | _(empty in prod)_ | Backend URL for frontend dev mode |

---

## API Endpoints

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/users` | No | Create user, returns user + JWT token |
| `GET` | `/api/v1/users/{id}` | No | Get user info by ID |
| `GET` | `/api/v1/users/{id}/token` | No | Get JWT token by user ID |
| `PATCH` | `/api/v1/users/{id}` | No | Update user name |
| `DELETE` | `/api/v1/users/{id}` | No | Delete user (cascades to posts) |
| `GET` | `/api/v1/users/{id}/posts` | No | Get user's posts (paginated) |

### Posts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/posts` | Bearer | Create post (authorized user) |
| `PATCH` | `/api/v1/posts/{id}` | Bearer | Update post (owner only) |
| `DELETE` | `/api/v1/posts/{id}` | Bearer | Delete post (owner only) |

### Request Examples

**Create user:**
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
```

Response:
```json
{
  "user": {
    "id": 1,
    "name": "Alice",
    "created_at": "2025-01-01T00:00:00+00:00",
    "updated_at": "2025-01-01T00:00:00+00:00"
  },
  "token": "eyJ..."
}
```

**Create post (with token):**
```bash
curl -X POST http://localhost:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"title": "My Post", "text": "Hello world"}'
```

**Get posts with pagination:**
```bash
curl "http://localhost:8000/api/v1/users/1/posts?limit=20&offset=0"
```

Response:
```json
{
  "items": [...],
  "total": 15,
  "has_more": false
}
```

---

## Caching Logic

### How it works:

1. When `GET /api/v1/users/{id}/posts` is called, the service first checks **Redis**
2. If cached data exists → return immediately (fast path)
3. If no cache:
   - `await asyncio.sleep(2)` — simulates slow DB query
   - Fetch from PostgreSQL
   - Serialize and store in Redis with **TTL = 600 seconds** (10 minutes)
4. Posts are considered "hot" for 10 minutes after first fetch

### Cache keys:

Pattern: `user:{user_id}:posts:{limit}:{offset}`

Example: `user:1:posts:20:0`

### Cache invalidation:

Cache is **automatically invalidated** when:
- User **creates** a post → all cached pages for that user are cleared
- User **updates** a post → same
- User **deletes** a post → same

Invalidation uses `SCAN` with pattern matching to clear all keys for a user:
```
user:{user_id}:posts:*
```

This is handled centrally in `CacheService.invalidate_user_posts()`.

---

## Infinite Scroll

### Frontend implementation:

1. `useInfiniteScroll` composable listens to scroll events (with `requestAnimationFrame` debouncing)
2. When distance to bottom < **500px**, triggers `loadMore()`
3. Guards:
   - Won't fire if already loading (`isLoading`)
   - Won't fire if no more data (`hasMore = false`)
   - Deduplicates posts by ID (prevents duplicates on fast scrolling)
4. Backend returns `{ items, total, has_more }` — `has_more` controls when to stop

### Backend pagination:

Query params: `limit` (1-100, default 20), `offset` (≥0, default 0)

---

## Running Tests

```bash
# From project root
docker-compose exec backend pytest tests/ -v

# Or locally (requires aiosqlite for SQLite async):
cd backend
pip install aiosqlite
pytest tests/ -v
```

### Test coverage:
- ✅ Create user
- ✅ Get token
- ✅ Get user by ID
- ✅ Get user — 404 for missing user
- ✅ Create post (authorized)
- ✅ Create post (unauthorized — rejected)
- ✅ Get user posts (pagination)
- ✅ Cache hit verification
- ✅ Cache invalidation on post creation
- ✅ Update user
- ✅ Delete user
- ✅ Forbidden edit (post ownership)

---

## Error Handling

| Status | Meaning |
|--------|---------|
| `400` | Invalid request (e.g., no fields to update) |
| `401` | Missing or invalid JWT token |
| `403` | Action forbidden (e.g., editing someone else's post) |
| `404` | Resource not found |
| `422` | Validation error (FastAPI/Pydantic) |

All error responses follow the format:
```json
{
  "detail": "Human-readable error message"
}
```

---

## Design Decisions

- **No Pinia** — app state is simple enough to manage with composables and `ref()`. Adding a store would be overengineering.
- **No component library** — clean CSS with design tokens keeps the bundle small and the design consistent.
- **Centralized cache service** — all Redis operations go through `CacheService`, making invalidation predictable.
- **DI via Depends** — clean wiring of DB sessions → repositories → services, easily testable.
- **Seed on startup** — `seed.py` runs once during container start for immediate demo experience.
