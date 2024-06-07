import unittest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from app.api.routes.admin.service import search_user, check_is_admin, status, view_transactions, deny_transaction, \
    confirm_user
from app.api.routes.users.schemas import UserFromSearchDTO
from app.core.models import User, Transaction, Account


def fake_account():
    return Account(id=1, username="tester", balance=1234.56, is_blocked=1)
def fake_user():
    return Mock(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            phone_number="1234567890",
            is_admin=False,
            is_restricted=True,

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

def fake_transaction():
    return Mock(
    id = 1,
    sender_account = "tester",
    receiver_account = "tester2",
    amount = 100,
    status = "completed",
    is_flagged = False,
    type="transfer",
    transaction_date=datetime(2022, 1, 1))

def fake_transaction2():
    return Mock(
    id = 2,
    sender_account = "tester2",
    receiver_account = "tester3",
    amount = 200,
    status = "pending",
    is_flagged = False,
    type="transfer",
    transaction_date=datetime(2022, 1, 2))
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

    def test_searchUser_withPageAndLimit(self):
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

    def test_searchUser_withoutPageAndLimit(self):
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
        user = fake_user()
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
        user = fake_user()
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
        self.assertEqual("Account with that username was not found", context.exception.detail)


    def test_viewTransactions_withNoFilters(self):
        # Arrange
        db = fake_db()
        db.query = Mock()
        transactions = [fake_transaction()]
        db.query(Transaction).all.return_value = transactions

        # Act
        result = view_transactions(None, None, None, None,None, None, None, db)

        # Assert
        self.assertEqual(1, len(result))
        self.assertEqual("tester", result[0].sender, )
        self.assertEqual("tester2", result[0].receiver)

    def test_viewTransactions_withSenderFilter(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        user = fake_user()
        transactions = [fake_transaction( )]
        db.query(User).filter_by.return_value.first.return_value = user
        db.query(Transaction).filter.return_value.all.return_value = transactions

        # Act
        result = view_transactions(sender="tester", receiver=None, status=None, sort=None,flagged=None, page=None, limit=None, db=db)

        # Assert
        self.assertEqual(1, len(result))
        self.assertEqual("tester", result[0].sender)
        self.assertEqual("tester2", result[0].receiver)

    def test_viewTransactions_withReceiverFilter(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        user = fake_user()
        transactions = [fake_transaction( )]
        db.query(User).filter_by.return_value.first.return_value = user
        db.query(Transaction).filter.return_value.all.return_value = transactions

        # Act
        result = view_transactions(sender=None, receiver="tester2", status=None, sort=None,flagged=None, page=None, limit=None,
                                   db=db)

        # Assert
        self.assertEqual(1, len(result))
        self.assertEqual("tester", result[0].sender)
        self.assertEqual("tester2", result[0].receiver)

    def test_viewTransactions_withStatusFilter(self):
        # Arrange
        db = fake_db( )
        db.query = Mock()
        transactions = [fake_transaction()]
        db.query(Transaction).filter.return_value.all.return_value = transactions

        # Act
        result = view_transactions(sender=None, receiver=None, status="completed", sort=None,flagged=None, page=None, limit=None,
                                   db=db)

        # Assert
        self.assertEqual(1, len(result))
        self.assertEqual("completed", result[0].status)

    def test_viewTransactions_withPagination(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        transactions = [fake_transaction( ), fake_transaction2()]
        db.query(Transaction).offset.return_value.limit.return_value.all.return_value = transactions

        # Act
        result = view_transactions(sender=None, receiver=None, status=None, sort=None,flagged=None, page=1, limit=2, db=db)

        # Assert
        self.assertEqual(2, len(result))
        self.assertEqual("tester", result[0].sender)
        self.assertEqual("tester2", result[1].sender)

    def test_viewTransactions_withSort(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        transactions = [fake_transaction( ), fake_transaction2()]
        db.query(Transaction).order_by.return_value.all.return_value = transactions

        # Act
        result = view_transactions(sender=None, receiver=None, status=None, sort="amount_asc",flagged=None, page=None, limit=None,
                                   db=db)

        # Assert
        self.assertEqual(2, len(result))
        self.assertEqual(100, result[0].amount)
        self.assertEqual(200, result[1].amount)

    def test_viewTransactions_senderNotFound(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.query(User).filter_by.return_value.first.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            view_transactions(sender="nonexistent", receiver=None, status=None, sort=None,flagged=None, page=None, limit=None, db=db)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User with that username was not found")

    def test_viewTransactions_receiverNotFound(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.query(User).filter_by.return_value.first.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            view_transactions(sender=None, receiver="nonexistent", status=None, sort=None, flagged=None, page=None, limit=None, db=db)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User with that username was not found")



    def test_denyTransaction_success(self):
        # Arrange
        db = fake_db()
        db.query = Mock( )
        db.filter_by = Mock()
        db.commit = Mock()
        transaction = fake_transaction2()
        transaction.status = "pending"
        db.query().filter_by().first.return_value = transaction

        # Act
        deny_transaction(2, db)

        # Assert
        self.assertEqual("denied", transaction.status)
        db.commit.assert_called_once()

    def test_denyTransaction_transactionNotFound(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.filter_by = Mock( )
        db.commit = Mock( )
        db.query(Transaction).filter_by( ).first.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            deny_transaction(transaction_id=1, db=db)

        self.assertEqual(404, context.exception.status_code)
        self.assertEqual("Transaction with that id was not found", context.exception.detail)
        db.commit.assert_not_called()

    def test_denyTransaction_transactionNotPending(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.filter_by = Mock( )
        db.commit = Mock( )
        transaction = fake_transaction( )
        transaction.status = "completed"
        db.query(Transaction).filter_by( ).first.return_value = transaction

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            deny_transaction(transaction_id=1, db=db)

        self.assertEqual(400, context.exception.status_code)
        self.assertEqual("Cannot denied non pending transactions", context.exception.detail)
        db.commit.assert_not_called()

    @patch('app.api.routes.admin.service.confirmed_email_sender')
    def test_confirmUser_success(self, mock_email_sender):
        # Arrange
        mock_email_sender.return_value = True
        db = fake_db( )
        db.query = Mock( )
        db.commit = Mock( )
        user = fake_user( )
        account = fake_account( )
        db.query(User).filter_by( ).first.side_effect = [user, account]
        db.query(Account).filter_by( ).first.return_value = account

        # Act
        confirm_user(id=1, db=db)

        # Assert
        self.assertEqual(0, user.is_restricted)
        self.assertEqual(0, account.is_blocked)
        db.commit.assert_called_once( )
        mock_email_sender.assert_called_once_with(user)

    def test_confirmUser_userNotFound(self):
        # Arrange
        db = fake_db( )
        db.query = Mock( )
        db.commit = Mock( )
        db.query(User).filter_by( ).first.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            confirm_user(id=1, db=db)

        self.assertEqual(404, context.exception.status_code)
        self.assertEqual("User with that id was not found", context.exception.detail)
        db.commit.assert_not_called()