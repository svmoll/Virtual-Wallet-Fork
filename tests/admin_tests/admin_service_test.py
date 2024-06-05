import unittest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from app.api.routes.admin.service import search_user, check_is_admin, status
from app.api.routes.users.schemas import UserFromSearchDTO
from app.core.models import User


def fake_user():
    return Mock(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            phone_number="1234567890",
            is_admin=False,
            is_restricted=False,
            is_blocked=False,

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

class AdminService_Should(unittest.TestCase):

    def test_searchUser_byUsername(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        db.query().filter_by().first.return_value = fake_user_dto1()

        # Act
        result = search_user(username="tester", db=db)

        # Assert
        self.assertIsInstance(result, UserFromSearchDTO)
        self.assertEqual("tester", result.username)
        self.assertEqual("email@example.com", result.email)

    def test_searchUser_usernameNotFoundRaisesHTTPException(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        db.query().filter_by().first.return_value = None

        # Assert
        with self.assertRaises(HTTPException):
            search_user(username="tester", db=db)

    def test_searchUser_byEmail(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.query( ).filter_by( ).first.return_value = fake_user_dto1( )

        # Act
        result = search_user(email="email@example.com", db=db)

        # Assert
        self.assertIsInstance(result, UserFromSearchDTO)
        self.assertEqual("tester", result.username)
        self.assertEqual("email@example.com", result.email)

    def test_searchUser_emailNotFoundRaisesHTTPException(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.query( ).filter_by( ).first.return_value = None

        # Assert
        with self.assertRaises(HTTPException):
            search_user(email="email@example.com", db=db)

    def test_searchUser_byPhoneNumber(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.query( ).filter_by( ).first.return_value = fake_user_dto1( )

        # Act
        result = search_user(phone_number="1234567890", db=db)

        # Assert
        self.assertIsInstance(result, UserFromSearchDTO)
        self.assertEqual("tester", result.username)
        self.assertEqual("email@example.com", result.email)

    def test_searchUser_phoneNumberNotFoundRaisesHTTPException(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.query( ).filter_by( ).first.return_value = None

        # Assert
        with self.assertRaises(HTTPException):
            search_user(phone_number="1234567890", db=db)

    def test_searchUser_pagination_withPageAndLimit(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        user_list = [fake_user_dto1( ), fake_user_dto2()]
        db.query( ).offset( ).limit( ).all.return_value = user_list

        # Act
        result = search_user(page=1, limit=2, db=db)
        result_list = list(result)

        # Assert
        self.assertEqual(len(result_list), 2)
        self.assertEqual(result_list[0].username, "tester")
        self.assertEqual(result_list[1].username, "tester2")

    def test_searchUser_pagination_withoutPageAndLimit(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        user_list = [fake_user_dto1( ), fake_user_dto2()]
        db.query( ).all.return_value = user_list

        # Act
        result = search_user(db=db)
        result_list = list(result)

        # Assert
        self.assertEqual(len(result_list), 2)
        self.assertEqual(result_list[0].username, "tester")
        self.assertEqual(result_list[1].username, "tester2")

    def test_searchUser_noCriteriaWithPageLimit(self):
        # Arrange
        db = fake_db()
        db.query = Mock( )
        db.offset = Mock()
        db.limit = Mock()
        db.all = Mock()
        db.filter = Mock()
        db.query.return_value = Mock()
        user_list = [fake_user_dto1(), fake_user_dto2()]
        db.query( ).offset( ).limit( ).all.return_value = user_list

        # Act
        result = search_user(page=1, limit=2, db=db)
        result_list = list(result)

        # Assert
        self.assertEqual(len(result_list), 2)
        self.assertEqual(result_list[0].username, "tester")
        self.assertEqual(result_list[1].username, "tester2")


    def test_checkIsAdmin_returnsTrueForAdmin(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        user = Mock(spec=User)
        user.is_admin = True
        db.query( ).filter( ).first.return_value = user


        # Act
        result = check_is_admin(1, db)

        # Assert
        self.assertTrue(result)


    def test_checkIsAdmin_returnsFalseForNonAdmin(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        user = Mock(spec=User)
        user.is_admin = False
        db.query( ).filter( ).first.return_value = user


        # Act
        result = check_is_admin(1, db)

        # Assert
        self.assertFalse(result)

    def tests_status_changesUserStatusToBlocked(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        user = fake_user()
        user.username = "testuser"
        user.is_blocked = 0
        db.query( ).filter_by( ).first.return_value = user


        # Act
        result = status("testuser", db)

        # Assert
        self.assertEqual("testuser is blocked", result)
        self.assertEqual(1, user.is_blocked)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(user)

    def tests_status_changesUserStatusToUnblocked(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        user = fake_user()
        user.username = "testuser"
        user.is_blocked = 1
        db.query( ).filter_by( ).first.return_value = user


        # Act
        result = status("testuser", db)

        # Assert
        self.assertEqual("testuser is unblocked", result)
        self.assertEqual(0, user.is_blocked)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(user)
    def tests_status_raisesHTTPExceptionWhenUserNotFound(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        db.query( ).filter_by( ).first.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            status("nonexistentuser", db)
        self.assertEqual(404, context.exception.status_code)
        self.assertEqual("User with that username was not found", context.exception.detail)