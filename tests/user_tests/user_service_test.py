import unittest
from unittest.mock import patch, Mock, MagicMock

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.core.models import User
from app.api.routes.users.schemas import UserDTO, UpdateUserDTO
from app.api.routes.users.service import create, update_user


def fake_user_dto():
    return Mock(
        username="tester",
        password="password",
        email="email@example.com",
        phone_number="1234567890",
        photo_path="photo.png",
        is_admin=False,
        is_restricted=False
    )

def fake_user_update_dto():
    return Mock(
        password="new_hashed_password",
        email="new_email@example.com",
        phone_number="0987654321",
        photo="photo.png",
    )

Session = sessionmaker()
def fake_db():
    return MagicMock(spec=Session)

class UsrServices_Should(unittest.TestCase):

    @patch('app.api.routes.users.service.hash_pass')
    def test_create_returnsCorrectUserWhenInoIsCorrect(self, hash_pass_mock):
        #Arrange
        hash_pass_mock.return_value = "hashed_password"
        user = fake_user_dto()
        db = fake_db()
        db.add_all = Mock()
        db.commit = Mock()
        db.refresh = Mock()

        #Act
        result = create(user, db)

        #Assert
        db.add_all.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, "tester")
        self.assertEqual(result.password, "hashed_password")
        self.assertEqual(result.email, "email@example.com")
        self.assertEqual(result.phone_number, "1234567890")

# TODO check deep equality
    @patch('app.api.routes.users.service.hash_pass')
    def test_create_returnsCorrectErrorWhenUsernameExists(self, hash_pass_mock):
        #Arrange
        hash_pass_mock.return_value = "hashed_password"
        user_dto = fake_user_dto()
        db = fake_db()
        db.add_all = Mock()
        db.commit = Mock(side_effect=IntegrityError(Mock(), Mock(), "Duplicate entry 'tester' for key 'username'"))
        db.rollback = Mock()

        #Assert
        with self.assertRaises(HTTPException) as context:
            create(user_dto, db)
        db.rollback.assert_called_once( )
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Username already exists")

    @patch('app.api.routes.users.service.hash_pass')
    def test_create_returnsCorrectErrorWhenPhoneNumberExists(self, hash_pass_mock):
        # Arrange
        hash_pass_mock.return_value = "hashed_password"
        user_dto = fake_user_dto( )
        db = fake_db()
        db.add_all = Mock( )
        db.commit = Mock(
            side_effect=IntegrityError(Mock(), Mock(), "Duplicate entry '1234567890' for key 'phone_number'"))
        db.rollback = Mock()

        #Assert
        with self.assertRaises(HTTPException) as context:
            create(user_dto, db)
        db.rollback.assert_called_once( )
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Phone number already exists")

    @patch('app.api.routes.users.service.hash_pass')
    def test_create_returnsCorrectErrorWhenEmailExists(self, hash_pass_mock):
        # Arrange
        hash_pass_mock.return_value = "hashed_password"
        user_dto = fake_user_dto( )
        db = fake_db()
        db.add_all = Mock( )
        db.commit = Mock(
            side_effect=IntegrityError(Mock( ), Mock( ), "Duplicate entry 'email@example.com' for key 'email'"))
        db.rollback = Mock( )

        #Assert
        with self.assertRaises(HTTPException) as context:
            create(user_dto, db)
        db.rollback.assert_called_once( )
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Email already exists")

    @patch('app.api.routes.users.service.hash_pass')
    def test_create_returnsCorrectErrorWhenInvalidDataIsPutSomehow(self, hash_pass_mock):
        # Arrange
        hash_pass_mock.return_value = "hashed_password"
        user_dto = fake_user_dto( )
        db = fake_db()
        db.add_all = Mock( )
        db.commit = Mock(side_effect=IntegrityError(Mock( ), Mock( ), "Some other integrity error"))
        db.rollback = Mock( )

        #Assert
        with self.assertRaises(HTTPException) as context:
            create(user_dto, db)
        db.rollback.assert_called_once( )
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Could not complete registration")

    @patch('app.api.routes.users.service.hash_pass')
    def test_updateUser_updatesCorrectly(self, hash_pass_mock):
        # Arrange
        hash_pass_mock.return_value = "new_hashed_password"
        db = fake_db()
        db.query = Mock()
        db.commit = Mock()
        db.refresh = Mock( )
        user = fake_user_dto()
        db.query().filter_by().first.return_value = user
        update_info = fake_user_update_dto()

        # Act
        result = update_user(1, update_info, db)

        # Assert
        db.commit.assert_called_once( )
        db.refresh.assert_called_once( )
        self.assertEqual("new_hashed_password", result.password)
        self.assertEqual("new_email@example.com",result.email)
        self.assertEqual("0987654321", result.phone_number)
        self.assertEqual("photo.png", result.photo_path)

    def test_updateUser_returns404WhenUserNotFound(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        db.query().filter_by().first.return_value = None
        update_info = fake_user_update_dto()

        # Assert
        with self.assertRaises(HTTPException) as context:
            update_user(1, update_info, db)
        self.assertEqual(404, context.exception.status_code)
        self.assertEqual("User not found", context.exception.detail)

    @patch('app.api.routes.users.service.hash_pass')
    def test_updateUser_returnsCorrectErrorWhenUsernameExists(self, hash_pass_mock):
        # Arrange
        hash_pass_mock.return_value = "new_hashed_password"
        db = fake_db( )
        db.query = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        user = fake_user_dto()
        db.query( ).filter_by( ).first.return_value = user
        update_info = fake_user_update_dto()
        db.commit.side_effect = IntegrityError(Mock( ), Mock( ), "Duplicate entry 'new_tester' for key 'username'")

        # Assert
        with self.assertRaises(HTTPException) as context:
            update_user(1, update_info, db)
        db.rollback.assert_called_once( )
        self.assertEqual(400, context.exception.status_code)
        self.assertEqual("Username already exists", context.exception.detail)

    @patch('app.api.routes.users.service.hash_pass')
    def test_updateUser_returnsCorrectErrorWhenPhoneNumberExists(self, hash_pass_mock):
        # Arrange
        hash_pass_mock.return_value = "new_hashed_password"
        db = fake_db()
        db.query = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        user = fake_user_dto()
        db.query( ).filter_by( ).first.return_value = user
        update_info = fake_user_update_dto()
        db.commit.side_effect = IntegrityError(Mock( ), Mock( ), "Duplicate entry '0987654321' for key 'phone_number'")

        # Assert
        with self.assertRaises(HTTPException) as context:
            update_user(1, update_info, db)
        db.rollback.assert_called_once( )
        self.assertEqual(400, context.exception.status_code)
        self.assertEqual("Phone number already exists", context.exception.detail)

    @patch('app.api.routes.users.service.hash_pass')
    def test_updateUser_returnsCorrectErrorWhenEmailExists(self, hash_pass_mock):
        # Arrange
        hash_pass_mock.return_value = "new_hashed_password"
        db = fake_db()
        db.query = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        user = fake_user_dto()
        db.query().filter_by( ).first.return_value = user
        update_info = fake_user_update_dto()
        db.commit.side_effect = IntegrityError(Mock(), Mock(),
                                               "Duplicate entry 'new_email@example.com' for key 'email'")

        # Assert
        with self.assertRaises(HTTPException) as context:
            update_user(1, update_info, db)
        db.rollback.assert_called_once()
        self.assertEqual(400, context.exception.status_code)
        self.assertEqual("Email already exists", context.exception.detail)

