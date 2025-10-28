"""
Auth Tests
Owner: Ryan
Description: Validate user registration, login, and JWT handling.
"""


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def register_user(client, email="test@demo.com", password="Pass123!", role="client"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "role": role},
    )


def login_user(client, email="test@demo.com", password="Pass123!"):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
def test_register_user_success(client):
    """Should register a new user successfully."""
    res = register_user(client)
    assert res.status_code == 201
    data = res.get_json()
    assert "user" in data
    assert data["user"]["email"] == "test@demo.com"


def test_login_with_invalid_password(client):
    """Should fail login if password is wrong."""
    register_user(client)
    res = login_user(client, password="wrongpass")
    assert res.status_code == 401
    assert "Invalid credentials" in res.get_json()["error"]


def test_login_and_access_me(client):
    """Should login and access protected /me route."""
    register_user(client)
    login = login_user(client)
    token = login.get_json()["access_token"]

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["email"] == "test@demo.com"


def test_refresh_token(client):
    """Should issue a new access token using refresh token."""
    register_user(client)
    login = login_user(client)
    refresh = login.get_json()["refresh_token"]

    res = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert res.status_code == 200
    assert "access_token" in res.get_json()


def test_logout_revokes_token(client):
    """Should revoke token and block further use."""
    register_user(client)
    login = login_user(client)
    token = login.get_json()["access_token"]

    # logout (revoke)
    res = client.delete("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

    # access protected route again should fail
    res2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 401
