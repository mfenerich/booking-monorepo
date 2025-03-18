"""Integration tests for the User API endpoints."""

import pytest
from booking_shared_models.models import User
from fastapi import status


class TestUserRegistrationAPI:
    """Integration tests for user registration API."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client, test_user_create):
        """Test successful user registration via API."""
        # Arrange
        user_data = {
            "email": test_user_create.email,
            "username": test_user_create.username,
            "password": test_user_create.password,
        }

        # Act
        response = await async_client.post("/api/v1/users/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User registered successfully"
        assert data["data"]["email"] == user_data["email"]
        assert data["data"]["username"] == user_data["username"]
        assert "password" not in data["data"]  # Password should not be returned
        assert (
            "hashed_password" not in data["data"]
        )  # Hashed password should not be returned

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, async_client, test_user, test_user_create
    ):
        """Test registration with duplicate email."""
        # Arrange - use existing test_user's email
        user_data = {
            "email": test_user.email,  # Already exists
            "username": test_user_create.username,
            "password": test_user_create.password,
        }

        # Act
        response = await async_client.post("/api/v1/users/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["message"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self, async_client, test_user, test_user_create
    ):
        """Test registration with duplicate username."""
        # Arrange - use existing test_user's username
        user_data = {
            "email": test_user_create.email,
            "username": test_user.username,  # Already exists
            "password": test_user_create.password,
        }

        # Act
        response = await async_client.post("/api/v1/users/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["message"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client):
        """Test registration with invalid email format."""
        # Arrange
        user_data = {
            "email": "invalid-email",  # Invalid format
            "username": "testuser123",
            "password": "password123",
        }

        # Act
        response = await async_client.post("/api/v1/users/register", json=user_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        # Check if response has details.errors structure (newer FastAPI versions)
        if "details" in data and "errors" in data["details"]:
            assert any(
                "email" in str(error["loc"]) for error in data["details"]["errors"]
            )
        # Or if it has the classic detail structure (older FastAPI versions)
        elif "detail" in data:
            assert any("email" in str(error["loc"]) for error in data["detail"])
        else:
            # Fail the test if neither expected structure is found
            assert False, "Validation error response doesn't have expected structure"


class TestGetUserAPI:
    """Integration tests for user retrieval API."""

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, async_client, test_user):
        """Test getting a user by ID."""
        # Act
        response = await async_client.get(f"/api/v1/users/{test_user.id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User retrieved successfully"
        assert data["data"]["id"] == test_user.id
        assert data["data"]["email"] == test_user.email
        assert data["data"]["username"] == test_user.username
        assert "password" not in data["data"]
        assert "hashed_password" not in data["data"]

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, async_client):
        """Test getting a non-existent user."""
        # Arrange
        non_existent_id = 9999

        # Act
        response = await async_client.get(f"/api/v1/users/{non_existent_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, async_client, test_user):
        """Test getting a user by email."""
        # Act
        response = await async_client.get(f"/api/v1/users/by-email/{test_user.email}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User retrieved successfully"
        assert data["data"]["id"] == test_user.id
        assert data["data"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, async_client):
        """Test getting a user by email that doesn't exist."""
        # Act
        response = await async_client.get(
            "/api/v1/users/by-email/nonexistent@example.com"
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, async_client, test_user):
        """Test getting a user by username."""
        # Act
        response = await async_client.get(
            f"/api/v1/users/by-username/{test_user.username}"
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User retrieved successfully"
        assert data["data"]["id"] == test_user.id
        assert data["data"]["username"] == test_user.username


class TestListUsersAPI:
    """Integration tests for listing users API."""

    @pytest.mark.asyncio
    async def test_list_users(self, async_client, test_user, db_session):
        """Test listing users."""
        # Arrange - add more users
        for i in range(5):
            user = User(
                email=f"list_api{i}@example.com",
                username=f"list_api_user{i}",
                hashed_password="hashed_pwd",
                is_active=True,
            )
            db_session.add(user)
        await db_session.commit()

        # Act
        response = await async_client.get("/api/v1/users/")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Users retrieved successfully"
        assert len(data["items"]) >= 1  # At least the test_user
        assert data["total"] >= 1

        # Check fields
        for user in data["items"]:
            assert "id" in user
            assert "email" in user
            assert "username" in user
            assert "password" not in user
            assert "hashed_password" not in user

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, async_client, db_session):
        """Test pagination when listing users."""
        # Arrange - add many users
        for i in range(15):  # Add 15 users to ensure we have enough for pagination
            user = User(
                email=f"page_api{i}@example.com",
                username=f"page_api_user{i}",
                hashed_password="hashed_pwd",
                is_active=True,
            )
            db_session.add(user)
        await db_session.commit()

        # Act - get first page
        response1 = await async_client.get("/api/v1/users/?skip=0&limit=5")

        # Act - get second page
        response2 = await async_client.get("/api/v1/users/?skip=5&limit=5")

        # Act - get third page
        response3 = await async_client.get("/api/v1/users/?skip=10&limit=5")

        # Assert
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response3.status_code == status.HTTP_200_OK

        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()

        # Check pagination info
        assert data1["page"] == 1
        assert data2["page"] == 2
        assert data3["page"] == 3

        assert data1["page_size"] == 5
        assert data2["page_size"] == 5
        assert data3["page_size"] == 5

        # Check items are different on each page
        page1_ids = {user["id"] for user in data1["items"]}
        page2_ids = {user["id"] for user in data2["items"]}
        page3_ids = {user["id"] for user in data3["items"]}

        assert len(page1_ids.intersection(page2_ids)) == 0
        assert len(page1_ids.intersection(page3_ids)) == 0
        assert len(page2_ids.intersection(page3_ids)) == 0


class TestUpdateUserAPI:
    """Integration tests for user update API."""

    @pytest.mark.asyncio
    async def test_update_user_email(self, async_client, test_user):
        """Test updating a user's email."""
        # Arrange
        update_data = {"email": "updated_api@example.com"}

        # Act
        response = await async_client.put(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User updated successfully"
        assert data["data"]["email"] == update_data["email"]
        assert data["data"]["username"] == test_user.username  # Unchanged

    @pytest.mark.asyncio
    async def test_update_user_username(self, async_client, test_user):
        """Test updating a user's username."""
        # Arrange
        update_data = {"username": "updated_api_user"}

        # Act
        response = await async_client.put(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User updated successfully"
        assert data["data"]["username"] == update_data["username"]
        assert data["data"]["email"] == test_user.email  # Unchanged

    @pytest.mark.asyncio
    async def test_update_user_active_status(self, async_client, test_user):
        """Test updating a user's active status."""
        # Arrange
        update_data = {"is_active": False}

        # Act
        response = await async_client.put(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User updated successfully"
        assert data["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, async_client):
        """Test updating a non-existent user."""
        # Arrange
        non_existent_id = 9999
        update_data = {"email": "nonexistent@example.com"}

        # Act
        response = await async_client.put(
            f"/api/v1/users/{non_existent_id}", json=update_data
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(
        self, async_client, test_user, db_session
    ):
        """Test updating a user with an email that already exists."""
        # Arrange - create another user
        other_user = User(
            email="other@example.com",
            username="other_user",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()

        # Try to update other_user with test_user's email
        update_data = {"email": test_user.email}

        # Act
        response = await async_client.put(
            f"/api/v1/users/{other_user.id}", json=update_data
        )

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["message"].lower()


class TestDeleteUserAPI:
    """Integration tests for user deletion API."""

    @pytest.mark.asyncio
    async def test_delete_user(self, async_client, test_user, db_session, db_client):
        """Test deleting a user."""
        # Store the user ID for later verification
        user_id = test_user.id

        # Act
        response = await async_client.delete(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User deleted successfully"

        # Create a fresh session to verify the deletion
        # This ensures we don't have stale data from the current session
        async with db_client.async_session() as fresh_session:
            # Verify user is deleted from database
            deleted_user = await fresh_session.get(User, user_id)
            assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, async_client):
        """Test deleting a non-existent user."""
        # Arrange
        non_existent_id = 9999

        # Act
        response = await async_client.delete(f"/api/v1/users/{non_existent_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
