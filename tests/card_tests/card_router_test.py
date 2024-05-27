import asyncio
import unittest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock, MagicMock, create_autospec
from app.api.routes.users.schemas import UserDTO, UpdateUserDTO, UserViewDTO
from app.core.models import Card
from app.api.routes.cards.router import create_card
from app.api.routes.cards.schemas import CardDTO, UserViewDTO


def fake_card():
    return Card(
        account_id=1,
        card_number= "1111222233334444",
        expiration_date= "2024-02-02",
        card_holder= "Dimitar Berbatov",
        cvv= "123"
    )

def fake_card_dto():
    return CardDTO(
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
    return UserViewDTO(id=1, username="testuser")


class CardRouter_Should(unittest.TestCase):

    @patch('app.api.routes.cards.router.create_card')
    def test_createCard_IsSuccessful(self, create_mock):
        #arrange
        card = fake_card()
        create_mock.return_value = card

        user = fake_user_view()
        db = fake_db()
        # Act
        async def async_test():
            result = await create_card(user, db)
        #Assert
            create_mock.assert_called_once()
            expected_result = card
            self.assertEqual(expected_result, result)

        asyncio.run(async_test())



