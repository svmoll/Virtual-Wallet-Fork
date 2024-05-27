import asyncio
import unittest
from urllib import response
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock, MagicMock, create_autospec
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth_service.auth import authenticate_user
from app.api.routes.users.schemas import UserDTO, UpdateUserDTO, UserViewDTO
from app.core.models import Transaction
from app.api.routes.transactions.schemas import TransactionDTO
from app.api.routes.transactions.router import (
    confirm_transaction,
    make_draft_transaction,
)


client = TestClient(app)


def fake_transaction():
    transaction = Transaction(
        sender_account="test_sender",
        receiver_account="test_receiver",
        amount=11.20,
        category_id=1,
        description="test_description",
        transaction_date=None,
        status="draft",
        is_recurring=False,
        recurring_interval=None,
        is_flagged=False,
    )
    transaction.id = 2
    return transaction


def fake_pending_transaction():
    transaction = Transaction(
        sender_account="test_sender",
        receiver_account="receiver_test",
        amount=11.20,
        category_id=1,
        description="test_description",
        transaction_date=None,
        status="pending",
        is_recurring=False,
        recurring_interval=None,
        is_flagged=False,
    )
    transaction.id = 2
    return transaction


def fake_transaction_dto():
    return TransactionDTO(
        receiver_account="test_receiver",
        amount=11.30,
        category_id=1,
        description="test_description",
    )


Session = sessionmaker()


def fake_db():
    return MagicMock()


def fake_user_view():
    return UserViewDTO(id=1, username="testuser")


class TransactionRouter_Should(unittest.TestCase):

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.service.create_draft_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_makeDraftTransaction_IsSuccessful(
        self, mock_get_db, create_draft_transaction_mock, get_user_mock
    ):
        # Arrange
        get_user_mock.return_value = fake_user_view()
        transaction_dto = fake_transaction_dto()
        mock_get_db.return_value = fake_db()
        db = fake_db()
        create_draft_transaction_mock.return_value = fake_transaction()
        user = fake_user_view()

        # Act
        response = make_draft_transaction(user, transaction_dto, db)

        # Assert
        self.assertEqual(
            response, "You are about to send 11.20 to test_receiver [Draft ID: 2]"
        )

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.service.create_draft_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_confirmTransaction_returnsCorrectMessage(
        self, mock_get_db, mock_confirm_draft_transaction, mock_get_user
    ):

        # Arrange
        mock_get_user.return_value = fake_user_view()
        mock_get_db.return_value = fake_db()
        db = fake_db()
        mock_confirm_draft_transaction.return_value = fake_pending_transaction()
        user = fake_user_view()
        transaction = fake_pending_transaction()
        transaction_id = 2

        # Act
        response = confirm_transaction(user, transaction_id, db)

        # Assert
        self.assertEqual(response, "Your transfer to receiver_test is pending!")
