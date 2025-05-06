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


