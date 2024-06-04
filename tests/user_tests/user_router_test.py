import asyncio
import json
import unittest

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock, MagicMock, create_autospec
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth_service.auth import authenticate_user
from app.api.routes.users.router import register_user, login, update, search, add_contact, delete_contact, view_contacts
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

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.search_user")
    def test_search_byUsername(self, mock_search_user, mock_get_db, mock_get_user):
        # Arrange
        mock_search_user.return_value = fake_user()
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()

        # Act
        response = search(fake_user_view(), "testuser", db)
        response_body = json.loads(response.body.decode("utf-8"))

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({"username": "testuser", "email": "test@example.com"}, response_body)
        mock_search_user.assert_called_once()

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.search_user")
    def test_search_byEmail(self, mock_search_user, mock_get_db, mock_get_user):
        # Arrange
        mock_search_user.return_value = fake_user()
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()

        # Act
        response = search(fake_user_view(), None, "test@example.com", db)
        response_body = json.loads(response.body.decode("utf-8"))

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({"username": "testuser", "email": "test@example.com"}, response_body)
        mock_search_user.assert_called_once()

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.search_user")
    def test_search_byPhoneNumber(self, mock_search_user, mock_get_db, mock_get_user):
        # Arrange
        mock_search_user.return_value = fake_user()
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()

        # Act
        response = search(fake_user_view(), None, None,"1234567890", db)
        response_body = json.loads(response.body.decode("utf-8"))

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({"username": "testuser", "email": "test@example.com"}, response_body)
        mock_search_user.assert_called_once()

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.search_user")
    def test_search_raisesBadRequestWhenNoQueryParamsAreAdded(self, mock_search_user, mock_get_db, mock_get_user):
        # Arrange
        mock_search_user.return_value = fake_user()
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()

        # Assert
        with self.assertRaises(HTTPException) as context:
            search(fake_user_view( ), None, None, None, db)

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.create_contact")
    def test_create_successfulAndReturnsCorrectStatusCode(self, mock_create_contact, mock_get_db, mock_get_user):
        # Arrange
        mock_create_contact.return_value = fake_user()
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()

        # Act
        response = add_contact(fake_user_view(), "tester", db)
        response_body = json.loads(response.body.decode("utf-8"))

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({"detail": "Successfully added new contact"}, response_body)
        mock_create_contact.assert_called_once()

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.create_contact")
    def test_create_raisesBadRequestWhenBodyIsEmpty(self, mock_create_contact, mock_get_db, mock_get_user):
        # Arrange
        mock_create_contact.return_value = fake_user()
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()

        # Assert
        with self.assertRaises(HTTPException) as context:
            add_contact(fake_user_view( ), None, db)

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.delete_contact")
    def test_deleteContact_successfullyRemovesTheContact(self, mock_delete, mock_get_db, mock_get_user):
        # Arrange
        mock_delete.return_value = True
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()

        # Act
        response = delete_contact(fake_user_view(), "tester", db)


        # Assert
        self.assertEqual(204, response.status_code)

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    def test_deleteContact_returnsCorrectStatusCodeWhenSuccessful(self,mock_get_db, mock_get_user):
        # Arrange
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()


        # Assert
        with self.assertRaises(HTTPException) as context:
            delete_contact(fake_user_view( ), None, db)

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.view")
    def test_viewContacts_returnsMessageWhenNoContacts(self, mock_view, mock_get_db, mock_get_user):
        # Arrange
        mock_get_user.return_value = fake_user_view( )
        mock_get_db.return_value = fake_db( )
        db = fake_db( )
        mock_view.return_value = []

        # Act
        response = view_contacts(fake_user_view(), db=db)
        response_body = json.loads(response.body.decode("utf-8"))

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({"detail": "No contacts found"}, response_body)
        mock_view.assert_called_once()

    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.users.service.view")
    def test_viewContacts_returnsMessageWhenNoContacts(self, mock_view, mock_get_db, mock_get_user):
        # Arrange
        mock_get_user.return_value = fake_user_view( )
        mock_get_db.return_value = fake_db( )
        db = fake_db( )
        mock_view.return_value = ["contact1", "contact2"]

        # Act
        response = view_contacts(fake_user_view(), db=db)

        # Assert
        self.assertEqual(["contact1", "contact2"], response)
        mock_view.assert_called_once()