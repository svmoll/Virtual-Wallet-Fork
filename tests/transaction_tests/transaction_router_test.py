import asyncio
import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock, MagicMock, create_autospec
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth_service.auth import authenticate_user
from app.api.routes.users.schemas import UserDTO, UpdateUserDTO, UserViewDTO
from app.api.routes.transactions.schemas import TransactionDTO
from app.api.routes.transactions.router import create_draft_transaction


client = TestClient(app)


def fake_transaction():
    return Mock(
        id=2,
        sender_account="test_sender",
        receiver_account="test_receiver",
        amount=11.20,
        category_id=1,
        description="test_description",
        transaction_date=None,
        status="draft",
        is_reccurring=False,
        recurring_interval=None,
        is_flagged=False,
    )


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


def fake_user_view():
    return UserViewDTO(id=1, username="testuser")


class TransactionRouter_Should(unittest.TestCase):

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.service.create_draft_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_createDraftTransaction_IsSuccessful(
        self, get_user_mock, create_draft_transaction_mock, mock_get_db
    ):
        # Arrange
        get_user_mock.return_value = fake_user_view()
        create_draft_transaction_mock.return_value = fake_transaction()
        mock_get_db.return_value = fake_db()
        user = fake_user_view()
        transaction = fake_transaction_dto()
        db = fake_db()

        # Act
        response = create_draft_transaction(user.username, transaction, db)

        # Assert
        self.assertEqual(response, "You are about to send 11.20 to test_receiver")
