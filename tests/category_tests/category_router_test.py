import unittest
from unittest.mock import patch, Mock
from fastapi.responses import JSONResponse
from app.api.routes.users.schemas import UserViewDTO
from app.core.models import Category
from app.api.routes.categories.router import create_category, get_categories_list
import json

def fake_category():
    return Category(
    id=1,
    name="Utilities",
    color_hex=None
    )

def fake_category_json():
    return [
            {
                'id': 1,
                'name': 'Rent'
            }
        ]


def fake_db():
    return Mock()   

def fake_user():
    return UserViewDTO(
         id=1,
         username='test_user'
    )

class CategoriesRouter_Should(unittest.TestCase):

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

    @patch('app.api.routes.categories.router.get_categories')
    def test_getCategoriesList_returnsTheCorrectStatusCodeAndMsg_WhenUserHasCategories(
        self,
        mock_get_categories
        ):
        # Arrange
        mock_user = fake_user()
        mock_db = fake_db()

        mock_category = fake_category_json()
        mock_get_categories.return_value = mock_category

        # Act
        response = get_categories_list(mock_user, mock_db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.body.decode('utf-8'))
        self.assertEqual(response_body, {
                "message": f"This is your list of categories:",
                "categories": mock_category
            })
        mock_get_categories.assert_called_once_with(mock_user, mock_db)


    @patch('app.api.routes.categories.router.get_categories')
    def test_getCategoriesList_returnsTheCorrectStatusCodeAndMsg_WhenUserHasNoTransactionsWithCategories(
        self,
        mock_get_categories
        ):
        # Arrange
        mock_user = fake_user()
        mock_db = fake_db()

        mock_get_categories.return_value = None

        # Act
        response = get_categories_list(mock_user, mock_db)

        # Assert
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.body.decode('utf-8'))
        self.assertEqual(response_body, {
                    "message": f"There are no associated categories with your username: {mock_user.username}."
                },)
        mock_get_categories.assert_called_once_with(mock_user, mock_db)
