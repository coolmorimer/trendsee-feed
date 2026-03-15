# Тесты API: юзеры, посты, кэш, права доступа

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    resp = await client.post("/api/v1/users", json={"name": "TestUser"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["name"] == "TestUser"
    assert "token" in data
    assert data["user"]["id"] > 0


@pytest.mark.asyncio
async def test_get_token(client: AsyncClient):
    # Create user first
    create_resp = await client.post("/api/v1/users", json={"name": "TokenUser"})
    user_id = create_resp.json()["user"]["id"]

    resp = await client.get(f"/api/v1/users/{user_id}/token")
    assert resp.status_code == 200
    assert "token" in resp.json()


@pytest.mark.asyncio
async def test_create_post_authorized(client: AsyncClient):
    # Create user and get token
    create_resp = await client.post("/api/v1/users", json={"name": "Author"})
    token = create_resp.json()["token"]

    resp = await client.post(
        "/api/v1/posts",
        json={"title": "My Post", "text": "Hello world"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Post"
    assert data["text"] == "Hello world"


@pytest.mark.asyncio
async def test_create_post_unauthorized(client: AsyncClient):
    resp = await client.post(
        "/api/v1/posts",
        json={"title": "My Post", "text": "Hello world"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_user_posts(client: AsyncClient):
    # Create user
    create_resp = await client.post("/api/v1/users", json={"name": "PostsUser"})
    user_id = create_resp.json()["user"]["id"]
    token = create_resp.json()["token"]

    # Create a few posts
    for i in range(3):
        await client.post(
            "/api/v1/posts",
            json={"title": f"Post {i}", "text": f"Content {i}"},
            headers={"Authorization": f"Bearer {token}"},
        )

    # Fetch posts (will be slow due to sleep, but we override that via SLOW_DB_DELAY)
    resp = await client.get(f"/api/v1/users/{user_id}/posts?limit=10&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_cache_hit(client: AsyncClient):
    from tests.conftest import fake_redis

    # Create user + posts
    create_resp = await client.post("/api/v1/users", json={"name": "CacheUser"})
    user_id = create_resp.json()["user"]["id"]
    token = create_resp.json()["token"]

    await client.post(
        "/api/v1/posts",
        json={"title": "Cached Post", "text": "Will be cached"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # First request — cache miss, goes to DB
    resp1 = await client.get(f"/api/v1/users/{user_id}/posts?limit=20&offset=0")
    assert resp1.status_code == 200

    # Verify cache was populated
    cache_key = f"user:{user_id}:posts:20:0"
    assert cache_key in fake_redis._store

    # Second request — should hit cache
    resp2 = await client.get(f"/api/v1/users/{user_id}/posts?limit=20&offset=0")
    assert resp2.status_code == 200
    assert resp2.json() == resp1.json()


@pytest.mark.asyncio
async def test_cache_invalidation_on_create(client: AsyncClient):
    from tests.conftest import fake_redis

    create_resp = await client.post("/api/v1/users", json={"name": "InvalidateUser"})
    user_id = create_resp.json()["user"]["id"]
    token = create_resp.json()["token"]

    # Populate cache
    await client.get(f"/api/v1/users/{user_id}/posts?limit=20&offset=0")
    cache_key = f"user:{user_id}:posts:20:0"
    assert cache_key in fake_redis._store

    # Create a new post — should invalidate cache
    await client.post(
        "/api/v1/posts",
        json={"title": "New", "text": "Invalidates cache"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cache_key not in fake_redis._store


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient):
    create_resp = await client.post("/api/v1/users", json={"name": "OldName"})
    user_id = create_resp.json()["user"]["id"]

    resp = await client.patch(
        f"/api/v1/users/{user_id}", json={"name": "NewName"}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "NewName"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    create_resp = await client.post("/api/v1/users", json={"name": "DeleteMe"})
    user_id = create_resp.json()["user"]["id"]

    resp = await client.delete(f"/api/v1/users/{user_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_forbidden_edit_post(client: AsyncClient):
    # Create two users
    resp1 = await client.post("/api/v1/users", json={"name": "Owner"})
    token_owner = resp1.json()["token"]

    resp2 = await client.post("/api/v1/users", json={"name": "Other"})
    token_other = resp2.json()["token"]

    # Owner creates post
    post_resp = await client.post(
        "/api/v1/posts",
        json={"title": "Owner Post", "text": "Mine"},
        headers={"Authorization": f"Bearer {token_owner}"},
    )
    post_id = post_resp.json()["id"]

    # Other tries to edit
    resp = await client.patch(
        f"/api/v1/posts/{post_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {token_other}"},
    )
    assert resp.status_code == 403
