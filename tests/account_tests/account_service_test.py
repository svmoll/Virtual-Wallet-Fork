import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock, Mock
from app.core.models import Account
from fastapi import HTTPException
from app.api.routes.accounts.service import withdrawal_request

def fake_account():
    return Account(
    id = 1,
    username = 'Grippen',
    balance = 1234.56,
    is_blocked = 0
    )

def fake_accountdto():
    return Account(
    id = 1,
    username = 'Grippen',
    balance = 1234.56,
    is_blocked = False
    )

def fake_db():
    return MagicMock()

def fake_user():
    return 

class AccountService_Should(unittest.TestCase):

    @patch("app.api.routes.accounts.service.get_account_by_id") 
    @patch("app.core.db_dependency.get_db")
    def test_accountWithdrawal_raisesBadREquest_WhenAccountHasLessThanTheWithdrawalAmount(
        self,
        mock_get_account_by_id,
        mock_get_db
        ):

        #Arrange
        withdrawal_amount = 9999.99
        mock_account = fake_accountdto()

        mock_get_account_by_id = Mock()
        mock_get_account_by_id.return_value = mock_account

        mock_get_db.return_value = fake_db()

        #Act
        try:
            withdrawal_request(withdrawal_amount, mock_account, mock_get_db)
        except HTTPException as exc:
            result_status_code = exc.status_code
            result_detail = exc.detail

        #Assert
        self.assertEqual(result_status_code, 400)
        self.assertEqual("Insufficient amount to withdraw", result_detail)


    @patch("app.core.db_dependency.get_db")
    def test_accountWithdrawal_raisesBadRequest_WhenTheWithdrawalAmountIsNegative(
        self, 
        mock_get_db
        ):

        #Arrange
        withdrawal_amount = -5
        account = fake_account()

        db = fake_db()
        mock_get_db.return_value = db

        #Act
        try:
            withdrawal_request(withdrawal_amount, account, mock_get_db)
        except HTTPException as exc:
            result_status_code = exc.status_code
            result_detail = exc.detail

        #Assert
        self.assertEqual(result_status_code, 400)
        self.assertIn("Withdrawals should be written as a positive number.", result_detail)

    @patch("app.core.db_dependency.get_db")
    def test_accountWithdrawal_returnCorrectBalance_WhenTheWithdrawalIsSuccessful(
        self, 
        mock_get_db
        ):

        #Arrange
        withdrawal_amount = 1233.56
        mock_account = fake_account()
        expected_balance = mock_account.balance - withdrawal_amount

        mock_db_session = fake_db()
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter().first.return_value = mock_account
        mock_get_db.return_value = mock_db_session

        # Act
        withdrawal_request(withdrawal_amount, mock_account, mock_get_db)

        # Assert
        actual_account_balance = mock_account.balance
        self.assertEqual(actual_account_balance, expected_balance)

    @patch("app.core.db_dependency.get_db")
    def test_accountWithdrawal_raisesBadRequest_WhenTheAccountIsBlocked(
        self, 
        mock_get_db
        ):

        #Arrange
        withdrawal_amount = 10
        mock_account = fake_account()
        mock_account.is_blocked = True

        mock_get_db.return_value = fake_db()

        #Act
        try:
            withdrawal_request(withdrawal_amount, mock_account, mock_get_db)
        except HTTPException as exc:
            result_status_code = exc.status_code
            result_detail = exc.detail

        #Assert
        self.assertEqual(result_status_code, 400)
        self.assertIn("Account is blocked. Contact Customer Support.", result_detail)


if __name__ == '__main__':
    unittest.main()