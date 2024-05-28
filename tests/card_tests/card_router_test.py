import unittest
from sqlalchemy.orm import sessionmaker
from fastapi import status
from unittest.mock import patch, Mock, MagicMock, create_autospec
from app.api.routes.users.schemas import UserDTO
from app.core.models import Card
from app.api.routes.cards.router import create_card


def fake_card():
    return Card(
        account_id=1,
        card_number= "1111222233334444",
        expiration_date= "2024-02-02",
        card_holder= "Dimitar Berbatov",
        cvv= "123"
    )


Session = sessionmaker()


def fake_db():
    session_mock = MagicMock(spec=Session)
    session_mock.query = MagicMock()
    session_mock.query.filter = MagicMock()
    return session_mock


def fake_user_view():
    return UserDTO(
        username="testuser", 
        password="User!234",
        phone_number="1234567891",
        email="email@email.com",
        fullname="Georgi Stoev"
    )

class CardRouter_Should(unittest.TestCase):

    @patch('app.api.routes.cards.router.service')  
    @patch('app.core.db_dependency.get_db')
    def test_createCardSuccess_returnsTheCorrectStatusCodeSuccessfully(self, mock_get_db, mock_service):
        #Arrange
        mock_current_user = fake_user_view()

        mock_db_session = fake_db()
        mock_get_db.return_value = mock_db_session

        mock_created_card = fake_card()
        mock_service.create.return_value = mock_created_card

        #Act
        response = create_card(current_user=mock_current_user, db=mock_db_session)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    @patch('app.api.routes.cards.router.service')  
    @patch('app.core.db_dependency.get_db')
    def test_createCardSuccess_returnsCorrectParametersSuccessfully(self, mock_get_db, mock_service):
        #Arrange
        mock_current_user = fake_user_view()

        mock_db_session = fake_db()
        mock_get_db.return_value = mock_db_session

        mock_created_card = fake_card()
        mock_service.create.return_value = mock_created_card

        #Act
        response = create_card(current_user=mock_current_user, db=mock_db_session)

        # Assert
        mock_service.create.assert_called_once_with(mock_current_user, mock_db_session)


