import unittest
from sqlalchemy.orm import sessionmaker
from fastapi import status
from unittest.mock import patch, Mock, MagicMock
from app.api.routes.users.schemas import UserDTO
from app.core.models import Card
from app.api.routes.cards.router import create_card, delete_card
from app.api.utils.responses import Forbidden


def fake_card():
    # return Card(
    #     account_id=1,
    #     card_number= "1111222233334444",
    #     expiration_date= "2024-02-02",
    #     card_holder= "Dimitar Berbatov",
    #     cvv= "123"
    # )
    return MagicMock()


Session = sessionmaker()


def fake_db():
    session_mock = MagicMock(spec=Session)
    # session_mock = MagicMock()
    # session_mock.query = MagicMock()
    # session_mock.query.filter = MagicMock()
    return session_mock


def fake_user_view():
    return UserDTO(
        username="testuser", 
        password="User!234",
        phone_number="1234567891",
        email="email@email.com",
        fullname="Salvador Dali"
    )

class CardRouter_Should(unittest.TestCase):


    @patch('app.core.db_dependency.get_db')
    @patch('app.api.auth_service.auth.get_user_or_raise_401')
    @patch('app.api.routes.cards.service.create')
    def test_createCardSuccess_returnsTheCorrectStatusCodeSuccessfully(
        self,
        mock_get_user_or_raise_401, 
        mock_get_db, 
        mock_create
        ):
        
        # Arrange
        mock_user = fake_user_view()
        mock_get_user_or_raise_401.return_value = mock_user

        db = fake_db()
        db.query.return_value = MagicMock()
        # db.query.filter_by.return_value = MagicMock()
        mock_get_db.return_value = db

        mock_created_card = fake_card()
        mock_create.return_value = mock_created_card

        # Act
        response = create_card(mock_user, mock_get_db)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        mock_create.assert_called_once_with(mock_user, db)


    @patch("app.api.routes.cards.service.delete")
    @patch("app.core.db_dependency.get_db")
    @patch("app.api.auth_service.auth.get_user_or_raise_401")
    def test_deleteCardSuccess_returnsTheCorrectStatusCodeSuccessfully(
        self, 
        mock_get_user, 
        mock_get_db, 
        mock_service_delete
        ):

        # Arrange
        card_to_delete = fake_card()
        card_to_delete.id = 1

        user = fake_user_view()
        mock_get_user.return_value = user

        mock_get_db.return_value = fake_db()
        db = fake_db()
        db.query = Mock()
        db.delete = Mock()
        db.commit = Mock()
        
        
        # mock_service_delete = Mock()
        mock_service_delete.return_value = None

        # Act
        response = delete_card(card_to_delete.id, mock_get_user, db)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT