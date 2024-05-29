import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock, Mock
from app.core.models import Account
from fastapi import status
from app.api.routes.accounts.router import create_withdrawal

def fake_account():
    return Account(
    id = 1,
    username = 'user',
    balance = 1234.56,
    is_blocked = 0
    )

def fake_db():
    return MagicMock()

def fake_user():
    return 

class AccountRouter_Should(unittest.TestCase):
    
    @patch("app.api.routes.accounts.service.withdrawal_request")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    @patch("app.core.db_dependency.get_db")
    def test_accountWithdrawal_returnsCorrectStatusCode_WhenSuccessful(
        self,
        mock_withdrawal_request, 
        mock_get_user_or_raise_401_mock,
        mock_get_db):

        #Arrange
        withdrawal_amount = 1000
        
        mock_withdrawal_request.side_effects = None
        
        mock_get_db.return_value = fake_db()
        mock_get_db.query = MagicMock()

        mock_get_user_or_raise_401_mock = fake_user()

        #Act
        result = create_withdrawal(
                                    mock_get_user_or_raise_401_mock, 
                                    mock_get_db,
                                    withdrawal_amount
                                    )

        #Assert
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)




