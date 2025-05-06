import pytest
from datetime import timedelta
from app.models.user_model import User, UserRole
from app.utils.security import hash_password, verify_password
from app.services.jwt_service import create_access_token


# User Registration: Duplicate Email Check
@pytest.mark.asyncio
async def test_user_registration_duplicate_email(db_session, user):
    duplicate_user = User(
        nickname="duplicate",
        first_name="Dupe",
        last_name="User",
        email=user.email,
        hashed_password=hash_password("NewPassword123"),
        role=UserRole.AUTHENTICATED
    )
    db_session.add(duplicate_user)
    with pytest.raises(Exception):
        await db_session.commit()

# User Login: Unverified Email
@pytest.mark.asyncio
async def test_login_unverified_user(async_client, unverified_user):
    response = await async_client.post("/auth/login", json={
        "email": unverified_user.email,
        "password": "MySuperPassword$1234"
    })
    assert response.status_code == 403

# Admin creates a new user
@pytest.mark.asyncio
async def test_admin_creates_user(async_client, admin_token):
    response = await async_client.post(
        "/users/",
        json={
            "nickname": "newbie",
            "email": "newbie@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass$123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newbie@example.com"

# Authenticated User Attempts Role Escalation
@pytest.mark.asyncio
async def test_user_attempts_admin_promotion(async_client, user_token, user):
    response = await async_client.patch(
        f"/users/{user.id}",
        json={"role": "ADMIN"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code in (403, 401)

# Login with Invalid Email Format
@pytest.mark.asyncio
async def test_login_invalid_email_format(async_client):
    response = await async_client.post("/auth/login", json={
        "email": "not-an-email",
        "password": "password"
    })
    assert response.status_code == 422

# Edge case: Long nickname
@pytest.mark.asyncio
async def test_create_user_with_long_nickname(async_client, admin_token):
    long_nickname = "x" * 256
    response = await async_client.post(
        "/users/",
        json={
            "nickname": long_nickname,
            "email": "longnick@example.com",
            "first_name": "Long",
            "last_name": "Nickname",
            "password": "SecurePass$123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code in (400, 422)

# Locked User Login Attempt
@pytest.mark.asyncio
async def test_login_locked_user(async_client, locked_user):
    response = await async_client.post("/auth/login", json={
        "email": locked_user.email,
        "password": "MySuperPassword$1234"
    })
    assert response.status_code == 403

# Token Expiry Simulation
@pytest.mark.asyncio
async def test_expired_token_access(async_client, admin_user):
    expired_token = create_access_token(
        data={"sub": str(admin_user.id), "role": admin_user.role.name},
        expires_delta=timedelta(minutes=-1)
    )
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code in (401, 403)
