import unittest
from sqlalchemy.orm import sessionmaker
from fastapi import status
from unittest.mock import patch, Mock
from app.api.routes.cards.router import create_card, delete_card
from app.api.routes.cards.schemas import DeleteCardDTO
from app.api.routes.users.schemas import UserViewDTO
from fastapi.responses import JSONResponse
import json
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def fake_card():
    return DeleteCardDTO(
                        id=1,
                        account_id=1,
                        card_number='8765432112345678'
                        )

def fake_db():
        return Mock()


def fake_user():
    return UserViewDTO(
         id=5,
         username='test_user'
    )

class CardRouter_Should(unittest.TestCase):

    @patch('app.api.routes.cards.service.create')
    def test_createCardSuccess_returnsTheCorrectStatusCode_WhenSuccessful(
        self,
        mock_create
        ):
        
        # Arrange
        mock_user = fake_user()
        mock_db = fake_db()

        mock_created_card = fake_card()
        mock_create.return_value = mock_created_card

        # Act
        response = create_card(mock_user, mock_db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 201)
        # Decode the response body
        response_body = response.body.decode('utf-8')
        # Parse the JSON response body
        response_body_dict = json.loads(response_body)
        # Assert the response message
        self.assertEqual(response_body_dict, 
                         {'message': 'New card for username {current_user.username} is created successfully.'}
                         )


    @patch("app.api.routes.cards.service.get_card_by_id")
    @patch("app.api.routes.cards.service.delete")
    def test_deleteCardSuccess_returnsTheCorrectStatusCode_WhenSuccessful(
        self, 
        mock_get_card_by_id,
        mock_service_delete
        ):

        # Arrange
        mock_user = fake_user()
        mock_user.id = 5
        db = fake_db()

        card_to_delete = fake_card()
        card_to_delete.account_id = mock_user.id
        card_to_delete.id = 1
        mock_get_card_by_id.return_value = card_to_delete # assigned
        # mock_get_card_by_id.return_value = fake_card() # callable
        # mock_get_card_by_id.return_value = [card_to_delete] # iterable
        mock_get_card_by_id.account_id = 1

        mock_service_delete.return_value = None

        # Act
        response = delete_card(card_to_delete.id, mock_user, db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)

        # response_body = response.body.decode('utf-8')
        # response_body_dict = json.loads(response_body)
        # self.assertEqual(response_body_dict, {
        #     'message': "Your card with number: {card_to_delete.card_number} has been deleted successfully."
        # })


    @patch("app.api.routes.cards.service.get_card_by_id")
    @patch("app.api.routes.cards.service.delete")
    def test_deleteCardSuccess_returnsTheCorrectStatusCode_WhenCardNotBelongToLoggedUser(
        self, 
        mock_get_card_by_id,
        mock_service_delete
        ):

        # Arrange
        mock_user = fake_user()
        db = fake_db()

        card_to_delete = fake_card()
        card_to_delete.account_id = 1
        card_to_delete.id = 1
        mock_get_card_by_id.return_value = card_to_delete
        print(mock_get_card_by_id)
        mock_service_delete.return_value = None

        # Act
        response = delete_card(card_to_delete.id, mock_user, db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 400)

        response_body = response.body.decode('utf-8')
        response_body_dict = json.loads(response_body)
        self.assertEqual(response_body_dict, {
            'message': f"Card with ID of {card_to_delete.id} does not belong to username: {mock_user.username}. "
        })