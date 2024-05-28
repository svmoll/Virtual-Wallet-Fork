import asyncio
import unittest
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException, status
from unittest.mock import patch, Mock, MagicMock, create_autospec
from app.api.routes.users.schemas import UserDTO, UpdateUserDTO, UserDTO
from app.core.models import Card
from app.api.routes.cards.router import create_card, delete_card
from app.api.routes.cards.schemas import CardDTO, UserViewDTO


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
    return MagicMock(spec=Session)


def fake_user_view():
    return UserDTO(id=1, username="testuser", fullname="Georgi Hristov")


class CardRouter_Should(unittest.TestCase):

    @patch('app.api.routes.cards.router.create_card')
    def test_createCard_returnsCorrectStatusCodeWhenSuccessful(self, create_mock):
        #Arrange
        # card = fake_card()
        # create_mock.return_value = card

        user = fake_user_view()
        db = fake_db()
        #Act
        result = create_card(user, db)
        #Assert
        create_mock.assert_called_once()
        expected_result = status.HTTP_201_CREATED
        self.assertEqual(expected_result, result)


