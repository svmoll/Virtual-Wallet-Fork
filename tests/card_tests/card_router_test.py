import unittest
from unittest.mock import patch, Mock
from fastapi.responses import JSONResponse
from app.api.routes.users.schemas import UserViewDTO
from app.api.routes.cards.schemas import DeleteCardDTO
from app.api.routes.cards.router import create_card, delete_card, view_cards
import json

def fake_card():
    return DeleteCardDTO(
                        id=1,
                        account_id=1,
                        card_number='8765-4321-1234-5678'
                        )


def fake_db():
    return Mock()


def fake_user():
    return UserViewDTO(
         id=1,
         username='test_user'
    )


class CardRouter_Should(unittest.TestCase):


    @patch('app.api.routes.cards.router.create')
    def test_createCardSuccess_returnsTheCorrectStatusCodeAndMsg_WhenSuccessful(
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
        response_body = response.body.decode('utf-8')
        response_body_dict = json.loads(response_body)
        self.assertEqual(response_body_dict, 
                         {'message': f'New card for username: {mock_user.username} is created successfully.'}
                         )
        mock_create.assert_called_once_with(mock_user, mock_db)


    @patch("app.api.routes.cards.router.delete")
    @patch("app.api.routes.cards.router.get_card_by_id")
    def test_deleteCardSuccess_returnsTheCorrectStatusCode_WhenSuccessful(
        self, 
        mock_get_card_by_id,
        mock_service_delete
        ):

        # Arrange
        mock_user = fake_user()
        mock_user.id = 1
        db = fake_db()

        card_to_delete = fake_card()
        card_to_delete.account_id = mock_user.id
        card_to_delete.id = 1
        # mock_get_card_by_id.return_value = card_to_delete # assigned
        # mock_get_card_by_id.return_value = fake_card() # callable
        mock_get_card_by_id.return_value = [card_to_delete][0] # iterable, list itself does not have attributes e.g. account_id but list[0] can.
        mock_get_card_by_id.account_id = 1

        mock_service_delete.return_value = None

        # Act
        response = delete_card(card_to_delete.id, mock_user, db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)
        mock_get_card_by_id.assert_called_once_with(1, db)
        mock_service_delete.assert_called_once_with(1, db)
        response_body = response.body.decode('utf-8')
        response_body_dict = json.loads(response_body)
        self.assertEqual(response_body_dict, {
            'message': f"Your card with number: {card_to_delete.card_number} has been deleted successfully."
        })


    @patch("app.api.routes.cards.router.delete")
    @patch("app.api.routes.cards.router.get_card_by_id")
    def test_deleteCardSuccess_returnsTheCorrectStatusCode_WhenCardNotBelongToLoggedUser(
        self, 
        mock_get_card_by_id,
        mock_service_delete
        ):

        # Arrange
        mock_user = fake_user()
        db = fake_db()

        card_to_delete = fake_card()
        card_to_delete.account_id = 5
        card_to_delete.id = 1
        mock_get_card_by_id.return_value = card_to_delete
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
        mock_get_card_by_id.assert_called_once_with(1, db)


    # @patch('app.api.routes.cards.router.get_view')
    # def test_ViewUserCards_returnsCardsCorrectStatusCodeAndMsg_WhenSuccessful(
    #     self,
    #     mock_get_view
    #     ):
        
    #     # Arrange
    #     mock_user = fake_user()
    #     mock_db = fake_db()

    #     mock_view = [fake_card(),]
    #     mock_get_view.return_value = mock_view

    #     # Act
    #     response = view_cards(mock_user, mock_db)

    #     # Assert
    #     self.assertIsInstance(response, JSONResponse)
    #     self.assertEqual(response.status_code, 200)
    #     # response_body = response.body.decode('utf-8')
    #     # response_body_dict = json.loads(response_body)
    #     # self.assertEqual(response_body_dict, 
    #     #                  {'message': f'New card for username: {mock_user.username} is created successfully.'}
    #     #                  )
    #     # mock_view.assert_called_once_with(mock_user, mock_db)

    #     @patch('app.api.routes.cards.router.get_view')
    #     def test_ViewUserCards_returnsNoCards_WhenNoneAreAssociatedWithUser(
    #     self,
    #     mock_get_view
    #     ):
        
    #     # Arrange
    #     mock_user = fake_user()
    #     mock_db = fake_db()

    #     mock_view = [fake_card(),]
    #     mock_get_view.return_value = mock_view

    #     # Act
    #     response = view_cards(mock_user, mock_db)

    #     # Assert
    #     self.assertIsInstance(response, JSONResponse)
    #     self.assertEqual(response.status_code, 200)
    #     # response_body = response.body.decode('utf-8')
    #     # response_body_dict = json.loads(response_body)
    #     # self.assertEqual(response_body_dict, 
    #     #                  {'message': f'New card for username: {mock_user.username} is created successfully.'}
    #     #                  )
    #     # mock_view.assert_called_once_with(mock_user, mock_db)

