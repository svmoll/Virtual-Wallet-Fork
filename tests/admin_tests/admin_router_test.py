import json
import unittest
from datetime import datetime
from unittest.mock import patch, Mock, MagicMock

from fastapi import HTTPException, status
from sqlalchemy.orm import sessionmaker
from starlette.responses import JSONResponse

from app.api.routes.admin.router import search_users, change_status, view_transactions, deny_transaction, confirm_user
from app.api.routes.admin.schemas import TransactionViewDTO
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

def fake_transaction_dto():
    return TransactionViewDTO(
        id=1,
        sender="tester",
        receiver="tester2",
        amount=100,
        status="completed",
        is_flagged=False,
        type="transfer",
        transaction_date=datetime(2022, 1, 1)
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
        self.assertEqual("email@example.com", response[0].email)

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
        self.assertEqual("email@example.com", response[0].email)

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
        self.assertEqual("tester", response[0].username)
        self.assertEqual("tester2", response[1].username)

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
        self.assertEqual(403, context.exception.status_code)
        self.assertEqual("Forbidden", context.exception.detail)

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
        self.assertEqual(403, context.exception.status_code)
        self.assertEqual("Forbidden", context.exception.detail)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.view_transactions")
    def test_viewTransactions_withNoFilters(self, mock_view_transactions, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db()
        user = fake_user_view()
        transactions = [fake_transaction_dto()]
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_view_transactions.return_value = transactions

        # Act
        response = view_transactions(current_user=user, db=db)

        # Assert
        self.assertEqual(len(response), 1)
        self.assertEqual("tester", response[0].sender)
        self.assertEqual("tester2", response[0].receiver)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.view_transactions")
    def test_viewTransactions_withSenderFilter(self, mock_view_transactions, mock_get_user, mock_check_is_admin,
                                               mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        transactions = [fake_transaction_dto( )]
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_view_transactions.return_value = transactions

        # Act
        response = view_transactions(current_user=user, sender="tester", db=db)

        # Assert
        self.assertEqual(1, len(response))
        self.assertEqual("tester", response[0].sender)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.view_transactions")
    def test_viewTransactions_withReceiverFilter(self, mock_view_transactions, mock_get_user, mock_check_is_admin,
                                                 mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        transactions = [fake_transaction_dto( )]
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_view_transactions.return_value = transactions

        # Act
        response = view_transactions(current_user=user, receiver="tester2", db=db)

        # Assert
        self.assertEqual(1, len(response))
        self.assertEqual("tester2", response[0].receiver)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.view_transactions")
    def test_viewTransactions_withStatusFilter(self, mock_view_transactions, mock_get_user, mock_check_is_admin,
                                               mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        transactions = [fake_transaction_dto( )]
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_view_transactions.return_value = transactions

        # Act
        response = view_transactions(current_user=user, status="completed", db=db)

        # Assert
        self.assertEqual(1, len(response))
        self.assertEqual("completed", response[0].status)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.view_transactions")
    def test_viewTransactions_withPagination(self, mock_view_transactions, mock_get_user, mock_check_is_admin,
                                             mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        transactions = [fake_transaction_dto( ), fake_transaction_dto( )]
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_view_transactions.return_value = transactions

        # Act
        response = view_transactions(current_user=user, page=1, limit=2, db=db)

        # Assert
        self.assertEqual(2, len(response), )

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.view_transactions")
    def test_viewTransactions_withSort(self, mock_view_transactions, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        transactions = [fake_transaction_dto( )]
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_view_transactions.return_value = transactions

        # Act
        response = view_transactions(current_user=user, sort="amount_asc", db=db)

        # Assert
        self.assertEqual(1, len(response))
        self.assertEqual(100, response[0].amount)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_viewTransactions_nonAdminForbidden(self, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = False
        mock_get_db.return_value = db

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            view_transactions(current_user=user, db=db)
        self.assertEqual(403, context.exception.status_code)
        self.assertEqual("Forbidden", context.exception.detail)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.view_transactions")
    def test_viewTransactions_transactionsNotFound(self, mock_view_transactions, mock_get_user, mock_check_is_admin,
                                                   mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db
        mock_view_transactions.return_value = []

        # Act
        response = view_transactions(current_user=user, db=db)
        response_body = json.loads(response.body.decode("utf-8"))

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(404, response.status_code)
        self.assertEqual("Transactions not found", response_body["message"])

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.deny_transaction")
    def test_denyTransaction_success(self, mock_deny_transaction, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db

        # Act
        response = deny_transaction(current_user=user, transaction_id=1, db=db)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_deny_transaction.assert_called_once_with(1, db)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_denyTransaction_nonAdminForbidden(self, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db( )
        user = fake_user_view( )
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = False
        mock_get_db.return_value = db

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            deny_transaction(current_user=user, transaction_id=1, db=db)

        self.assertEqual(403, context.exception.status_code)
        self.assertEqual("Forbidden", context.exception.detail)
        mock_check_is_admin.assert_called_once_with(user.id, db)


    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.api.routes.admin.service.confirm_user")
    def test_confirmUser_success(self, mock_confirm_user, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db()
        user = fake_user_view()
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = True
        mock_get_db.return_value = db

        # Act
        response = confirm_user(current_user=user, user_id=1, db=db)
        response_body = json.loads(response.body.decode("utf-8"))

        # Assert
        self.assertEqual(200, response.status_code)
        self.assertEqual("Granted access to user", response_body)
        mock_confirm_user.assert_called_once_with(1, db)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.admin.service.check_is_admin")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_confirmUser_nonAdminForbidden(self, mock_get_user, mock_check_is_admin, mock_get_db):
        # Arrange
        db = fake_db()
        user = fake_user_view()
        mock_get_user.return_value = user
        mock_check_is_admin.return_value = False
        mock_get_db.return_value = db

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            confirm_user(current_user=user, user_id=1, db=db)

        self.assertEqual(403, context.exception.status_code)
        self.assertEqual("Forbidden", context.exception.detail)
        mock_check_is_admin.assert_called_once_with(user.id, db)