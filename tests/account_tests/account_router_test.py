import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
from app.core.models import Account
from fastapi import status
from app.api.routes.accounts.router import create_withdrawal

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

class AccountRouter_Should(unittest.TestCase):
    
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    def test_accountWithdrawal_returnsCorrectStatusCode_WhenSuccessful(
        self, 
        mock_get_user_or_raise_401_mock,
        mock_get_db):

        #Arrange
        withdrawal_amount = 1000
        account = fake_account()

        db = fake_db()
        mock_get_db.return_value = db

        mock_user = fake_user()
        mock_get_user_or_raise_401_mock = mock_user

        #Act
        result = create_withdrawal(withdrawal_amount,account, mock_get_user_or_raise_401_mock, mock_get_db)

        #Assert
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)




