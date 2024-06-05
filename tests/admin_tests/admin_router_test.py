import json
import unittest
from unittest.mock import patch, Mock, MagicMock

from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from app.api.routes.admin.router import search_users, change_status
from app.api.routes.users.schemas import UserViewDTO


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

def fake_user_dto1():
    return Mock(
        username="tester",
        password="password",
        email="email@example.com",
        phone_number="1234567890",
        fullname="Test User",
        photo_path="photo.png",
        is_admin=False,
        is_restricted=False,
    )

def fake_user_dto2():
    return Mock(
        username="tester2",
        password="password",
        email="email2@example.com",
        phone_number="1234567890",
        fullname="Test User",
        photo_path="photo.png",
        is_admin=False,
        is_restricted=False,
    )

def fake_user_view():
    return UserViewDTO(id=1, username="testuser")
class AdminRouter_Should(unittest.TestCase):
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.search_user")
    def test_searchUsers_byUsername(self, mock_search_user, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db()
        user = fake_user_view()
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_search_user.return_value = [fake_user_dto1()]

        # Act
        response =  search_users(user)

        # Assert
        self.assertEqual("tester", response[0].username)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.search_user")
    def test_search_users_by_email(self, mock_search_user, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = Mock( )
        user = fake_user_view( )
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_search_user.return_value = [fake_user_dto1( )]

        # Act
        response = search_users(current_user=user, email="email@example.com", db=db)

        # Assert
        self.assertEqual(response[0].email, "email@example.com")

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.search_user")
    def test_search_users_by_phone_number(self, mock_search_user, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = Mock( )
        user = fake_user_view( )
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_search_user.return_value = [fake_user_dto1( )]

        # Act
        response = search_users(current_user=user, phone_number="1234567890", db=db)

        # Assert
        self.assertEqual(response[0].email, "email@example.com")

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.search_user")
    def test_search_users_with_pagination(self, mock_search_user, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = Mock( )
        user = fake_user_view( )
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_search_user.return_value = [fake_user_dto1( ), fake_user_dto2( )]

        # Act
        response = search_users(current_user=user, page=1, limit=2, db=db)

        # Assert
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0].username, "tester")
        self.assertEqual(response[1].username, "tester2")

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_search_users_non_admin_forbidden(self, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = Mock( )
        user = fake_user_view( )
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = False
        mock_get_db.return_value = db

        # Act
        with self.assertRaises(HTTPException) as context:
            search_users(current_user=user, db=db)

        # Assert
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Forbidden")

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.status")
    def test_changeStatus_admin(self, mock_status, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db()
        current_user = fake_user_view( )
        target_username = "testuser"
        mock_get_user.return_value = current_user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_status.return_value = "testuser is blocked"

        # Act
        response = change_status(current_user, target_username, db)
        response_body = json.loads(response.body.decode("utf-8"))

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual({"action": "testuser is blocked"}, response_body)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_changeStatus_userNotAdmin(self, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db()
        current_user = fake_user_view()
        target_username = "testuser"
        mock_get_user.return_value = current_user
        mock_check_is_admin.return_value = False
        mock_get_db.return_value = db


        # Assert
        with self.assertRaises(HTTPException) as context:
            change_status(current_user, target_username, db)
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Forbidden")