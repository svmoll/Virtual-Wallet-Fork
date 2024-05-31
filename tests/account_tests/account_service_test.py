import unittest
from unittest.mock import patch, Mock
from app.core.models import Account

# from app.api.routes.accounts.schemas import AccountViewDTO
from fastapi import HTTPException
from app.api.routes.accounts.service import withdrawal_request, get_account_by_username


def fake_account():
    return Account(id=1, username="Grippen", balance=1234.56, is_blocked=0)


# def fake_accountdto():
#     return AccountViewDTO(id=1, username="Grippen", balance=1234.56, is_blocked=False)


def fake_db():
    return Mock()


def fake_user():
    return Mock()


class AccountService_Should(unittest.TestCase):

    @patch("app.api.routes.accounts.service.get_account_by_id")
    def test_accountWithdrawal_raisesBadREquest_WhenAccountHasLessThanTheWithdrawalAmount(
        self, mock_get_account_by_id
    ):

        # Arrange
        mock_get_db = fake_db()
        mock_current_user = fake_user()

        mock_account = fake_account()
        mock_account.balance = 50.00  # Mock account balance
        mock_get_account_by_id.return_value = mock_account

        withdrawal_amount = 100

        # Act
        with self.assertRaises(HTTPException) as context:
            withdrawal_request(withdrawal_amount, mock_current_user, mock_get_db)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            f"Insufficient amount to withdraw {withdrawal_amount} leva.",
        )

    @patch("app.api.routes.accounts.service.get_account_by_id")
    def test_accountWithdrawal_raisesBadRequest_WhenTheAccountIsBlocked(
        self, mock_get_account_by_id
    ):

        # Arrange
        mock_get_db = fake_db()
        mock_current_user = fake_user()

        mock_account = fake_account()
        mock_account.balance = 100.00
        mock_account.is_blocked = True
        mock_get_account_by_id.return_value = mock_account

        withdrawal_amount = 50.00

        # Act
        with self.assertRaises(HTTPException) as context:
            withdrawal_request(withdrawal_amount, mock_current_user, mock_get_db)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail, f"Account is blocked. Contact Customer Support."
        )

    @patch("app.api.routes.accounts.service.get_account_by_id")
    def test_accountWithdrtest_accountWithdrawal_raisesBadRequest_WhenTheWithdrawalAmountIsNegative(
        self, mock_get_account_by_id
    ):

        # Arrange
        mock_get_db = fake_db()
        mock_current_user = fake_user()

        mock_account = fake_account()
        mock_get_account_by_id.return_value = mock_account

        withdrawal_amount = -50.00

        # Act
        with self.assertRaises(HTTPException) as context:
            withdrawal_request(withdrawal_amount, mock_current_user, mock_get_db)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail, f"Withdrawals should be a positive number."
        )

    # Fix below
    @patch("app.api.routes.accounts.service.get_account_by_id")
    def test_accountWithdrawal_returnCorrectBalance_WhenTheWithdrawalIsSuccessful(
        self, mock_get_account_by_id
    ):

        # Arrange
        withdrawal_amount = 50
        mock_get_db = fake_db()

        mock_account = fake_account()
        mock_account.balance = 100
        mock_get_account_by_id.return_value = mock_account

        expected_balance = mock_account.balance - withdrawal_amount

        # Act
        result = withdrawal_request(withdrawal_amount, mock_account, mock_get_db)
        actual_account_balance = result.balance

        # Assert
        self.assertEqual(actual_account_balance, expected_balance)

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


if __name__ == "__main__":
    unittest.main()
