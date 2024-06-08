import unittest
from unittest.mock import patch, Mock 
from app.core.models import Category
from app.api.routes.users.schemas import UserViewDTO
from fastapi import HTTPException
from app.api.utils.responses import DatabaseError
from app.api.routes.categories.service import (
                                            create,
                                            category_exists,
                                            get_categories
                                            )

def fake_category():
    return Category(
    id=1,
    name="Utilities"
    )

def fake_db():
    return Mock()   

def fake_user():
    return UserViewDTO(
         id=1,
         username='test_user'
    )


class CategoriesServiceShould(unittest.TestCase):

    @patch('app.api.routes.categories.service.category_exists')
    def test_create_ReturnsTheCreatedCategoryObject_whenSuccessul(
        self,
        mock_category_exists
        ):
        # Arrange
        mock_category = fake_category()
        # The creation of the Category would not have hit the DB which would increment the next category.id
        mock_category.id = None 
        mock_db = fake_db()

        mock_category_exists.return_value = False

        # Act
        result = create(mock_category,mock_db)
        expected_result = mock_category

        # Assert
        self.assertEqual(result.name, expected_result.name)
        self.assertEqual(result, expected_result)

    def test_categoryExists_returnsTrue_whenCategoryExists(self):
        # Arrange
        mock_category = fake_category()
        mock_db = fake_db()

        mock_db.execute.return_value.fetchone.return_value = mock_category.name

        # Act
        result = category_exists(mock_category,mock_db)

        # Assert
        self.assertEqual(result, True)


    def test_categoryExists_returnsFalse_whenCategoryDoesntExists(self):
        # Arrange
        mock_category = fake_category()
        mock_category.id = None
        mock_db = fake_db()
        mock_db.execute.return_value.fetchone.return_value = None

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
        mock_db = fake_db()

        mock_category_exists.return_value = True

        # Act & Assert 
        with self.assertRaises((HTTPException)) as context:
            create(mock_category, mock_db)
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Category already exists. Please use the existing one or try a different name.")


    def test_getCategories_returnCategoriesObjects_whenSuccessful(self):
        mock_user = fake_user()
        mock_db = fake_db()

        mock_execute = Mock()
        mock_db.execute.return_value = mock_execute

        mock_scalars = Mock()
        mock_execute.scalars.return_value = mock_scalars

        mock_category = fake_category()
        mock_category2 = fake_category()
        mock_category2.id = 2
        mock_category2.name = 'Rent'

        mock_all = [mock_category, mock_category2]
        mock_scalars.all.return_value = mock_all

        # Call the function with mocked objects
        with unittest.mock.patch('app.api.routes.categories.service.logging.error'):
            result = get_categories(mock_user, mock_db)

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['category_id'], 1)
        self.assertEqual(result[0]['category_name'], 'Utilities')
        self.assertEqual(result[1]['category_id'], 2)
        self.assertEqual(result[1]['category_name'], 'Rent')
        mock_db.execute.assert_called_once()


    def test_getCategories_returnsDatabaseError_whenUnknownErrorOccurs(self):
        # Mock the user and db objects
        mock_user = fake_user()
        mock_db = fake_db()

        mock_db.execute.side_effect = DatabaseError("Database error occurred")

        with unittest.mock.patch('app.api.routes.categories.service.logging.error'):
            result = get_categories(mock_user, mock_db)

        # Assertions
        self.assertEqual(result, []) 




