import unittest
from unittest.mock import patch, Mock
from app.core.models import Account, Withdrawal
from fastapi import HTTPException
from app.api.routes.accounts.service import (
    add_money_to_account,
    withdraw_money_from_account,
    get_account_by_username,
)


def fake_account():
    return Account(id=1, username="Grippen", balance=1234.56, is_blocked=0)


def fake_db():
    return Mock()


def fake_user():
    return Mock()


class AccountService_Should(unittest.TestCase):

    @patch("app.api.routes.accounts.service.get_account_by_username")
    def test_withdrawMoneyFromAccount_returnsCorrectBalance(self, mock_get_account):
        # Arrange
        username = "Grippen"
        withdrawal_amount = 100
        db = fake_db()
        account = fake_account()
        mock_get_account.return_value = account

        # Act
        result = withdraw_money_from_account(username, withdrawal_amount, db)

        # Assert
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(account)
        self.assertEqual(result, "1134.56")

    @patch("app.api.routes.accounts.service.get_account_by_username")
    def test_withdrawMoneyFromAccount_raises403WhenAccountBlocked(
        self, mock_get_account
    ):
        # Arrange
        username = "Grippen"
        withdrawal_amount = 111
        db = fake_db()
        account = fake_account()
        account.is_blocked = True
        mock_get_account.return_value = account

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            withdraw_money_from_account(username, withdrawal_amount, db)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(
            context.exception.detail,
            f"Account is blocked",
        )

    @patch("app.api.routes.accounts.service.get_account_by_username")
    def test_withdrawMoneyFromAccount_raises400WhenInsufficientFunds(
        self, mock_get_account
    ):
        # Arrange
        username = "Grippen"
        withdrawal_amount = 2000
        db = fake_db()
        mock_get_account.return_value = fake_account()

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            withdraw_money_from_account(username, withdrawal_amount, db)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            f"Insufficient funds",
        )

    @patch("app.api.routes.accounts.service.get_account_by_username")
    def test_withdrawMoneyFromAccount_raises400WhenAmountBelowOrZero(
        self, mock_get_account
    ):
        # Arrange
        username = "Grippen"
        withdrawal_amount = 0
        db = fake_db()
        mock_get_account.return_value = fake_account()

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            withdraw_money_from_account(username, withdrawal_amount, db)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            f"Amount must be more than 0.",
        )

    @patch("app.core.db_dependency.get_db")
    def test_getAccountByUsername_returnsAccountWhenExists(self, mock_get_db):
        # Arrange
        username = "test_username"
        db = fake_db()
        mock_get_db.return_value = db
        account = fake_account()
        db.query.return_value.filter.return_value.first.return_value = account

        # Act
        result = get_account_by_username(username, db)

        # Assert
        self.assertEqual(result, account)
        db.query.assert_called_once_with(Account)
        db.query.return_value.filter.assert_called_once()
        db.query.return_value.filter.return_value.first.assert_called_once()

    @patch("app.core.db_dependency.get_db")
    def test_getAccountByUsername_raises404WhenAccountIsNone(self, mock_get_db):
        # Arrange
        username = "test_username"
        db = fake_db()
        mock_get_db.return_value = db
        db.query.return_value.filter.return_value.first.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            get_account_by_username(username, db)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Account not found!")
        db.query.assert_called_once_with(Account)
        db.query.return_value.filter.assert_called_once()
        db.query.return_value.filter.return_value.first.assert_called_once()

    @patch("app.api.routes.accounts.service.get_account_by_username")
    def test_addMoneyToAccount_returnsUpdatedBalance(self, mock_get_account):
        # Arrange
        username = "Grippen"
        deposit_amount = 100
        db = fake_db()
        account = fake_account()
        mock_get_account.return_value = account

        # Act
        result = add_money_to_account(username, deposit_amount, db)

        # Assert
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(account)
        self.assertEqual(result, 1334.56)

    @patch("app.api.routes.accounts.service.get_account_by_username")
    def test_addMoneyToAccount_returns403WhenAccountBlocked(self, mock_get_account):
        # Arrange
        username = "Grippen"
        deposit = 100
        db = fake_db()
        db.commit
        account = fake_account()
        account.is_blocked = True
        mock_get_account.return_value = account

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            add_money_to_account(username, deposit, db)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Account is blocked")


if __name__ == "__main__":
    unittest.main()
