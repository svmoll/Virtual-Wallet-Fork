import asyncio
import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock, MagicMock, create_autospec
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth_service.auth import authenticate_user
from app.api.routes.users.router import register_user, login
from app.api.routes.users.schemas import UserDTO


client = TestClient(app)


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
    #
    # @patch("app.api.auth_service.auth")
    # def test_login_isSuccessful(self, authenticate_mock):
    #     db = fake_db()
    #     authenticate_mock.return_value = fake_user()
    #
    #     async def async_test():
    #         result = await login(fake_data, db)
    #
    #     asyncio.run(async_test())
    #
    # @patch('app.api.auth_service.auth.authenticate_user')
    # @patch('app.api.auth_service.auth.create_token')
    # def test_login_success(self, mock_create_token, mock_authenticate_user):
    #     mock_authenticate_user.return_value = {"username": "valid_user"}
    #     mock_create_token.return_value = "mock_access_token"
    #
    #     response = self.client.post("/login", data={"username": "valid_user"})
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json( ), {"access_token": "mock_access_token", "token_type": "bearer"})
    #
    # @patch('app.api.auth_service.auth.authenticate_user')
    # @patch('app.api.auth_service.auth.create_token')
    # def test_login_success(self, mock_create_token, mock_authenticate_user):
    #     # Mock return values
    #     mock_authenticate_user.return_value = {"username": "valid_user"}
    #     mock_create_token.return_value = "mock_access_token"
    #
    #     # Perform the POST request
    #     response = client.post("/login", data={"username": "valid_user", "password": "valid_password"})
    #
    #     # Assert the response
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json( ), {"access_token": "mock_access_token", "token_type": "bearer"})
    #
    #     # Assert that mocks were called with expected arguments
    #     mock_authenticate_user.assert_called_once_with(MagicMock( ), "valid_user", "valid_password")
    #     mock_create_token.assert_called_once( )