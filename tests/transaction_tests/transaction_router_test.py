import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock, Mock
from fastapi import status
from app.api.routes.users.schemas import UserViewDTO
from app.core.models import Transaction
from app.api.routes.transactions.schemas import TransactionDTO
from app.api.routes.transactions.router import (
    accept_transaction,
    confirm_transaction,
    decline_transaction,
    delete_draft_transaction,
    make_draft_transaction,
    edit_draft_transaction,
    cancel_recurring_transaction,
)
import json


def fake_transaction():
    return MagicMock()


def fake_pending_transaction():
    return MagicMock()


def fake_transaction_dto():
    return MagicMock()


Session = sessionmaker()


def fake_db():
    return MagicMock()


def fake_user_view():
    return MagicMock()


class TransactionRouter_Should(unittest.TestCase):

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.service.create_draft_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_makeDraftTransaction_returnsCorrectStatusCodeWhenSuccessful(
        self, mock_get_user, mock_create_draft_transaction, mock_get_db
    ):
        # Arrange
        transaction_dto = fake_transaction_dto()
        db = fake_db()
        user = fake_user_view()
        mock_get_user.return_value = user
        mock_get_db.return_value = db
        mock_created_draft_transaction = fake_transaction()
        mock_create_draft_transaction.return_value = mock_created_draft_transaction

        # Act
        response = make_draft_transaction(user, transaction_dto, db)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.router.update_draft_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_editDraftTransaction_returnsCorrectStatusCodeWhenSuccessful(
        self, mock_get_user, mock_update_draft_transaction, mock_get_db
    ):
        # Arrange
        user = fake_user_view()
        transaction_id = 2
        updated_transaction = fake_transaction_dto()
        db = fake_db()
        mock_get_user.return_value = user
        mock_get_db.return_value = db
        mock_updated_draft = fake_transaction()
        mock_update_draft_transaction.return_value = mock_updated_draft

        # Act
        response = edit_draft_transaction(user, transaction_id, updated_transaction, db)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.router.confirm_draft_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_confirmTransaction_returnsCorrectStatusCodeWhenSuccessful(
        self,
        mock_get_user,
        mock_confirm_draft_transaction,
        mock_get_db,
    ):
        # Arrange
        transaction_id = 2
        db = fake_db()
        user = fake_user_view()

        mock_get_user.return_value = user
        mock_get_db.return_value = db
        mock_confirm_draft_transaction.return_value = fake_pending_transaction()

        # Act
        response = confirm_transaction(user, transaction_id, db)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.service.delete_draft")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_deleteDraftTransaction_returnsCorrectStatusCodeWhenSuccessful(
        self, mock_get_user, mock_delete_draft, mock_get_db
    ):
        # Arrange
        transaction_id = 2
        db = fake_db()
        user = fake_user_view()
        mock_get_user.return_value = user
        mock_get_db.return_value = db
        mock_delete_draft.return_value = None

        # Act
        response = delete_draft_transaction(user, transaction_id, db)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.router.accept_incoming_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_acceptTransaction_returnsCorrectStatusCodeWhenSuccessful(
        self, mock_get_user, mock_accept_incoming_transaction, mock_get_db
    ):
        # Arrange
        transaction_id = 2
        db = fake_db()
        user = fake_user_view()
        mock_get_user.return_value = user
        mock_get_db.return_value = db
        mock_accept_incoming_transaction.return_value = 33.30

        # Act
        response = accept_transaction(user, transaction_id, db)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_content = {"message": "Your balance is 33.3."}
        response_content = json.loads(response.body.decode())
        self.assertEqual(response_content, expected_content)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.router.decline_incoming_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_declineTransaction_returnsCorrectStatusCodeWhenSuccessful(
        self, mock_get_user, mock_decline_incoming_transaction, mock_get_db
    ):
        # Arrange
        transaction_id = 2
        db = fake_db()
        user = fake_user_view()
        mock_get_user.return_value = user
        mock_get_db.return_value = db
        mock_decline_incoming_transaction.return_value = None

        # Act
        response = decline_transaction(user, transaction_id, db)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch("app.core.db_dependency.get_db")
    @patch("app.api.routes.transactions.router.cancelling_recurring_transaction")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    async def test_cancel_recurring_transaction_success(
        self, mock_get_user, mock_cancel_transaction, mock_get_db
    ):
        # Arrange
        recurring_transaction_id = 1
        current_user = MagicMock()
        db = MagicMock()
        scheduler = MagicMock()
        request = MagicMock()
        request.app.state.scheduler = scheduler
        mock_get_user.return_value = current_user
        mock_get_db.return_value = db

        # Act
        response = await cancel_recurring_transaction(
            request, recurring_transaction_id, current_user
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_cancel_transaction.assert_called_once_with(
            recurring_transaction_id, current_user.username, db, scheduler
        )
