import unittest
from unittest.mock import patch, Mock
from fastapi.responses import JSONResponse
from app.api.routes.users.schemas import UserViewDTO
from app.api.routes.categories.schemas import CategoryDTO
from app.api.routes.categories.router import create_category
import json

def fake_category():
    return CategoryDTO(
    id=1,
    name="Utilities",
    color_hex=None
    )

def fake_db():
    return Mock()   

def fake_user():
    return UserViewDTO(
         id=1,
         username='test_user'
    )

class CardRouter_Should(unittest.TestCase):

    @patch('app.api.routes.categories.router.create')
    def test_createCategorySuccess_returnsTheCorrectStatusCodeAndMsg_WhenSuccessful(
        self,
        mock_create,
        ):
        # Arrange
        mock_user = fake_user()
        mock_db = fake_db()

        mock_category = fake_category()
        mock_create.return_value = mock_category
        # Act
        response = create_category(mock_category, mock_user, mock_db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 201)
        response_body = json.loads(response.body.decode('utf-8'))
        self.assertEqual(response_body,
                         {'message': f"{mock_category.name} category is created successfully"}
                         )
        mock_create.assert_called_once_with(mock_category, mock_db)


