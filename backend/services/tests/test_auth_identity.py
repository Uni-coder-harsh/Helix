from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from helix_platform.persistence import SessionLocal
from services.identity.crypto import hash_password, verify_password
from services.identity.jwt import create_access_token, decode_token
from services.identity.models import UserDB


def test_password_hashing() -> None:
    password = "supersecurepassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_jwt_utilities() -> None:
    user_id = "test-user-id"
    email = "test@example.com"
    token = create_access_token(user_id, email)

    decoded = decode_token(token)
    assert decoded["sub"] == user_id
    assert decoded["email"] == email
    assert decoded["type"] == "access"


def test_register_flow(client: TestClient) -> None:
    email = "register_test@example.com"
    # Successful registration
    response = client.post(
        "/identity/register", json={"email": email, "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["is_verified"] is False
    assert "id" in data

    # Conflict / Email already registered
    response = client.post(
        "/identity/register", json={"email": email, "password": "password123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

    # Invalid email validation
    response = client.post(
        "/identity/register", json={"email": "invalid-email", "password": "password123"}
    )
    assert response.status_code == 422

    # Short password validation
    response = client.post(
        "/identity/register",
        json={"email": "short_pwd@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_login_and_logout_flow(client: TestClient) -> None:
    email = "login_test@example.com"
    password = "password123"

    # 1. Register user
    client.post("/identity/register", json={"email": email, "password": password})

    # 2. Login - Incorrect credentials
    response = client.post(
        "/identity/login", json={"email": email, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

    # 3. Login - Correct credentials
    response = client.post(
        "/identity/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Check cookies
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    # 4. Logout
    logout_response = client.post("/identity/logout")
    assert logout_response.status_code == 200
    # Cookies should be deleted / empty
    assert not logout_response.cookies.get("access_token")


def test_me_protected_route(client: TestClient) -> None:
    email = "me_test@example.com"
    password = "password123"

    # 1. Register and login
    client.post("/identity/register", json={"email": email, "password": password})
    login_resp = client.post(
        "/identity/login", json={"email": email, "password": password}
    )
    access_token = login_resp.json()["access_token"]

    # Clear client cookies to test unauthorized access
    client.cookies.clear()

    # 2. Access me without credentials
    resp = client.get("/identity/me")
    assert resp.status_code == 401

    # 3. Access me with authorization header
    resp = client.get(
        "/identity/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == email

    # 4. Access me with cookie
    client.cookies.set("access_token", access_token)
    resp = client.get("/identity/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == email
    # Clear client cookies
    client.cookies.clear()


def test_token_refresh_flow(client: TestClient) -> None:
    email = "refresh_test@example.com"
    password = "password123"

    # 1. Register and login
    client.post("/identity/register", json={"email": email, "password": password})
    login_resp = client.post(
        "/identity/login", json={"email": email, "password": password}
    )
    refresh_token = login_resp.json()["refresh_token"]

    # 2. Refresh via JSON payload
    resp = client.post("/identity/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    new_refresh_token = data["refresh_token"]

    # 3. Refresh via cookie
    client.cookies.set("refresh_token", new_refresh_token)
    resp = client.post("/identity/refresh")
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    client.cookies.clear()


def test_email_verification_skeleton(client: TestClient) -> None:
    email = "verify_test@example.com"
    password = "password123"

    # Register
    reg_resp = client.post(
        "/identity/register", json={"email": email, "password": password}
    )
    user_id = reg_resp.json()["id"]

    # Fetch user to get verification token from DB (since register response doesn't expose token)
    db: Session = SessionLocal()
    try:
        user: Any = db.query(UserDB).filter(UserDB.id == user_id).first()
        assert user is not None
        token = user.verification_token
        assert token is not None
    finally:
        db.close()

    # Verify email
    resp = client.post("/identity/verify-email", json={"token": token})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Email verified successfully"

    # Verify user is indeed verified in DB
    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        assert user is not None
        assert user.is_verified
        assert user.verification_token is None
    finally:
        db.close()

    # Resend verification
    resend_resp = client.post("/identity/resend-verification", json={"email": email})
    assert resend_resp.status_code == 200
    assert "already verified" in resend_resp.json()["message"]


def test_password_reset_skeleton(client: TestClient) -> None:
    email = "reset_pwd_test@example.com"
    password = "password123"

    # Register
    client.post("/identity/register", json={"email": email, "password": password})

    # Forgot password
    forgot_resp = client.post("/identity/forgot-password", json={"email": email})
    assert forgot_resp.status_code == 200
    reset_token = forgot_resp.json()["reset_token"]
    assert reset_token is not None

    # Reset password
    new_password = "newsupersecurepassword"
    reset_resp = client.post(
        "/identity/reset-password",
        json={"token": reset_token, "new_password": new_password},
    )
    assert reset_resp.status_code == 200
    assert reset_resp.json()["message"] == "Password has been reset successfully"

    # Login with new password
    login_resp = client.post(
        "/identity/login", json={"email": email, "password": new_password}
    )
    assert login_resp.status_code == 200


def test_change_password_and_logout_all(client: TestClient) -> None:
    email = "change_pwd_test@example.com"
    password = "password123"

    # Register
    client.post("/identity/register", json={"email": email, "password": password})

    # Login
    login_resp = client.post(
        "/identity/login", json={"email": email, "password": password}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Change password (wrong old password)
    change_resp = client.post(
        "/identity/change-password",
        json={"old_password": "wrongpassword", "new_password": "newpassword123"},
        headers=headers,
    )
    assert change_resp.status_code == 400

    # Change password successfully
    change_resp = client.post(
        "/identity/change-password",
        json={"old_password": password, "new_password": "newpassword123"},
        headers=headers,
    )
    assert change_resp.status_code == 200
    assert change_resp.json()["message"] == "Password changed successfully"

    # Login again with new password
    login_resp2 = client.post(
        "/identity/login", json={"email": email, "password": "newpassword123"}
    )
    assert login_resp2.status_code == 200
    token2 = login_resp2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Logout all sessions
    logout_resp = client.post("/identity/sessions/logout-all", headers=headers2)
    assert logout_resp.status_code == 204
