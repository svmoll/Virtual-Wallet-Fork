import unittest
from unittest.mock import patch, Mock, call 
from app.core.models import Category
from app.api.routes.users.schemas import UserViewDTO
from app.api.routes.categories.schemas import CategoryDTO
from datetime import timedelta, date
from fastapi import HTTPException
from app.api.routes.categories.service import (
                                            create,
                                            category_exists
                                            )

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


class CardsServiceShould(unittest.TestCase):



    def test_create_ReturnsTheCreatedCategoryObject_whenSuccessul(self):
        # Arrange
        mock_category = fake_category()
        mock_db = fake_db()

        # Act
        result = create(mock_category,mock_db)
        expected_result = mock_category

        # Assert
        self.assertEqual(result, expected_result)

    def test_categoryExists_returnsTrue_whenCategoryExists(self):
        # Arrange
        mock_category = fake_category()
        mock_db = fake_db()

        # Act
        result = category_exists(mock_category,mock_db)

        # Assert
        self.assertEqual(result, True)


    def test_categoryExists_returnsTrue_whenCategoryDoesntExists(self):
        # Arrange
        mock_category = fake_category()
        mock_db = fake_db()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = category_exists(mock_category,mock_db)

        # Assert
        self.assertEqual(result, False)


    @patch('app.api.routes.categories.service.category_exists')
    def test_createCategory_returnsHTTPException_whenCategoryExists(
        self,
        mock_category_exists
        ):
        # Arrange
        mock_category = fake_category()
        mock_user = fake_user()
        mock_db = fake_db()

        mock_category_exists.return_value = True

        # Act & Assert 
        with self.assertRaises((HTTPException)) as context:
            create(mock_category, mock_db)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Category already exists. Please use the existing one or try a different name.")






