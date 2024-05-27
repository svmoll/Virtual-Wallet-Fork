import asyncio
import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock, MagicMock, create_autospec
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth_service.auth import authenticate_user
from app.api.routes.users.router import register_user, login, update
from app.api.routes.users.schemas import UserDTO, UpdateUserDTO, UserViewDTO

client = TestClient(app)

ACCESS_TOKEN = "test_token"
USERNAME = "test_user"
PASSWORD = "test_password"

def fake_user():
    return Mock(
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

def fake_user_update_dto():
    return UpdateUserDTO(
        password="new_hashed_passw0rD!",
        email="new_email@example.com",
        phone_number="0987654321",
        photo="photo.png",
    )

def fake_user_view():
    return UserViewDTO(id=1, username="testuser")

class UserRouter_Should(unittest.TestCase):


    @patch('app.api.routes.users.service.create')
    def test_registerUser_IsSuccessful(self, create_mock):
        #Arrange
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

    @patch('app.api.auth_service.auth.authenticate_user')
    @patch('app.api.auth_service.auth.create_token')
    def test_login_success(self, mock_create_token, mock_authenticate_user):
        #Arrange
        mock_authenticate_user.return_value = True
        mock_create_token.return_value = ACCESS_TOKEN
        form_data = {
            "username": USERNAME,
            "password": PASSWORD
        }

        # Act
        response = client.post("/users/login", data=form_data)

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({
            "access_token": ACCESS_TOKEN,
            "token_type": "bearer"
        },response.json( ))
        mock_authenticate_user.assert_called_once()
        mock_create_token.assert_called_once( )


    @patch('app.api.auth_service.auth.authenticate_user')
    @patch('app.api.auth_service.auth.create_token')
    def test_login_success(self, mock_create_token, mock_authenticate_user):
        #Arrange
        mock_authenticate_user.return_value = True
        mock_create_token.return_value = ACCESS_TOKEN
        form_data = {
            "username": USERNAME,
            "password": PASSWORD
        }

        # Act
        response = client.post("/users/login", data=form_data)

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({
            "access_token": ACCESS_TOKEN,
            "token_type": "bearer"
        },response.json())
        mock_authenticate_user.assert_called_once()
        mock_create_token.assert_called_once()

    @patch('app.api.auth_service.auth.authenticate_user')
    def test_login_failWhenIncorrectCredentials(self, mock_authenticate_user):
        #Arrange
        mock_authenticate_user.return_value = None

        form_data = {
            "username": USERNAME,
            "password": PASSWORD
        }

        # Act
        response = client.post("/users/login", data=form_data)

        # Assert
        self.assertEqual(401, response.status_code)
        self.assertEqual({"detail": "Incorrect username or password"}, response.json())
        mock_authenticate_user.assert_called_once()

    @patch('app.api.auth_service.auth.get_token')
    @patch('app.api.auth_service.auth.blacklist_token')
    def test_logout_success(self, mock_blacklist_token, mock_get_token):
        #Arrange
        mock_get_token.return_value = ACCESS_TOKEN
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }

        # Act
        response = client.get("/users/logout", headers=headers)

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({"msg": "Successfully logged out"}, response.json())
        mock_blacklist_token.assert_called_once_with(ACCESS_TOKEN)

    @patch("app.api.routes.users.service.update_user")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_update_updatesTheCorrectProfileInfo(self, mock_get_user, mock_get_db, mock_update_user):
        # Arrange
        mock_get_user.return_value = fake_user_view()
        updated_user_dto = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()
        mock_update_user.return_value = fake_user()

        # Act
        response = update(fake_user_update_dto(), updated_user_dto, db)

        # Assert
        self.assertEqual(f"User testuser updated profile successfully.", response)
        mock_update_user.assert_called_once()



