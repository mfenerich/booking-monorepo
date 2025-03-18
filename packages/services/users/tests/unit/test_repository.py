"""Unit tests for the user repository."""

import pytest
from booking_shared_models.models import User
from sqlalchemy import select

from booking_users.services.repository import UserRepository, user_repository


@pytest.mark.asyncio
async def test_repository_singleton():
    """Test that user_repository is a singleton instance of UserRepository."""
    assert isinstance(user_repository, UserRepository)
    assert user_repository.model == User


class TestUserRepository:
    """Tests for the UserRepository class."""

    @pytest.mark.asyncio
    async def test_create(self, db_session):
        """Test creating a user."""
        # Arrange
        user_data = {
            "email": "repo_test@example.com",
            "username": "repo_user",
            "hashed_password": "hashed_password",
            "is_active": True,
        }

        # Act
        user = await user_repository.create(db_session, user_data)

        # Assert
        assert user.id is not None
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert user.hashed_password == user_data["hashed_password"]
        assert user.is_active == user_data["is_active"]

        # Check it's in the database
        db_user = await db_session.get(User, user.id)
        assert db_user is not None
        assert db_user.email == user.email

    @pytest.mark.asyncio
    async def test_get(self, db_session, test_user):
        """Test getting a user by ID."""
        # Act
        user = await user_repository.get(db_session, test_user.id)

        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, db_session):
        """Test getting a non-existent user."""
        # Act
        user = await user_repository.get(db_session, 9999)

        # Assert
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_email(self, db_session, test_user):
        """Test getting a user by email."""
        # Act
        user = await user_repository.get_by_email(db_session, test_user.email)

        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_by_email_nonexistent(self, db_session):
        """Test getting a non-existent user by email."""
        # Act
        user = await user_repository.get_by_email(db_session, "nonexistent@example.com")

        # Assert
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_username(self, db_session, test_user):
        """Test getting a user by username."""
        # Act
        user = await user_repository.get_by_username(db_session, test_user.username)

        # Assert
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_by_username_nonexistent(self, db_session):
        """Test getting a non-existent user by username."""
        # Act
        user = await user_repository.get_by_username(db_session, "nonexistent")

        # Assert
        assert user is None

    @pytest.mark.asyncio
    async def test_list(self, db_session, test_user):
        """Test listing users."""
        # Arrange - add a few more users
        for i in range(5):
            user = User(
                email=f"list{i}@example.com",
                username=f"list_user{i}",
                hashed_password="hashed_pwd",
                is_active=True,
            )
            db_session.add(user)
        await db_session.commit()

        # Act
        users = await user_repository.list(db_session)

        # Assert
        assert len(users) >= 6  # test_user + 5 new users
        assert any(u.id == test_user.id for u in users)

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, db_session, test_user):
        """Test listing users with pagination."""
        # Arrange - add a few more users
        for i in range(10):
            user = User(
                email=f"page{i}@example.com",
                username=f"page_user{i}",
                hashed_password="hashed_pwd",
                is_active=True,
            )
            db_session.add(user)
        await db_session.commit()

        # Act
        users_page1 = await user_repository.list(db_session, skip=0, limit=5)
        users_page2 = await user_repository.list(db_session, skip=5, limit=5)

        # Assert
        assert len(users_page1) == 5
        assert len(users_page2) == 5
        # Check pages are different
        page1_ids = {u.id for u in users_page1}
        page2_ids = {u.id for u in users_page2}
        assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_list_with_custom_query(self, db_session, test_user):
        """Test listing users with a custom query."""
        # Arrange - add users with different active statuses
        user_active = User(
            email="active@example.com",
            username="active_user",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        user_inactive = User(
            email="inactive@example.com",
            username="inactive_user",
            hashed_password="hashed_pwd",
            is_active=False,
        )
        db_session.add_all([user_active, user_inactive])
        await db_session.commit()

        # Act - query only active users
        query = select(User).where(User.is_active.is_(True))
        active_users = await user_repository.list(db_session, stmt=query)

        # Act - query only inactive users
        query = select(User).where(User.is_active.is_(False))
        inactive_users = await user_repository.list(db_session, stmt=query)

        # Assert
        assert all(u.is_active for u in active_users)
        assert all(not u.is_active for u in inactive_users)
        assert len(inactive_users) >= 1

    @pytest.mark.asyncio
    async def test_count(self, db_session):
        """Test counting users."""
        # Arrange - get current count
        initial_count = await user_repository.count(db_session)

        # Arrange - add more users
        for i in range(3):
            user = User(
                email=f"count{i}@example.com",
                username=f"count_user{i}",
                hashed_password="hashed_pwd",
                is_active=True,
            )
            db_session.add(user)
        await db_session.commit()

        # Act
        new_count = await user_repository.count(db_session)

        # Assert
        assert new_count == initial_count + 3

    @pytest.mark.asyncio
    async def test_count_with_query(self, db_session):
        """Test counting users with a filtered query."""
        # Arrange - add users with different active statuses
        user_active = User(
            email="count_active@example.com",
            username="count_active_user",
            hashed_password="hashed_pwd",
            is_active=True,
        )
        user_inactive = User(
            email="count_inactive@example.com",
            username="count_inactive_user",
            hashed_password="hashed_pwd",
            is_active=False,
        )
        db_session.add_all([user_active, user_inactive])
        await db_session.commit()

        # Act - count only active users
        query = select(User).where(User.is_active.is_(True))
        active_count = await user_repository.count(db_session, stmt=query)

        # Act - count only inactive users
        query = select(User).where(User.is_active.is_(False))
        inactive_count = await user_repository.count(db_session, stmt=query)

        # Assert
        assert active_count >= 1
        assert inactive_count >= 1

        # Total should equal sum of active and inactive
        total_count = await user_repository.count(db_session)
        assert total_count >= active_count + inactive_count

    @pytest.mark.asyncio
    async def test_update(self, db_session, test_user):
        """Test updating a user."""
        # Arrange
        update_data = {
            "email": "updated_repo@example.com",
            "username": "updated_repo_user",
        }

        # Act
        updated_user = await user_repository.update(
            db_session, test_user.id, update_data
        )

        # Assert
        assert updated_user is not None
        assert updated_user.id == test_user.id
        assert updated_user.email == update_data["email"]
        assert updated_user.username == update_data["username"]

        # Check database was updated
        db_user = await db_session.get(User, test_user.id)
        assert db_user.email == update_data["email"]
        assert db_user.username == update_data["username"]

    @pytest.mark.asyncio
    async def test_update_nonexistent(self, db_session):
        """Test updating a non-existent user."""
        # Arrange
        update_data = {"email": "nonexistent@example.com"}

        # Act
        updated_user = await user_repository.update(db_session, 9999, update_data)

        # Assert
        assert updated_user is None

    @pytest.mark.asyncio
    async def test_delete(self, db_session, test_user):
        """Test deleting a user."""
        # Act
        result = await user_repository.delete(db_session, test_user.id)

        # Assert
        assert result is True

        # Check user is deleted from database
        db_user = await db_session.get(User, test_user.id)
        assert db_user is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, db_session):
        """Test deleting a non-existent user."""
        # Act
        result = await user_repository.delete(db_session, 9999)

        # Assert
        assert result is False
