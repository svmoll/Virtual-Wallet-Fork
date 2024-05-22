import asyncio
import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock, MagicMock, create_autospec
from app.api.routes.users.router import register_user
from app.api.routes.users.schemas import UserDTO


def fake_user():
    return UserDTO(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            phone_number="1234567890",
            is_admin=False,
            is_restricted=False
        )

Session = sessionmaker()
def fake_db():
    return MagicMock(spec=Session)


class UserRouter_Should(unittest.TestCase):


    @patch('app.api.routes.users.service.create')
    def test_registerUser_IsSuccessful(self, create_mock):
        #arrange
        user = fake_user()
        db = fake_db()
        create_mock.return_value = user
        # Act
        async def async_test():
            result = await register_user(user, db)
        #Assert
            create_mock.assert_called_once()
            expected_result = f"User {user.username} created successfully."
            self.assertEqual(expected_result, result)

        asyncio.run(async_test())

