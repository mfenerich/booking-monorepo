"""Unit tests for the user service module."""

import pytest
from booking_api import ConflictError, NotFoundError
from booking_shared_models.models import User
from booking_shared_models.schemas import UserCreate, UserUpdate
from sqlalchemy import text

from booking_users.services.user_service import (
    delete_user,
    get_user,
    get_user_by_email,
    get_user_by_username,
    list_users,
    register_user,
    update_user,
)


class TestRegisterUser:
    """Tests for the register_user function."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, db_session):
        """Test successful user registration."""
        # Arrange
        user_data = UserCreate(
            email="register@example.com",
            username="registeruser",
            password="password123",
        )

        # Act
        user = await register_user(db_session, user_data)

        # Assert
        assert user.email == user_data.email
        assert user.username == user_data.username
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_register_user_email_conflict(self, db_session, test_user):
        """Test registration fails with existing email."""
        # Arrange
        user_data = UserCreate(
            email=test_user.email,  # Same email as existing user
            username="uniqueuser",
            password="password123",
        )

        # Act & Assert
        with pytest.raises(ConflictError, match="User with this email already exists"):
            await register_user(db_session, user_data)

    @pytest.mark.asyncio
    async def test_register_user_username_conflict(self, db_session, test_user):
        """Test registration fails with existing username."""
        # Arrange
        user_data = UserCreate(
            email="unique@example.com",
            username=test_user.username,  # Same username as existing user
            password="password123",
        )

        # Act & Assert
        with pytest.raises(
            ConflictError, match="User with this username already exists"
        ):
            await register_user(db_session, user_data)


class TestGetUser:
    """Tests for the get_user function."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, db_session, test_user):
        """Test successful user retrieval by ID."""
        # Act
        user = await get_user(db_session, test_user.id)

        # Assert
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, db_session):
        """Test get_user raises NotFoundError when user does not exist."""
        # Arrange
        non_existent_id = 9999

        # Act & Assert
        with pytest.raises(
            NotFoundError, match=f"User with ID {non_existent_id} not found"
        ):
            await get_user(db_session, non_existent_id)

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, db_session, test_user):
        """Test successful user retrieval by email."""
        # Act
        user = await get_user_by_email(db_session, test_user.email)

        # Assert
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_session):
        """Test get_user_by_email raises NotFoundError when user does not exist."""
        # Act & Assert
        with pytest.raises(
            NotFoundError, match="User with email nonexistent@example.com not found"
        ):
            await get_user_by_email(db_session, "nonexistent@example.com")

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, db_session, test_user):
        """Test successful user retrieval by username."""
        # Act
        user = await get_user_by_username(db_session, test_user.username)

        # Assert
        assert user.id == test_user.id
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session):
        """Test get_user_by_username raises NotFoundError when user does not exist."""
        # Act & Assert
        with pytest.raises(
            NotFoundError, match="User with username nonexistent not found"
        ):
            await get_user_by_username(db_session, "nonexistent")


class TestListUsers:
    """Tests for the list_users function."""

    @pytest.mark.asyncio
    async def test_list_users_empty(self, db_session):
        """Test listing users when there are no users."""
        # Arrange - delete all users
        await db_session.execute(text("DELETE FROM users"))  # Use text() here
        await db_session.commit()

        # Act
        users, count = await list_users(db_session)

        # Assert
        assert len(users) == 0
        assert count == 0

    @pytest.mark.asyncio
    async def test_list_users_single(self, db_session, test_user):
        """Test listing users when there is one user."""
        # Act
        users, count = await list_users(db_session)

        # Assert
        assert len(users) == 1
        assert count == 1
        assert users[0].id == test_user.id

    @pytest.mark.asyncio
    async def test_list_users_multiple(self, db_session, test_user):
        """Test listing users when there are multiple users."""
        # Arrange - add another user
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        db_session.add(user2)
        await db_session.commit()

        # Act
        users, count = await list_users(db_session)

        # Assert
        assert len(users) == 2
        assert count == 2
        assert {u.email for u in users} == {test_user.email, "user2@example.com"}

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, db_session, test_user):
        """Test pagination in list_users."""
        # Arrange - add multiple users
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                hashed_password="hashed_pwd",
                is_active=True,
            )
            db_session.add(user)
        await db_session.commit()

        # Act - get first page
        users_page1, count = await list_users(db_session, skip=0, limit=3)

        # Act - get second page
        users_page2, _ = await list_users(db_session, skip=3, limit=3)

        # Assert
        assert len(users_page1) == 3
        assert len(users_page2) == 3  # 5 users + 1 test_user = 6 total
        assert count == 6
        # Check that pages are different
        assert set(u.id for u in users_page1).isdisjoint(set(u.id for u in users_page2))


class TestUpdateUser:
    """Tests for the update_user function."""

    @pytest.mark.asyncio
    async def test_update_user_email(self, db_session, test_user):
        """Test updating a user's email."""
        # Arrange
        user_data = UserUpdate(email="updated@example.com")

        # Act
        updated_user = await update_user(db_session, test_user.id, user_data)

        # Assert
        assert updated_user.email == "updated@example.com"
        # Check database was updated
        db_user = await db_session.get(User, test_user.id)
        assert db_user.email == "updated@example.com"

    @pytest.mark.asyncio
    async def test_update_user_username(self, db_session, test_user):
        """Test updating a user's username."""
        # Arrange
        user_data = UserUpdate(username="updateduser")

        # Act
        updated_user = await update_user(db_session, test_user.id, user_data)

        # Assert
        assert updated_user.username == "updateduser"
        # Check database was updated
        db_user = await db_session.get(User, test_user.id)
        assert db_user.username == "updateduser"

    @pytest.mark.asyncio
    async def test_update_user_password(self, db_session, test_user):
        """Test updating a user's password."""
        # Arrange
        original_password_hash = test_user.hashed_password
        user_data = UserUpdate(password="newpassword123")

        # Act
        await update_user(db_session, test_user.id, user_data)

        # Assert - we can't check the actual hash, but we can verify it changed
        db_user = await db_session.get(User, test_user.id)
        assert db_user.hashed_password != original_password_hash

    @pytest.mark.asyncio
    async def test_update_user_active_status(self, db_session, test_user):
        """Test updating a user's active status."""
        # Arrange
        user_data = UserUpdate(is_active=False)

        # Act
        updated_user = await update_user(db_session, test_user.id, user_data)

        # Assert
        assert updated_user.is_active is False
        # Check database was updated
        db_user = await db_session.get(User, test_user.id)
        assert db_user.is_active is False

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, db_session):
        """Test updating a non-existent user."""
        # Arrange
        user_data = UserUpdate(email="updated@example.com")
        non_existent_id = 9999

        # Act & Assert
        with pytest.raises(
            NotFoundError, match=f"User with ID {non_existent_id} not found"
        ):
            await update_user(db_session, non_existent_id, user_data)

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(self, db_session, test_user):
        """Test updating a user with an email that already exists."""
        # Arrange - create another user
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        db_session.add(user2)
        await db_session.commit()

        # Update user2 with test_user's email
        user_data = UserUpdate(email=test_user.email)

        # Act & Assert
        with pytest.raises(ConflictError, match="User with this email already exists"):
            await update_user(db_session, user2.id, user_data)

    @pytest.mark.asyncio
    async def test_update_user_username_conflict(self, db_session, test_user):
        """Test updating a user with a username that already exists."""
        # Arrange - create another user
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        db_session.add(user2)
        await db_session.commit()

        # Update user2 with test_user's username
        user_data = UserUpdate(username=test_user.username)

        # Act & Assert
        with pytest.raises(
            ConflictError, match="User with this username already exists"
        ):
            await update_user(db_session, user2.id, user_data)

    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, db_session, test_user):
        """Test updating a user with no changes."""
        # Arrange
        user_data = UserUpdate()  # Empty update

        # Act
        updated_user = await update_user(db_session, test_user.id, user_data)

        # Assert - should return the original user
        assert updated_user.id == test_user.id
        assert updated_user.email == test_user.email
        assert updated_user.username == test_user.username


class TestDeleteUser:
    """Tests for the delete_user function."""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session, test_user):
        """Test successful user deletion."""
        # Act
        result = await delete_user(db_session, test_user.id)

        # Assert
        assert result is True
        # Verify user is deleted from database
        remaining_user = await db_session.get(User, test_user.id)
        assert remaining_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, db_session):
        """Test deleting a non-existent user."""
        # Arrange
        non_existent_id = 9999

        # Act & Assert
        with pytest.raises(
            NotFoundError, match=f"User with ID {non_existent_id} not found"
        ):
            await delete_user(db_session, non_existent_id)
