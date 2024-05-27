import asyncio
import unittest
from unittest.mock import patch, Mock, MagicMock
from app.api.routes.users.schemas import UserDTO, UpdateUserDTO, UserViewDTO
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.api.routes.cards.schemas import CardDTO
from app.api.routes.cards.service import unique_card_number, create_cvv_number, create_card_number, create_expiration_date, get_user_fullname
from datetime import datetime, timedelta
import random

def fake_card_dto():
    return CardDTO(
        account_id=1,
        card_number= "1111222233334444",
        expiration_date= "2024-02-02",
        card_holder= "Dimitar Berbatov",
        cvv= "123"
    )


def fake_user_view():
    return UserViewDTO(id=1, username="testuser", fullname="Georgi Stoev")


Session = sessionmaker()


def fake_db():
    session_mock = MagicMock(spec=Session)
    session_mock.query = MagicMock()
    session_mock.query.filer = MagicMock()
    return session_mock

class CardsServiceShould(unittest.TestCase):

    @patch("app.api.routes.cards.service.random.choice")
    def test_createCardNumber_IsCorrect(self, create_mock):
        # Arrange
        create_mock.side_effect = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '1', '2', '3', '4', '5', '6']

        # Act
        result = create_card_number()

        # Assert
        self.assertEqual(result, '1234567890123456')
        self.assertEqual(len(result), 16)
        create_mock.assert_called_with('0123456789')
        self.assertEqual(create_mock.call_count, 16)


    @patch("app.api.routes.cards.service.datetime")
    def test_createExpirationDate_IsCorrect(self, datetime_mock):
        #Arrange
        fixed_time_now = datetime(2024,1,1)
        datetime_mock.now.return_value = fixed_time_now
        datetime_mock.timedelta = timedelta

        # Act 
        result = create_expiration_date()

        #Assert
        expected_date = fixed_time_now + timedelta(days=1826)
        self.assertEqual(expected_date, result)
        
    @patch('app.api.routes.cards.service.random.choice')
    def test_generateCvv_IsCorrectFormat(self, mock_random_choice):
        # Arrange
        mock_random_choice.side_effect = lambda x: x[0]  # Return the first character of the input 'digits'

        # Act 
        result = create_cvv_number()

        # Assert
        self.assertTrue(result.isdigit())  
        self.assertEqual(len(result), 3)   
        mock_random_choice.assert_called_with('0123456789')  
        self.assertEqual(mock_random_choice.call_count, 3)   

    # @patch('app.api.routes.cards.service.create_card_number')
    # @patch('app.api.routes.cards.service.get_db')
    # def test_unique_card_number_generation(self, mock_get_db, mock_create_card_number):
    #     # Arrange
    #     mock_db_session = MagicMock(spec=Session)
    #     mock_get_db.return_value = mock_db_session

    #     # Mock behavior of querying the database
    #     mock_query = mock_db_session.query.return_value # breaks here
    #     mock_filter_by = mock_query.filter_by.return_value
    #     mock_filter_by.first.return_value = None
        
    #     # Mock behavior of create_card_number
    #     mock_create_card_number.side_effect = ['1234567890123456', '2345678901234567', '3456789012345678']

    #     # Act
    #     result1 = unique_card_number()
    #     result2 = unique_card_number()
    #     result3 = unique_card_number()

    #     # Assert
    #     self.assertEqual(result1, '1234567890123456')
    #     self.assertEqual(result2, '2345678901234567')
    #     self.assertEqual(result3, '3456789012345678')

    #     # Verify mock calls
    #     mock_create_card_number.assert_called()
    #     self.assertEqual(mock_create_card_number.call_count, 3)
    #     mock_db_session.query.assert_called_with(Card)
    #     mock_db_session.query.return_value.filter_by.assert_called()
    #     mock_db_session.query.return_value.filter_by.return_value.first.assert_called_with(card_number=result1)

    # @patch('app.api.routes.users.service.get_db')
    # def test_get_user_fullname(self, mock_get_db):
    #     # Arrange
    #     mock_db_session = MagicMock(spec=Session)
    #     mock_get_db.return_value = mock_db_session

    #     mock_user = fake_user_view()
    #     mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user

    #     mock_current_user = MagicMock()
    #     mock_current_user.id = 1

    #     # Act
    #     result = get_user_fullname(mock_current_user, mock_db_session)

    #     # Assert
    #     self.assertEqual(result, mock_user)

    #     # Verify mock calls
    #     mock_db_session.query.assert_called_once()  # Ensure query(User) was called once
    #     mock_db_session.query.return_value.filter_by.assert_called_once_with(id=mock_current_user.id)  # Ensure filter_by was called with the correct argument
    #     mock_db_session.query.return_value.filter_by.return_value.first.assert_called_once()  # Ensure first() was called once


