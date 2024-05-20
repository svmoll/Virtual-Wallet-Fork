import asyncio
import unittest
from sqlalchemy.orm import Session
from unittest.mock import patch, Mock, MagicMock, create_autospec

from app.api.routes.users.router import user_router
from app.api.routes.users.schemas import UserDTO
from app.api.routes.users.router import register_user


def fake_user():
    return UserDTO(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            phone_number="1234567890",
            is_admin=False,
            is_restricted=False
        )



class UserRouter_Should(unittest.TestCase):


    @patch('app.api.routes.users.service.create')
    def test_registerUser_IsSuccessful(self, create_mock):

        user = fake_user()
        db = create_autospec(Session)
        create_mock.return_value = user

        async def async_test():
            result = await register_user(user, db)

            create_mock.assert_called_once()

            expected_result = f"User {user.username} created successfully."
            self.assertEqual(expected_result, result)

        asyncio.run(async_test())

