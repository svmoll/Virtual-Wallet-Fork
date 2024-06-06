import unittest
from jose import jwt
from unittest.mock import patch, Mock, call 
from app.core.models import Card
from datetime import timedelta, date
from fastapi import HTTPException
from app.api.routes.cards.service import (
                                        unique_card_number, 
                                        create_cvv_number, 
                                        create_card_number, 
                                        create_expiration_date, 
                                        decrypt_cvv,
                                        get_user_fullname,
                                        get_card_by_id,
                                        delete,
                                        )



def fake_card():
    return Mock()


def fake_user_view():
    return Mock()


def fake_db():
    return Mock()


class CardsServiceShould(unittest.TestCase):


    @patch("app.api.routes.cards.service.random.choice")
    def test_createCardNumber_IsCorrectFormat(self, create_mock):
        # Arrange
        create_mock.side_effect = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '1', '2', '3', '4', '5', '6']

        # Act
        result = create_card_number()

        # Assert
        self.assertEqual(result, '1234-5678-9012-3456')
        self.assertEqual(len(result), 19)
        create_mock.assert_called_with('0123456789')
        self.assertEqual(create_mock.call_count, 16)


    @patch('app.api.routes.cards.service.create_card_number')
    @patch('app.api.routes.cards.service.get_db')
    def test_createCardNumber_createsUniqueCardNumber(self, mock_get_db, mock_create_card_number):
        # Arrange
        mock_db_session = fake_db()
        mock_get_db.return_value = mock_db_session

        def filter_by_side_effect(card_number):
            filter_mock = Mock()
            filter_mock.first.return_value = None
            return filter_mock

        mock_query = mock_db_session.query.return_value
        mock_query.filter_by.side_effect = filter_by_side_effect

        mock_create_card_number.side_effect = ['1234-5678-9012-3456', '2345-6789-0123-4567', '3456-7890-1234-5678']

        # Act
        result1 = unique_card_number(mock_db_session)
        result2 = unique_card_number(mock_db_session)
        result3 = unique_card_number(mock_db_session)

        # Assert
        assert result1 == '1234-5678-9012-3456'
        assert result2 == '2345-6789-0123-4567'
        assert result3 == '3456-7890-1234-5678'

        # Verify mock calls
        mock_create_card_number.assert_called()
        assert mock_create_card_number.call_count == 3
        mock_db_session.query.assert_called_with(Card)
        mock_query.filter_by.assert_has_calls([
            call(card_number='1234-5678-9012-3456'),
            call(card_number='2345-6789-0123-4567'),
            call(card_number='3456-7890-1234-5678')
        ], any_order=True)
        assert mock_query.filter_by.call_count == 3


    @patch("app.api.routes.cards.service.date")
    def test_createExpirationDate_IsCorrect(self, date_mock):
        #Arrange
        fixed_time_now = date.today()
        date_mock.today.return_value = fixed_time_now
        date_mock.timedelta = timedelta

        # Act 
        result = create_expiration_date()

        #Assert
        expected_date = fixed_time_now + timedelta(days=1826)
        self.assertEqual(expected_date, result)


    @patch('app.api.routes.cards.service.random.choice')
    def test_generateCvv_randomChoiceIsCalledCorrectly(
        self, 
        mock_random_choice
        ):
        # Arrange
        mock_random_choice.side_effect = lambda x: x[0]
        
        # Act
        result = create_cvv_number()

        # Assert
        self.assertEqual(len(result), 99)
        mock_random_choice.assert_called_with('0123456789')
        self.assertEqual(mock_random_choice.call_count, 3)


    # @patch('app.api.routes.cards.service.random.choice')
    @patch('random.choice') # also works
    def test_createCvvNumber_encryptCvv_encryptsCorrectly(self, mock_random_choice):
        # Arrange
        mock_random_choice.side_effect = ['4', '4', '4']  # Predictable CVV '123'
        
        # Act
        formatted_cvv = create_cvv_number()

        # Assert
        expected_encrypted_cvv = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdnYiOiI0NDQifQ.fknnE5fh6cZHpIBnW934gIxqQsm2zdq3PDPgUQ8hd4Y"
        self.assertEqual(formatted_cvv, expected_encrypted_cvv)


    @patch('app.api.routes.cards.service.jwt.decode')
    def test_decryptCvv_returnsCorrectFormat(
        self, 
        mock_jwt_decode
        ):
        # Arrange
        mock_jwt_decode.return_value = '444'
        
        # Act
        encrypted_cvv = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdnYiOiI0NDQifQ.fknnE5fh6cZHpIBnW934gIxqQsm2zdq3PDPgUQ8hd4Y"
        actual_result = decrypt_cvv(encrypted_cvv)

        # Assert
        self.assertEqual(len(actual_result), 3)
        self.assertEqual(mock_jwt_decode.return_value, actual_result)
        self.assertTrue(actual_result.isdigit(), "service.decrypt_cvv does not return digits")


    def test_getUserFullName_returnsCorrectName(self):
        # Arrange
        mock_db_session = fake_db()

        mock_user = fake_user_view()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        mock_current_user = fake_user_view()

        # Act
        result = get_user_fullname(mock_current_user, mock_db_session)

        # Assert
        self.assertEqual(mock_user, result)

        # Verify mock calls
        mock_db_session.query.assert_called_once()  
        mock_db_session.query.return_value.filter_by.assert_called_once_with(username=mock_current_user.username)
        mock_db_session.query.return_value.filter_by.return_value.first.assert_called_once()


    @patch('app.api.routes.cards.service.get_db')
    def test_getCardById_returnsTheCardSuccessfully(self, mock_get_db):
        # Arrange
        expected_card = fake_card() 

        db = fake_db()
        mock_get_db.return_value = db
        db.query(Card).filter_by(id=expected_card.id).first.return_value = expected_card

        # Act
        actual_card = get_card_by_id(expected_card.id, db)

        # Assert
        self.assertEqual(actual_card, expected_card)


    @patch('app.api.routes.cards.service.get_db')
    def test_getCardById_returnsReturnsHTTPExceptionWhenNotFound(self, mock_get_db):
        # Arrange
        card_id = 12231  
        db = fake_db()
        mock_get_db.return_value = db
        db.query(Card).filter_by(id=card_id).first.return_value = None

        # Act
        try:
            get_card_by_id(card_id, db)
            self.fail("Expected HTTPException not raised.")
        except HTTPException as e:
        
        # Assert
            self.assertEqual(e.status_code, 404)
            self.assertEqual(e.detail, "Card not found!")


    @patch('app.api.routes.cards.service.get_card_by_id')
    @patch('app.api.routes.cards.service.get_db')
    def test_deleteCard_trulyDeleted(self, mock_get_db, mock_get_card_by_id):
        # Arrange
        card = fake_card()
        db = fake_db()
        db.delete = Mock()
        db.commit = Mock()
        mock_get_db.return_value = db

        card_to_delete = Mock(spec=Card)
        mock_get_card_by_id.return_value = card_to_delete

        # Act
        delete(card.id, db)

        # Assert
        mock_get_card_by_id.assert_called_once_with(card.id, db)
        db.delete.assert_called_once_with(card_to_delete)
        db.commit.assert_called_once()

    @patch('app.api.routes.cards.service.get_card_by_id')
    def test_deleteCard_trulyDeleted(self,  mock_get_card_by_id):
        # Arrange
        card = fake_card()
        db = fake_db()
        db.delete = Mock()
        db.commit = Mock()
        # mock_get_db.return_value = db

        card_to_delete = Mock(spec=Card)
        mock_get_card_by_id.return_value = card_to_delete

        # Act
        delete(card.id, db)

        # Assert
        mock_get_card_by_id.assert_called_once_with(card.id, db)
        db.delete.assert_called_once_with(card_to_delete)
        db.commit.assert_called_once()


