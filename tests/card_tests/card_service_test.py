import asyncio
import unittest
from unittest.mock import patch, Mock, MagicMock
from app.api.routes.users.schemas import UserDTO, UpdateUserDTO, UserViewDTO
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.api.routes.cards.schemas import CardDTO
from app.api.routes.cards.service import create, generate_cvv_number, generate_card_number, user_fullname


def fake_card_dto():
    return CardDTO(
        account_id=1,
        card_number= "1111222233334444",
        expiration_date= "2024-02-02",
        card_holder= "Dimitar Berbatov",
        cvv= "123"
    )


def fake_user_view():
    return UserViewDTO(id=1, username="testuser")


Session = sessionmaker()


def fake_db():
    session_mock = MagicMock(spec=Session)
    session_mock.query = MagicMock()
    session_mock.query.filer = MagicMock()
    return session_mock

class CardsServiceShould(unittest.TestCase):

    @patch('app.api.routes.cards.service.create')
    def test_generateExpirationDate_IsCorrect(self, create_mock):
        #Arrange
        card = fake_card_dto()
        create_mock.return_value = card

        user = fake_user_view()
        db = fake_db()
        # Act 
        async def async_test():
            new_card = await create(user, db)
            result = new_card.expiration_date
        #Assert
            create_mock.assert_called_once()
            expected_result = card.expiration_date
            self.assertEqual(expected_result, result)

        asyncio.run(async_test())

    @patch('app.api.routes.cards.service.generate_cvv_number')
    def test_generateCvv_IsCorrectFormat(self, create_mock):
        #Arrange
        card = fake_card_dto()
        create_mock.return_value = card

        # Act 
        async def async_test():
            new_cvv = await generate_cvv_number()
            result = new_cvv
        #Assert
            create_mock.assert_called_once()
            expected_result = card.cvv
            self.assertEqual(expected_result, result)

        asyncio.run(async_test())

    @patch('app.api.routes.cards.service.generate_card_number')
    def test_generateCardNumber_IsCorrect(self, create_mock):
        #Arrange
        card = fake_card_dto()
        create_mock.return_value = card

        # Act 
        async def async_test():
            new_card_number = await generate_card_number()
            result = new_card_number
        #Assert
            create_mock.assert_called_once()
            expected_result = card.card_number
            self.assertEqual(expected_result, result)

        asyncio.run(async_test())

    # @patch('app.api.routes.cards.service.create')
    # def test_SelectsCardHolderFullname_returnCorrectName(self, create_mock): # complete
    #     #Arrange
    #     card = fake_card_dto()
    #     create_mock.return_value = card

    #     user = fake_user_view()
    #     db = fake_db()
    #     # Act 
    #     async def async_test():
    #         new_card = await create(user, db)
    #         result = new_card.fullname
    #     #Assert
    #         create_mock.assert_called_once()
    #         expected_result = card.fullname
    #         self.assertEqual(expected_result, result)

    #     asyncio.run(async_test())

