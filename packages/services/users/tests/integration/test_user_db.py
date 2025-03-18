"""Additional tests for user database operations."""

import pytest
from booking_api import ConflictError, NotFoundError
from booking_auth import verify_password
from booking_shared_models.models import User
from booking_shared_models.schemas import UserUpdate

from booking_users.services.user_service import (
    get_user,
    get_user_by_email,
    get_user_by_username,
    update_user,
)


class TestUserDatabaseRetrieval:
    """Tests for user retrieval operations."""

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, db_session, test_user):
        """Test retrieving a user by ID."""
        # Act
        user = await get_user(db_session, test_user.id)

        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, db_session):
        """Test get_user with non-existent ID."""
        # Arrange
        non_existent_id = 9999

        # Act & Assert
        with pytest.raises(
            NotFoundError, match=f"User with ID {non_existent_id} not found"
        ):
            await get_user(db_session, non_existent_id)

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session, test_user):
        """Test retrieving a user by email."""
        # Act
        user = await get_user_by_email(db_session, test_user.email)

        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_session):
        """Test get_user_by_email with non-existent email."""
        # Act & Assert
        with pytest.raises(
            NotFoundError, match="User with email nonexistent@example.com not found"
        ):
            await get_user_by_email(db_session, "nonexistent@example.com")

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session, test_user):
        """Test retrieving a user by username."""
        # Act
        user = await get_user_by_username(db_session, test_user.username)

        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session):
        """Test get_user_by_username with non-existent username."""
        # Act & Assert
        with pytest.raises(
            NotFoundError, match="User with username nonexistent not found"
        ):
            await get_user_by_username(db_session, "nonexistent")


class TestUserDatabaseUpdate:
    """Tests for user update operations."""

    @pytest.mark.asyncio
    async def test_update_user_email(self, db_session, test_user):
        """Test updating a user's email."""
        # Arrange
        new_email = "updated_db_test@example.com"
        update_data = UserUpdate(email=new_email)

        # Act
        updated_user = await update_user(db_session, test_user.id, update_data)

        # Assert
        assert updated_user.email == new_email

        # Verify in database
        db_user = await db_session.get(User, test_user.id)
        assert db_user.email == new_email

    @pytest.mark.asyncio
    async def test_update_user_username(self, db_session, test_user):
        """Test updating a user's username."""
        # Arrange
        new_username = "updated_db_username"
        update_data = UserUpdate(username=new_username)

        # Act
        updated_user = await update_user(db_session, test_user.id, update_data)

        # Assert
        assert updated_user.username == new_username

        # Verify in database
        db_user = await db_session.get(User, test_user.id)
        assert db_user.username == new_username

    @pytest.mark.asyncio
    async def test_update_user_password(self, db_session, test_user):
        """Test updating a user's password."""
        # Arrange
        original_hash = test_user.hashed_password
        new_password = "NewSecurePassword123!"
        update_data = UserUpdate(password=new_password)

        # Act
        await update_user(db_session, test_user.id, update_data)

        # Assert - password should be hashed differently
        db_user = await db_session.get(User, test_user.id)
        assert db_user.hashed_password != original_hash
        assert verify_password(new_password, db_user.hashed_password)

    @pytest.mark.asyncio
    async def test_update_user_active_status(self, db_session, test_user):
        """Test updating a user's active status."""
        # Arrange - ensure user is active initially
        test_user.is_active = True
        await db_session.commit()

        # Update to inactive
        update_data = UserUpdate(is_active=False)

        # Act
        updated_user = await update_user(db_session, test_user.id, update_data)

        # Assert
        assert updated_user.is_active is False

        # Verify in database
        db_user = await db_session.get(User, test_user.id)
        assert db_user.is_active is False

    @pytest.mark.asyncio
    async def test_update_user_multiple_fields(self, db_session, test_user):
        """Test updating multiple user fields at once."""
        # Arrange
        update_data = UserUpdate(
            email="multi_update@example.com",
            username="multi_update_user",
            is_active=False,
        )

        # Act
        updated_user = await update_user(db_session, test_user.id, update_data)

        # Assert
        assert updated_user.email == update_data.email
        assert updated_user.username == update_data.username
        assert updated_user.is_active is update_data.is_active

        # Verify in database
        db_user = await db_session.get(User, test_user.id)
        assert db_user.email == update_data.email
        assert db_user.username == update_data.username
        assert db_user.is_active is update_data.is_active

    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, db_session, test_user):
        """Test updating a user with no changes."""
        # Arrange - create empty update
        update_data = UserUpdate()

        # Act
        updated_user = await update_user(db_session, test_user.id, update_data)

        # Assert - should return user with no changes
        assert updated_user.id == test_user.id
        assert updated_user.email == test_user.email
        assert updated_user.username == test_user.username
        assert updated_user.is_active == test_user.is_active

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, db_session):
        """Test updating a non-existent user."""
        # Arrange
        non_existent_id = 9999
        update_data = UserUpdate(email="nonexistent@example.com")

        # Act & Assert
        with pytest.raises(
            NotFoundError, match=f"User with ID {non_existent_id} not found"
        ):
            await update_user(db_session, non_existent_id, update_data)

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(self, db_session, test_user):
        """Test updating a user with an email that already exists."""
        # Arrange - create another user
        other_user = User(
            email="other_db@example.com",
            username="other_db_user",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()

        # Try to update other_user with test_user's email
        update_data = UserUpdate(email=test_user.email)

        # Act & Assert
        with pytest.raises(ConflictError, match="User with this email already exists"):
            await update_user(db_session, other_user.id, update_data)

    @pytest.mark.asyncio
    async def test_update_user_username_conflict(self, db_session, test_user):
        """Test updating a user with a username that already exists."""
        # Arrange - create another user
        other_user = User(
            email="other_username_db@example.com",
            username="other_username_db_user",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()

        # Try to update other_user with test_user's username
        update_data = UserUpdate(username=test_user.username)

        # Act & Assert
        with pytest.raises(
            ConflictError, match="User with this username already exists"
        ):
            await update_user(db_session, other_user.id, update_data)
