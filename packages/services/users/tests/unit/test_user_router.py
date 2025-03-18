"""Unit tests for the user router endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from booking_api import ConflictError, NotFoundError
from booking_shared_models.schemas import User

# Constants for URIs
BASE_URI = "/api/v1/users"
REGISTER_URI = f"{BASE_URI}/register"
USER_BY_ID_URI = f"{BASE_URI}/{{user_id}}"
USER_BY_EMAIL_URI = f"{BASE_URI}/by-email/{{email}}"
USER_BY_USERNAME_URI = f"{BASE_URI}/by-username/{{username}}"
USERS_URI = f"{BASE_URI}/"


@pytest.fixture
def mock_user_dict():
    """Create a mock user dictionary."""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True,
        "created_at": "2025-03-18T00:00:00",
        "updated_at": "2025-03-18T00:00:00",
    }


@pytest.fixture
def mock_user(mock_user_dict):
    """Create a mock user object."""
    return User.model_validate(mock_user_dict)


class TestRegisterEndpoint:
    """Tests for the /register endpoint."""

    def test_register_success(self, client, mock_user):
        """Test successful user registration endpoint."""
        # Arrange
        user_data = {
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123",
        }

        with patch(
            "booking_users.routers.user_router.register_user", new=AsyncMock()
        ) as mock_service:
            mock_service.return_value = mock_user

            # Act
            response = client.post(REGISTER_URI, json=user_data)
            # Assert
            assert response.status_code == 201
            result = response.json()
            assert result["success"] is True
            assert result["message"] == "User registered successfully"
            assert result["data"]["email"] == mock_user.email
            mock_service.assert_called_once()

    def test_register_validation_error(self, client):
        """Test validation error on registration endpoint."""
        # Arrange - missing required fields
        user_data = {
            "username": "newuser",
            # Missing email and password
        }

        # Act
        response = client.post(REGISTER_URI, json=user_data)

        # Assert
        assert response.status_code == 422  # Validation error
        result = response.json()
        assert "details" in result
        assert "errors" in result["details"]
        # Ensure error mentions the missing field
        assert any("email" in error["loc"] for error in result["details"]["errors"])

    def test_register_conflict_error(self, client):
        """Test conflict error on registration endpoint."""
        # Arrange
        user_data = {
            "email": "existing@example.com",
            "username": "existinguser",
            "password": "password123",
        }

        with patch(
            "booking_users.routers.user_router.register_user", new=AsyncMock()
        ) as mock_service:
            mock_service.side_effect = ConflictError(
                "User with this email already exists"
            )

            # Act
            response = client.post(REGISTER_URI, json=user_data)

            # Assert
            assert response.status_code == 409
            result = response.json()
            assert result["success"] is False
            assert "already exists" in result["message"]
            mock_service.assert_called_once()


class TestGetUserEndpoints:
    """Tests for user retrieval endpoints."""

    def test_get_user_by_id_success(self, client, mock_user):
        """Test successful user retrieval by ID endpoint."""
        # Arrange
        user_id = 1

        with patch(
            "booking_users.routers.user_router.get_user", new=AsyncMock()
        ) as mock_service:
            mock_service.return_value = mock_user

            # Act
            response = client.get(USER_BY_ID_URI.format(user_id=user_id))

            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["message"] == "User retrieved successfully"
            assert result["data"]["id"] == user_id
            # Don't check the session parameter name specifically
            mock_service.assert_called_once()
            assert (
                mock_service.call_args[0][1] == user_id
                or mock_service.call_args[1].get("user_id") == user_id
            )

    def test_get_user_by_id_not_found(self, client):
        """Test user retrieval with non-existent ID endpoint."""
        # Arrange
        user_id = 999

        with patch(
            "booking_users.routers.user_router.get_user", new=AsyncMock()
        ) as mock_service:
            mock_service.side_effect = NotFoundError(
                f"User with ID {user_id} not found"
            )

            # Act
            response = client.get(USER_BY_ID_URI.format(user_id=user_id))

            # Assert
            assert response.status_code == 404
            result = response.json()
            assert result["success"] is False
            assert "not found" in result["message"]
            mock_service.assert_called_once()

    def test_get_user_by_email_success(self, client, mock_user):
        """Test successful user retrieval by email endpoint."""
        # Arrange
        email = "test@example.com"

        with patch(
            "booking_users.routers.user_router.get_user_by_email", new=AsyncMock()
        ) as mock_service:
            mock_service.return_value = mock_user

            # Act
            response = client.get(USER_BY_EMAIL_URI.format(email=email))

            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["message"] == "User retrieved successfully"
            assert result["data"]["email"] == email
            mock_service.assert_called_once()

    def test_get_user_by_email_invalid_format(self, client):
        """Test user retrieval with invalid email format."""
        # Arrange
        invalid_email = "invalid-email"

        # Act
        response = client.get(USER_BY_EMAIL_URI.format(email=invalid_email))

        # Assert
        assert response.status_code == 422  # Validation error
        result = response.json()
        assert "details" in result
        assert "errors" in result["details"]
        # Check that error is related to email validation
        email_errors = [
            err for err in result["details"]["errors"] if "email" in str(err)
        ]
        assert len(email_errors) > 0

    def test_get_user_by_username_success(self, client, mock_user):
        """Test successful user retrieval by username endpoint."""
        # Arrange
        username = "testuser"

        with patch(
            "booking_users.routers.user_router.get_user_by_username", new=AsyncMock()
        ) as mock_service:
            mock_service.return_value = mock_user

            # Act
            response = client.get(USER_BY_USERNAME_URI.format(username=username))

            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["message"] == "User retrieved successfully"
            assert result["data"]["username"] == username
            mock_service.assert_called_once()


class TestListUsersEndpoint:
    """Tests for the list users endpoint."""

    def test_list_users_success(self, client, mock_user):
        """Test successful listing of users endpoint."""
        # Arrange
        users = [mock_user, mock_user]
        total = len(users)

        with patch(
            "booking_users.routers.user_router.list_users", new=AsyncMock()
        ) as mock_service:
            mock_service.return_value = (users, total)

            # Act
            response = client.get(f"{USERS_URI}?skip=0&limit=10")

            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["message"] == "Users retrieved successfully"
            assert len(result["items"]) == len(users)
            assert result["page"] == 1
            assert result["page_size"] == 10
            assert result["total"] == total
            mock_service.assert_called_once()

    def test_list_users_pagination(self, client, mock_user):
        """Test pagination parameters in list users endpoint."""
        # Arrange
        users = [mock_user]
        total = 100  # Pretend we have 100 users total

        with patch(
            "booking_users.routers.user_router.list_users", new=AsyncMock()
        ) as mock_service:
            mock_service.return_value = (users, total)

            # Act
            response = client.get(f"{USERS_URI}?skip=20&limit=10")

            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["page"] == 3  # (skip=20 / limit=10) + 1 = 3
            assert result["page_size"] == 10
            assert result["total"] == total
            # Don't check the session parameter name specifically
            mock_service.assert_called_once()
            call_kwargs = mock_service.call_args[1]
            assert call_kwargs.get("skip") == 20 or call_kwargs.get("offset") == 20
            assert call_kwargs.get("limit") == 10

    def test_list_users_negative_skip(self, client):
        """Test list users with negative skip parameter."""
        # Act
        response = client.get(f"{USERS_URI}?skip=-10&limit=10")

        # Assert
        assert response.status_code == 422  # Validation error
        result = response.json()
        assert "details" in result
        assert "errors" in result["details"]
        # Error should mention the skip parameter
        assert any("skip" in str(error["loc"]) for error in result["details"]["errors"])

    def test_list_users_too_large_limit(self, client):
        """Test list users with limit exceeding maximum."""
        # Act
        response = client.get(f"{USERS_URI}?skip=0&limit=1000")

        # Assert
        assert response.status_code == 422  # Validation error
        result = response.json()
        assert "details" in result
        assert "errors" in result["details"]
        # Error should mention the limit parameter
        assert any(
            "limit" in str(error["loc"]) for error in result["details"]["errors"]
        )


class TestUpdateUserEndpoint:
    """Tests for the update user endpoint."""

    def test_update_user_success(self, client, mock_user):
        """Test successful user update endpoint."""
        # Arrange
        user_id = 1
        update_data = {"email": "updated@example.com"}

        with patch(
            "booking_users.routers.user_router.update_user", new=AsyncMock()
        ) as mock_service:
            updated_user = mock_user.model_copy(update={"email": "updated@example.com"})
            mock_service.return_value = updated_user

            # Act
            response = client.put(
                USER_BY_ID_URI.format(user_id=user_id), json=update_data
            )

            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["message"] == "User updated successfully"
            assert result["data"]["email"] == "updated@example.com"
            mock_service.assert_called_once()

    def test_update_user_not_found(self, client):
        """Test updating a non-existent user."""
        # Arrange
        user_id = 999
        update_data = {"email": "updated@example.com"}

        with patch(
            "booking_users.routers.user_router.update_user", new=AsyncMock()
        ) as mock_service:
            mock_service.side_effect = NotFoundError(
                f"User with ID {user_id} not found"
            )

            # Act
            response = client.put(
                USER_BY_ID_URI.format(user_id=user_id), json=update_data
            )

            # Assert
            assert response.status_code == 404
            result = response.json()
            assert result["success"] is False
            assert "not found" in result["message"]
            mock_service.assert_called_once()

    def test_update_user_conflict(self, client):
        """Test update with conflicting data."""
        # Arrange
        user_id = 1
        update_data = {"email": "existing@example.com"}

        with patch(
            "booking_users.routers.user_router.update_user", new=AsyncMock()
        ) as mock_service:
            mock_service.side_effect = ConflictError(
                "User with this email already exists"
            )

            # Act
            response = client.put(
                USER_BY_ID_URI.format(user_id=user_id), json=update_data
            )

            # Assert
            assert response.status_code == 409
            result = response.json()
            assert result["success"] is False
            assert "already exists" in result["message"]
            mock_service.assert_called_once()

    def test_update_user_invalid_email(self, client):
        """Test update with invalid email format."""
        # Arrange
        user_id = 1
        update_data = {"email": "invalid-email"}

        # Act
        response = client.put(USER_BY_ID_URI.format(user_id=user_id), json=update_data)

        # Assert
        assert response.status_code == 422  # Validation error
        result = response.json()
        assert "details" in result
        assert "errors" in result["details"]
        # Error should mention the email field
        assert any(
            "email" in str(error["loc"]) for error in result["details"]["errors"]
        )


class TestDeleteUserEndpoint:
    """Tests for the delete user endpoint."""

    def test_delete_user_success(self, client):
        """Test successful user deletion endpoint."""
        # Arrange
        user_id = 1

        with patch(
            "booking_users.routers.user_router.delete_user", new=AsyncMock()
        ) as mock_service:
            mock_service.return_value = True

            # Act
            response = client.delete(USER_BY_ID_URI.format(user_id=user_id))

            # Assert
            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert result["message"] == "User deleted successfully"
            mock_service.assert_called_once()
            # Check that user_id is in the arguments, without requiring specific parameter name
            call_args = mock_service.call_args
            passed_user_id = None
            if len(call_args[0]) > 1:
                passed_user_id = call_args[0][1]  # Positional argument
            else:
                passed_user_id = call_args[1].get("user_id")  # Keyword argument
            assert passed_user_id == user_id

    def test_delete_user_not_found(self, client):
        """Test deleting a non-existent user."""
        # Arrange
        user_id = 999

        with patch(
            "booking_users.routers.user_router.delete_user", new=AsyncMock()
        ) as mock_service:
            mock_service.side_effect = NotFoundError(
                f"User with ID {user_id} not found"
            )

            # Act
            response = client.delete(USER_BY_ID_URI.format(user_id=user_id))

            # Assert
            assert response.status_code == 404
            result = response.json()
            assert result["success"] is False
            assert "not found" in result["message"]
            mock_service.assert_called_once()
