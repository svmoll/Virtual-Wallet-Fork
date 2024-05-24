import unittest
from unittest.mock import patch, Mock, MagicMock

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException


from app.core.models import Transaction
from app.api.routes.transactions.schemas import TransactionDTO
from app.api.routes.transactions.service import create_draft_transaction


def fake_transaction_dto():
    return TransactionDTO(
        receiver_account="test_receiver",
        amount=11.30,
        category_id=1,
        description="test_description",
    )


Session = sessionmaker()


def fake_db():
    return MagicMock(spec=Session)


TEST_SENDER_ACCOUNT = "test_sender"


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
