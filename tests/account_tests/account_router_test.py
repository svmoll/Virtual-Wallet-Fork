import unittest
from unittest.mock import patch, Mock
from app.core.models import Account
from app.api.routes.accounts.router import create_withdrawal
from fastapi.responses import JSONResponse
import json


def fake_account():
    return Account(id=1, username="user", balance=1234.56, is_blocked=0)


def fake_db():
    return Mock()


def fake_user():
    return Mock()


class AccountRouter_Should(unittest.TestCase):

    @patch("app.api.routes.accounts.service.get_account_by_id")
    def test_accountWithdrawal_returnsCorrectStatusCode_WhenSuccessful(
        self,
        mock_get_account_by_id,
    ):

        # Arrange
        mock_get_db = fake_db()
        mock_current_user = fake_user()

        mock_account = fake_account()
        mock_account.balance = 100.00
        mock_account.is_blocked = False
        mock_get_account_by_id.return_value = mock_account

        withdrawal_amount = 10.00

        # Act
        response = create_withdrawal(mock_current_user, mock_get_db, withdrawal_amount)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 201)

        response_body = response.body.decode("utf-8")
        response_body_dict = json.loads(response_body)
        self.assertEqual(
            response_body_dict,
            {
                "message": f"The withdrawal of {withdrawal_amount} leva has been being processed."
            },
        )
