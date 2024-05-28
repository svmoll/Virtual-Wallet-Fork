import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
from app.core.models import Account
from fastapi import status, HTTPException
from app.api.routes.accounts.service import withdrawal_request

def fake_account():
    return Account(
    id = 1,
    username = 'Grippen',
    balance = 1234.56,
    is_blocked = 0
    )

def fake_db():
    return MagicMock()

def fake_user():
    return 

class AccountService_Should(unittest.TestCase):

    # @patch('app.api.routes.accounts.service.withdrawal_request')
    @patch("app.core.db_dependency.get_db")
    def test_accountWithdrawal_raisesBadREquest_WhenAccountHasLessThanTheWithdrawalAmount(
        self, 
        mock_withdrawal_request,
        mock_get_db
        ):

        #Arrange
        withdrawal_amount = 9999.99
        account = fake_account()

        db = fake_db()
        mock_get_db.return_value = db

        # mock_withdrawal_request.side_effect = HTTPException(status_code=400, detail=f"Insufficient amount to withdraw {withdrawal_amount} leva")

        #Act
        try:
            withdrawal_request(withdrawal_amount, account, mock_get_db)
        except HTTPException as exc:
            result_status_code = exc.status_code
            result_detail = exc.detail

        #Assert
        self.assertEqual(result_status_code, 400)
        self.assertIn("Insufficient amount to withdraw", result_detail)


    @patch('app.api.routes.accounts.service.withdrawal_request')
    @patch("app.core.db_dependency.get_db")
    def test_accountWithdrawal_raisesBadRequest_WhenTheWithdrawalAmountIsNegative(
        self, 
        mock_withdrawal_request,
        mock_get_db
        ):

        #Arrange
        withdrawal_amount = 9999.99
        account = fake_account()

        db = fake_db()
        mock_get_db.return_value = db

        # mock_withdrawal_request.side_effect = HTTPException(status_code=400, detail=f"Insufficient amount to withdraw {withdrawal_amount} leva")

        #Act
        try:
            withdrawal_request(withdrawal_amount, account, mock_get_db)
        except HTTPException as exc:
            result_status_code = exc.status_code
            result_detail = exc.detail

        #Assert
        self.assertEqual(result_status_code, 400)
        self.assertIn("Insufficient amount to withdraw", result_detail)

    @patch('app.api.routes.accounts.router.create_withdrawal')
    def test_accountWithdrawal_isSuccessful():
        account = fake_account()
        amount = 1000

    # is not blocked
    # correct amount is withdrawn
    # is withdrawn


if __name__ == '__main__':
    unittest.main()