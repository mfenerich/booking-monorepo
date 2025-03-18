from typing import Any, Dict, Optional

import httpx


class UserInfoProvider:
    """Helper class for fetching user information across services"""

    def __init__(self, users_service_url: str):
        """
        Initialize with the URL of the users service
        """
        self.users_service_url = users_service_url

    async def get_user_by_id(
        self, user_id: str, token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID.
        Requires a valid token with authorization to access user data.
        """
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.users_service_url}/api/v1/users/{user_id}", headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return result.get("data")
                return None
            except Exception:
                return None

    @staticmethod
    def from_settings():
        """Factory method to create provider from settings"""
        import os

        users_url = os.getenv("USERS_SERVICE_URL", "http://localhost:8000")
        return UserInfoProvider(users_url)
