import pytest
import json


@pytest.fixture
def sample_comment(logged_in_client, sample_post):
    response = logged_in_client.post("/api/posts/comment", json={
        "post_id": sample_post["id"],
        "content": "This is a comment",
    })
    assert response.status_code == 200
    return response.json()


class TestCommentCreation:
    def test_create_comment(self, logged_in_client, sample_post):
        response = logged_in_client.post("/api/posts/comment", json={
            "post_id": sample_post["id"],
            "content": "Great post!",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is not None
        assert data["content"] == "Great post!"
        assert data["post_id"] == sample_post["id"]
        assert "user" in data or "user_id" in data

    def test_create_multiple_comments(self, logged_in_client, sample_post):
        for i in range(3):
            resp = logged_in_client.post("/api/posts/comment", json={
                "post_id": sample_post["id"],
                "content": f"Comment {i}",
            })
            assert resp.status_code == 200

        response = logged_in_client.get(f"/api/comments/{sample_post['id']}")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_create_comment_unauthenticated(self, sample_post):
        from fastapi.testclient import TestClient
        from src.main import app
        with TestClient(app) as fresh_client:
            response = fresh_client.post("/api/posts/comment", json={
                "post_id": sample_post["id"],
                "content": "Should fail",
            })
            assert response.status_code == 401

    def test_create_comment_on_nonexistent_post(self, logged_in_client):
        response = logged_in_client.post("/api/posts/comment", json={
            "post_id": 9999,
            "content": "Bad post",
        })
        assert response.status_code == 500


class TestCommentRetrieval:
    def test_get_comments_for_post(self, logged_in_client, sample_post):
        post_id = sample_post["id"]
        logged_in_client.post("/api/posts/comment", json={
            "post_id": post_id, "content": "First",
        })
        logged_in_client.post("/api/posts/comment", json={
            "post_id": post_id, "content": "Second",
        })

        response = logged_in_client.get(f"/api/comments/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        contents = {c["content"] for c in data}
        assert "First" in contents
        assert "Second" in contents

    def test_get_comments_empty_post(self, logged_in_client, sample_post):
        response = logged_in_client.get(f"/api/comments/{sample_post['id']}")
        assert response.status_code == 204

    def test_get_comments_includes_user(self, logged_in_client, sample_post):
        logged_in_client.post("/api/posts/comment", json={
            "post_id": sample_post["id"], "content": "With user",
        })
        response = logged_in_client.get(f"/api/comments/{sample_post['id']}")
        assert response.status_code == 200
        comment = response.json()[0]
        assert "user" in comment
        assert comment["user"]["username"] == "testuser"
        assert "password" not in comment["user"]


class TestCommentLikes:
    def test_like_comment(self, logged_in_client, sample_comment):
        response = logged_in_client.post("/api/comments/like", json={
            "comment_id": sample_comment["id"],
        })
        assert response.status_code == 200
        assert "Liked" in response.json()["message"]

    def test_unlike_comment(self, logged_in_client, sample_comment):
        logged_in_client.post("/api/comments/like", json={
            "comment_id": sample_comment["id"],
        })
        response = logged_in_client.request("DELETE", "/api/comments/like", json={
            "comment_id": sample_comment["id"],
        })
        assert response.status_code == 200
        assert "Like Removed" in response.json()["message"]

    def test_duplicate_like_comment(self, logged_in_client, sample_comment):
        logged_in_client.post("/api/comments/like", json={
            "comment_id": sample_comment["id"],
        })
        response = logged_in_client.post("/api/comments/like", json={
            "comment_id": sample_comment["id"],
        })
        assert response.status_code == 500
