import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.models.user import UserRole
from app.core.security import create_access_token
from datetime import timedelta


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(async_client: AsyncClient):
    """1. Unauthenticated requests must be rejected with 401 Unauthorized."""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_authentication_workflow(async_client: AsyncClient):
    """5. Registration & Login workflow testing with JWT issuance."""
    # Register Student
    reg_payload = {
        "email": "test.student@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test Student Learner",
        "role": "STUDENT",
    }
    reg_resp = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert "refresh_token" in reg_data
    assert reg_data["user"]["email"] == "test.student@example.com"
    assert reg_data["user"]["role"] == "STUDENT"

    # Login Student
    login_payload = {
        "email": "test.student@example.com",
        "password": "SecurePassword123!",
    }
    login_resp = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    token = login_data["access_token"]

    # Verify Current User Profile
    me_resp = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "test.student@example.com"


@pytest.mark.asyncio
async def test_invalid_credentials_rejected(async_client: AsyncClient):
    """6. Invalid login credentials must be rejected with 401 Unauthorized."""
    payload = {
        "email": "nonexistent.user@example.com",
        "password": "WrongPassword999!",
    }
    resp = await async_client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid email or password."


@pytest.mark.asyncio
async def test_student_cannot_access_admin_resources(async_client: AsyncClient):
    """2. Student role cannot access administrative endpoints (403 Forbidden)."""
    # Register/Login as student
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "student.rbac@example.com",
            "password": "Password123!",
            "full_name": "RBAC Student",
            "role": "STUDENT",
        },
    )
    token = reg.json()["access_token"]

    # Attempt to access student endpoint -> Should succeed (200)
    student_resp = await async_client.get(
        "/api/v1/users/student-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert student_resp.status_code == 200

    # Attempt to access admin endpoint -> Must fail (403)
    admin_resp = await async_client.get(
        "/api/v1/users/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert admin_resp.status_code == 403


@pytest.mark.asyncio
async def test_instructor_cannot_access_admin_resources(async_client: AsyncClient):
    """3. Instructor role cannot access administrative endpoints (403 Forbidden)."""
    # Register/Login as instructor
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "instructor.rbac@example.com",
            "password": "Password123!",
            "full_name": "RBAC Instructor",
            "role": "INSTRUCTOR",
        },
    )
    token = reg.json()["access_token"]

    # Attempt to access instructor endpoint -> Should succeed (200)
    inst_resp = await async_client.get(
        "/api/v1/users/instructor-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert inst_resp.status_code == 200

    # Attempt to access admin endpoint -> Must fail (403)
    admin_resp = await async_client.get(
        "/api/v1/users/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert admin_resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_admin_and_subordinate_resources(async_client: AsyncClient):
    """4. Platform Admin role can access administrative and all subordinate endpoints (200 OK)."""
    # Register/Login as platform admin
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin.rbac@example.com",
            "password": "Password123!",
            "full_name": "RBAC Admin",
            "role": "PLATFORM_ADMIN",
        },
    )
    token = reg.json()["access_token"]

    # Admin access admin-only -> 200
    admin_resp = await async_client.get(
        "/api/v1/users/admin-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert admin_resp.status_code == 200

    # Admin access instructor-only -> 200
    inst_resp = await async_client.get(
        "/api/v1/users/instructor-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert inst_resp.status_code == 200

    # Admin access student-only -> 200
    student_resp = await async_client.get(
        "/api/v1/users/student-only",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert student_resp.status_code == 200


@pytest.mark.asyncio
async def test_resource_ownership_checks(async_client: AsyncClient):
    """7. Resource ownership verification (owner or admin 200, other user 403)."""
    # User 1 (Student A)
    u1 = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner.user1@example.com",
            "password": "Password123!",
            "full_name": "Owner User 1",
            "role": "STUDENT",
        },
    )
    u1_data = u1.json()
    u1_id = u1_data["user"]["id"]
    u1_token = u1_data["access_token"]

    # User 2 (Student B)
    u2 = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "other.user2@example.com",
            "password": "Password123!",
            "full_name": "Other User 2",
            "role": "STUDENT",
        },
    )
    u2_token = u2.json()["access_token"]

    # User 1 accesses their own profile -> 200 OK
    own_resp = await async_client.get(
        f"/api/v1/users/{u1_id}/profile",
        headers={"Authorization": f"Bearer {u1_token}"},
    )
    assert own_resp.status_code == 200
    assert own_resp.json()["id"] == u1_id

    # User 2 attempts to access User 1's profile -> 403 Forbidden
    unauthorized_resp = await async_client.get(
        f"/api/v1/users/{u1_id}/profile",
        headers={"Authorization": f"Bearer {u2_token}"},
    )
    assert unauthorized_resp.status_code == 403

    # Admin accesses User 1's profile -> 200 OK
    admin_reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin.owner@example.com",
            "password": "Password123!",
            "full_name": "Super Admin",
            "role": "PLATFORM_ADMIN",
        },
    )
    admin_token = admin_reg.json()["access_token"]
    admin_lookup = await async_client.get(
        f"/api/v1/users/{u1_id}/profile",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_lookup.status_code == 200
    assert admin_lookup.json()["id"] == u1_id


@pytest.mark.asyncio
async def test_invalid_and_expired_jwt_rejected(async_client: AsyncClient):
    """8. Invalid or expired JWT tokens are rejected with 401."""
    # Invalid token string
    resp1 = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-real-jwt-token"},
    )
    assert resp1.status_code == 401

    # Expired token
    expired_token = create_access_token(
        subject=999,
        role="STUDENT",
        expires_delta=timedelta(seconds=-10),
    )
    resp2 = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp2.status_code == 401
    assert "expired" in resp2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_token_revocation(async_client: AsyncClient):
    """9. Logout revokes token and prevents subsequent access."""
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "logout.test@example.com",
            "password": "Password123!",
            "full_name": "Logout Tester",
            "role": "STUDENT",
        },
    )
    token = reg.json()["access_token"]

    # Verify token works
    valid_resp = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert valid_resp.status_code == 200

    # Logout
    logout_resp = await async_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_resp.status_code == 200

    # Verify token is now rejected
    post_logout_resp = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert post_logout_resp.status_code == 401
    assert "revoked" in post_logout_resp.json()["detail"].lower()
