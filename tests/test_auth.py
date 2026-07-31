import pytest


class TestRegister:
    def test_register_success(self, client):
        response = client.post("/api/register", json={
            "username": "newuser",
            "nickname": "New User",
            "email": "new@example.com",
            "password": "pass123",
        })
        assert response.status_code == 200
        assert "Created" in response.json()["message"]

    def test_register_duplicate_username(self, client, registered_user):
        response = client.post("/api/register", json={
            "username": "testuser",
            "nickname": "Another",
            "email": "other@example.com",
            "password": "pass123",
        })
        assert response.status_code == 500

    def test_register_duplicate_email(self, client, registered_user):
        response = client.post("/api/register", json={
            "username": "otheruser",
            "nickname": "Other",
            "email": "test@example.com",
            "password": "pass123",
        })
        assert response.status_code == 500

    def test_register_empty_fields(self, client):
        response = client.post("/api/register", json={
            "username": "",
            "nickname": "Test",
            "email": "test@example.com",
            "password": "pass123",
        })
        assert response.status_code == 500

    def test_register_at_in_username(self, client):
        response = client.post("/api/register", json={
            "username": "user@name",
            "nickname": "Test",
            "email": "test@example.com",
            "password": "pass123",
        })
        assert response.status_code == 500


class TestLogin:
    def test_login_username_success(self, client, registered_user):
        response = client.post("/api/login", json={
            "user": "testuser",
            "password": "securepass123",
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Cookies!"
        assert "uid" in response.cookies

    def test_login_email_success(self, client, registered_user):
        response = client.post("/api/login", json={
            "user": "test@example.com",
            "password": "securepass123",
        })
        assert response.status_code == 200
        assert "uid" in response.cookies

    def test_login_wrong_password(self, client, registered_user):
        response = client.post("/api/login", json={
            "user": "testuser",
            "password": "wrongpass",
        })
        assert response.status_code == 500

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/login", json={
            "user": "nobody",
            "password": "pass",
        })
        assert response.status_code == 500


class TestTokenValidation:
    def test_logged_with_valid_token(self, logged_in_client):
        response = logged_in_client.get("/api/logged")
        assert response.status_code == 200
        assert "Logged In" in response.json()["res"]

    def test_logged_without_token(self, client):
        response = client.get("/api/logged")
        assert response.status_code == 401
        assert "Token is missing" in response.json()["detail"]

    def test_logged_with_invalid_token(self, client):
        client.cookies.set("uid", "invalid.jwt.token")
        response = client.get("/api/logged")
        assert response.status_code == 401
        assert "Error" in response.json()["detail"]


class TestProfile:
    def test_profile_with_valid_token(self, logged_in_client):
        response = logged_in_client.get("/api/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password" not in data

    def test_profile_without_token(self, client):
        response = client.get("/api/profile")
        assert response.status_code == 401

    def test_profile_user_not_found(self, client):
        import jwt as pyjwt
        import os

        token = pyjwt.encode(
            {"user_id": 99999, "exp": 9999999999},
            os.environ["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        client.cookies.set("uid", token)
        response = client.get("/api/profile")
        assert response.status_code == 500


class TestLogout:
    def test_logout_clears_cookie(self, logged_in_client):
        response = logged_in_client.post("/api/logout")
        assert response.status_code == 200
        assert "logged out" in response.json()["message"]

    def test_logout_without_token(self, client):
        response = client.post("/api/logout")
        assert response.status_code == 401
