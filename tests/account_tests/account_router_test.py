import unittest
from fastapi import status
from unittest.mock import patch, Mock
from app.core.models import Account
from app.api.routes.accounts.router import deposit_money, withdraw_money
from fastapi.responses import JSONResponse
import json


def fake_account():
    return Account(id=1, username="user", balance=1234.56, is_blocked=0)


def fake_db():
    return Mock()


def fake_user():
    return Mock()


class AccountRouter_Should(unittest.TestCase):

    @patch("app.api.routes.accounts.router.withdraw_money_from_account")
    def test_withdrawMoney_returnsCorrectStatusCodeAndMessageWithUpdatedBalance(
        self,
        mock_withdraw_money_from_account,
    ):

        # Arrange
        user = fake_user()
        db = fake_db()
        withdrawal_amount = 11.70
        mock_withdraw_money_from_account.return_value = "50.30"

        # Act
        response = withdraw_money(user, withdrawal_amount, db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_content = {"message": "Your current balance is 50.30"}
        response_content = json.loads(response.body.decode())
        self.assertEqual(response_content, expected_content)

    @patch("app.api.routes.accounts.router.add_money_to_account")
    def test_AddMoney_returnsCorrectStatusCodeAndMessageWithUpdatedBalance(
        self,
        mock_add_money_to_account,
    ):

        # Arrange
        user = fake_user()
        db = fake_db()
        withdrawal_amount = 11.70
        mock_add_money_to_account.return_value = "11.20"

        # Act
        response = deposit_money(user, withdrawal_amount, db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_content = {"message": "Your current balance is 11.20"}
        response_content = json.loads(response.body.decode())
        self.assertEqual(response_content, expected_content)
