import pytest
import json


class TestPostCRUD:
    def test_create_post(self, logged_in_client):
        response = logged_in_client.post("/api/posts/create", json={
            "title": "My First Post",
            "content": "Hello forum!",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is not None
        assert data["title"] == "My First Post"
        assert data["content"] == "Hello forum!"
        assert data["is_closed"] is False
        assert data["answer_id"] is None
        assert "user" in data
        assert data["user"]["username"] == "testuser"
        assert "password" not in data["user"]

    def test_get_post_by_id(self, logged_in_client, sample_post):
        post_id = sample_post["id"]
        response = logged_in_client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["content"] == "Post content here"
        assert data["user"]["username"] == "testuser"

    def test_get_all_posts(self, logged_in_client):
        logged_in_client.post("/api/posts/create", json={
            "title": "Post A", "content": "Content A",
        })
        logged_in_client.post("/api/posts/create", json={
            "title": "Post B", "content": "Content B",
        })
        response = logged_in_client.get("/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        titles = {p["title"] for p in data}
        assert "Post A" in titles
        assert "Post B" in titles


class TestPostLikes:
    def test_like_post(self, logged_in_client, sample_post):
        response = logged_in_client.post("/api/posts/like", json={
            "post_id": sample_post["id"],
        })
        assert response.status_code == 200
        assert "Liked" in response.json()["message"]

    def test_unlike_post(self, logged_in_client, sample_post):
        logged_in_client.post("/api/posts/like", json={
            "post_id": sample_post["id"],
        })
        response = logged_in_client.request("DELETE", "/api/posts/like", json={
            "post_id": sample_post["id"],
        })
        assert response.status_code == 200
        assert "Like Removed" in response.json()["message"]

    def test_duplicate_like(self, logged_in_client, sample_post):
        logged_in_client.post("/api/posts/like", json={
            "post_id": sample_post["id"],
        })
        response = logged_in_client.post("/api/posts/like", json={
            "post_id": sample_post["id"],
        })
        assert response.status_code == 500


class TestPostAnswer:
    def _register_and_login(self, client, username, email):
        client.post("/api/register", json={
            "username": username,
            "nickname": username,
            "email": email,
            "password": "pass123",
        })
        client.post("/api/login", json={
            "user": username,
            "password": "pass123",
        })

    def test_mark_best_answer(self, logged_in_client, sample_post):
        post_id = sample_post["id"]
        comment_resp = logged_in_client.post("/api/posts/comment", json={
            "post_id": post_id,
            "content": "The answer",
        })
        assert comment_resp.status_code == 200
        comment_id = comment_resp.json()["id"]

        response = logged_in_client.put("/api/comments/best", json={
            "post_id": post_id,
            "comment_id": comment_id,
        })
        assert response.status_code == 200
        assert "answer set" in response.json()["message"]

    def test_non_owner_cannot_mark_answer(self, logged_in_client, sample_post):
        post_id = sample_post["id"]

        comment_resp = logged_in_client.post("/api/posts/comment", json={
            "post_id": post_id,
            "content": "A comment",
        })
        comment_id = comment_resp.json()["id"]

        from fastapi.testclient import TestClient
        from src.main import app
        with TestClient(app) as other_client:
            self._register_and_login(other_client, "other", "other@example.com")
            response = other_client.put("/api/comments/best", json={
                "post_id": post_id,
                "comment_id": comment_id,
            })
            assert response.status_code == 500


class TestPostClose:
    def test_close_post(self, logged_in_client, sample_post):
        response = logged_in_client.put("/api/posts/closed", json={
            "post_id": sample_post["id"],
        })
        assert response.status_code == 200
        assert "True" in response.json()["message"]

    def test_non_owner_cannot_close(self, logged_in_client, sample_post):
        from fastapi.testclient import TestClient
        from src.main import app
        with TestClient(app) as other_client:
            other_client.post("/api/register", json={
                "username": "other",
                "nickname": "Other",
                "email": "other@example.com",
                "password": "pass123",
            })
            other_client.post("/api/login", json={
                "user": "other",
                "password": "pass123",
            })
            response = other_client.put("/api/posts/closed", json={
                "post_id": sample_post["id"],
            })
            assert response.status_code == 500
