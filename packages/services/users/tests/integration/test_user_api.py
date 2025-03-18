"""Integration tests for the User API endpoints."""

import pytest
from booking_shared_models.models import User
from fastapi import status

pytestmark = pytest.mark.skip(reason="Skipping entire file. Implement authentication.")

# Constants to avoid repetition
BASE_URL = "/api/v1/users"
REGISTER_URL = f"{BASE_URL}/register"
BY_EMAIL_URL = f"{BASE_URL}/by-email"
BY_USERNAME_URL = f"{BASE_URL}/by-username"

MSG_USER_REGISTERED = "User registered successfully"
MSG_USER_RETRIEVED = "User retrieved successfully"
MSG_USERS_RETRIEVED = "Users retrieved successfully"
MSG_USER_UPDATED = "User updated successfully"
MSG_USER_DELETED = "User deleted successfully"

ERR_ALREADY_EXISTS = "already exists"
ERR_NOT_FOUND = "not found"


class TestUserRegistrationAPI:
    """Integration tests for user registration API."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client, test_user_create):
        """Test successful user registration via API."""
        user_data = {
            "email": test_user_create.email,
            "username": test_user_create.username,
            "password": test_user_create.password,
        }
        response = await async_client.post(REGISTER_URL, json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USER_REGISTERED
        assert data["data"]["email"] == user_data["email"]
        assert data["data"]["username"] == user_data["username"]
        assert "password" not in data["data"]
        assert "hashed_password" not in data["data"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, async_client, test_user, test_user_create
    ):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,  # Already exists
            "username": test_user_create.username,
            "password": test_user_create.password,
        }
        response = await async_client.post(REGISTER_URL, json=user_data)
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert ERR_ALREADY_EXISTS in data["message"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self, async_client, test_user, test_user_create
    ):
        """Test registration with duplicate username."""
        user_data = {
            "email": test_user_create.email,
            "username": test_user.username,  # Already exists
            "password": test_user_create.password,
        }
        response = await async_client.post(REGISTER_URL, json=user_data)
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert ERR_ALREADY_EXISTS in data["message"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",  # Invalid format
            "username": "testuser123",
            "password": "password123",
        }
        response = await async_client.post(REGISTER_URL, json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        if "details" in data and "errors" in data["details"]:
            assert any(
                "email" in str(error["loc"]) for error in data["details"]["errors"]
            )
        elif "detail" in data:
            assert any("email" in str(error["loc"]) for error in data["detail"])
        else:
            assert False, "Validation error response doesn't have expected structure"


class TestGetUserAPI:
    """Integration tests for user retrieval API."""

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, async_client, test_user):
        """Test getting a user by ID."""
        response = await async_client.get(f"{BASE_URL}/{test_user.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USER_RETRIEVED
        assert data["data"]["id"] == test_user.id
        assert data["data"]["email"] == test_user.email
        assert data["data"]["username"] == test_user.username
        assert "password" not in data["data"]
        assert "hashed_password" not in data["data"]

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, async_client):
        """Test getting a non-existent user."""
        non_existent_id = 9999
        response = await async_client.get(f"{BASE_URL}/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert ERR_NOT_FOUND in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, async_client, test_user):
        """Test getting a user by email."""
        response = await async_client.get(f"{BY_EMAIL_URL}/{test_user.email}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USER_RETRIEVED
        assert data["data"]["id"] == test_user.id
        assert data["data"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, async_client):
        """Test getting a user by email that doesn't exist."""
        response = await async_client.get(f"{BY_EMAIL_URL}/nonexistent@example.com")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert ERR_NOT_FOUND in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, async_client, test_user):
        """Test getting a user by username."""
        response = await async_client.get(f"{BY_USERNAME_URL}/{test_user.username}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USER_RETRIEVED
        assert data["data"]["id"] == test_user.id
        assert data["data"]["username"] == test_user.username


class TestListUsersAPI:
    """Integration tests for listing users API."""

    @pytest.mark.asyncio
    async def test_list_users(self, async_client, test_user, db_session):
        """Test listing users."""
        for i in range(5):
            user = User(
                email=f"list_api{i}@example.com",
                username=f"list_api_user{i}",
                hashed_password="hashed_pwd",
                is_active=True,
            )
            db_session.add(user)
        await db_session.commit()
        response = await async_client.get(f"{BASE_URL}/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USERS_RETRIEVED
        assert len(data["items"]) >= 1
        assert data["total"] >= 1
        for user in data["items"]:
            assert "id" in user
            assert "email" in user
            assert "username" in user
            assert "password" not in user
            assert "hashed_password" not in user

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, async_client, db_session):
        """Test pagination when listing users."""
        for i in range(15):
            user = User(
                email=f"page_api{i}@example.com",
                username=f"page_api_user{i}",
                hashed_password="hashed_pwd",
                is_active=True,
            )
            db_session.add(user)
        await db_session.commit()
        response1 = await async_client.get(f"{BASE_URL}/?skip=0&limit=5")
        response2 = await async_client.get(f"{BASE_URL}/?skip=5&limit=5")
        response3 = await async_client.get(f"{BASE_URL}/?skip=10&limit=5")
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response3.status_code == status.HTTP_200_OK
        data1, data2, data3 = response1.json(), response2.json(), response3.json()
        assert data1["page"] == 1
        assert data2["page"] == 2
        assert data3["page"] == 3
        assert data1["page_size"] == 5
        assert data2["page_size"] == 5
        assert data3["page_size"] == 5
        page1_ids = {user["id"] for user in data1["items"]}
        page2_ids = {user["id"] for user in data2["items"]}
        page3_ids = {user["id"] for user in data3["items"]}
        assert not (page1_ids & page2_ids)
        assert not (page1_ids & page3_ids)
        assert not (page2_ids & page3_ids)


class TestUpdateUserAPI:
    """Integration tests for user update API."""

    @pytest.mark.asyncio
    async def test_update_user_email(self, async_client, test_user):
        """Test updating a user's email."""
        update_data = {"email": "updated_api@example.com"}
        response = await async_client.put(
            f"{BASE_URL}/{test_user.id}", json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USER_UPDATED
        assert data["data"]["email"] == update_data["email"]
        assert data["data"]["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_update_user_username(self, async_client, test_user):
        """Test updating a user's username."""
        update_data = {"username": "updated_api_user"}
        response = await async_client.put(
            f"{BASE_URL}/{test_user.id}", json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USER_UPDATED
        assert data["data"]["username"] == update_data["username"]
        assert data["data"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_update_user_active_status(self, async_client, test_user):
        """Test updating a user's active status."""
        update_data = {"is_active": False}
        response = await async_client.put(
            f"{BASE_URL}/{test_user.id}", json=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USER_UPDATED
        assert data["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, async_client):
        """Test updating a non-existent user."""
        non_existent_id = 9999
        update_data = {"email": "nonexistent@example.com"}
        response = await async_client.put(
            f"{BASE_URL}/{non_existent_id}", json=update_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert ERR_NOT_FOUND in data["message"].lower()

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(
        self, async_client, test_user, db_session
    ):
        """Test updating a user with an email that already exists."""
        other_user = User(
            email="other@example.com",
            username="other_user",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        update_data = {"email": test_user.email}
        response = await async_client.put(
            f"{BASE_URL}/{other_user.id}", json=update_data
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert ERR_ALREADY_EXISTS in data["message"].lower()


class TestDeleteUserAPI:
    """Integration tests for user deletion API."""

    @pytest.mark.asyncio
    async def test_delete_user(self, async_client, test_user, db_session, db_client):
        """Test deleting a user."""
        user_id = test_user.id
        response = await async_client.delete(f"{BASE_URL}/{user_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == MSG_USER_DELETED
        async with db_client.async_session() as fresh_session:
            deleted_user = await fresh_session.get(User, user_id)
            assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, async_client):
        """Test deleting a non-existent user."""
        non_existent_id = 9999
        response = await async_client.delete(f"{BASE_URL}/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert ERR_NOT_FOUND in data["message"].lower()
