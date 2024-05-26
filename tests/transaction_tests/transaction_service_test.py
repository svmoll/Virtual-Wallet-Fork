import unittest
from unittest.mock import patch, Mock, MagicMock

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.core.models import Transaction
from app.api.routes.transactions.schemas import TransactionDTO
from app.api.routes.transactions.service import (
    create_draft_transaction,
    update_draft_transaction,
    get_transaction_by_id,
)


def fake_transaction_dto():
    return TransactionDTO(
        receiver_account="test_receiver",
        amount=11.30,
        category_id=1,
        description="test_description",
    )


def fake_updated_dto():
    return TransactionDTO(
        receiver_account="updated_receiver",
        amount=101.40,
        category_id=2,
        description="updated_description",
    )


def fake_transaction_draft():
    transaction = Transaction(
        sender_account=TEST_SENDER_ACCOUNT,
        receiver_account="test_receiver",
        amount=11.30,
        category_id=1,
        description="test_description",
        status="draft",
        is_recurring=False,
        is_flagged=False,
    )
    transaction.id = 1
    return transaction


Session = sessionmaker()


def fake_db():
    session_mock = MagicMock(spec=Session)
    session_mock.query = MagicMock()
    session_mock.query.filer = MagicMock()
    return session_mock


TEST_SENDER_ACCOUNT = "test_sender"
WRONG_SENDER_ACCOUNT = "wrong_sender"


class TransactionsServiceShould(unittest.TestCase):

    def test_createDraftTransaction_returnsTransactionWhenInputCorrect(self):
        # Arrange
        transaction = fake_transaction_dto()
        sender_account = TEST_SENDER_ACCOUNT
        db = fake_db()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()

        # Act
        result = create_draft_transaction(sender_account, transaction, db)

        # Assert
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        self.assertIsInstance(result, Transaction)
        self.assertEqual(result.sender_account, "test_sender")
        self.assertEqual(result.receiver_account, "test_receiver")
        self.assertEqual(result.amount, 11.30)
        self.assertEqual(result.category_id, 1)
        self.assertEqual(result.description, "test_description")
        self.assertEqual(result.transaction_date, None)
        self.assertEqual(result.status, "draft")
        self.assertEqual(result.is_recurring, False)
        self.assertEqual(result.is_flagged, False)

    def test_createDraftTransaction_raisesHTTPExceptionForNonExistentReceiver(self):
        # Arrange
        transaction = fake_transaction_dto()
        sender_account = TEST_SENDER_ACCOUNT
        db = fake_db()
        db.add = Mock()
        db.commit = Mock(side_effect=IntegrityError(Mock(), Mock(), "receiver_account"))
        db.rollback = Mock()

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            create_draft_transaction(sender_account, transaction, db)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Receiver doesn't exist!")

    def test_createDraftTransaction_raisesHTTPExceptionWhenCategoryIDDoesNotExist(self):
        # Arrange
        transaction = fake_transaction_dto()
        sender_account = TEST_SENDER_ACCOUNT
        db = fake_db()
        db.add = Mock()
        db.commit = Mock(side_effect=IntegrityError(Mock(), Mock(), "category_id"))
        db.rollback = Mock()

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            create_draft_transaction(sender_account, transaction, db)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Category doesn't exist!")
        db.rollback.assert_called_once()

    @patch("app.api.routes.transactions.service.get_transaction_by_id")
    def test_updateDraftTransaction_returnsUpdatedTransactionWhenInputCorrect(
        self, get_transaction_mock
    ):
        # Arrange
        transaction_id = 1
        sender_account = TEST_SENDER_ACCOUNT
        updated_transaction = fake_updated_dto()
        db = fake_db()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        get_transaction_mock.return_value = fake_transaction_draft()

        # Act
        result = update_draft_transaction(
            sender_account, transaction_id, updated_transaction, db
        )

        # Assert
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        self.assertEqual(result.amount, 101.40)
        self.assertEqual(result.receiver_account, "updated_receiver")
        self.assertEqual(result.category_id, 2)
        self.assertEqual(result.description, "updated_description")

    def test_getTransactionByID_returnsTransactionWhenExists(self):
        # Arrange
        transaction_id = 1
        db = fake_db()
        transaction = fake_transaction_draft()
        db.query().filter().first.return_value = transaction

        # Act
        result = get_transaction_by_id(transaction_id, db)

        # Assert
        self.assertEqual(result, transaction)

    def test_getTransactionByID_returnsNoneWhenTransactionDoesNotExist(self):
        # Arrange
        transaction_id = 1
        db = fake_db()
        db.query().filter().first.return_value = None

        # Act
        result = get_transaction_by_id(transaction_id, db)

        # Assert
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
