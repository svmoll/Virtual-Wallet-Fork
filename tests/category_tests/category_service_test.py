import unittest
from unittest.mock import patch, Mock 
from app.core.models import Category
from app.api.routes.users.schemas import UserViewDTO
from fastapi import HTTPException
from app.api.utils.responses import DatabaseError
from app.api.routes.categories.service import (
                                                create,
                                                category_exists,
                                                get_categories,
                                                generate_report,
                                                get_category_period_transactions,
                                                data_prep,
                                                visualise_report
                                                )
from decimal import Decimal


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
        # The creation of the Category would not have hit the DB by the time of thewhich would increment the next category.id
        # Hence the test is with category.id = None rather than an integer
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


    def test_categoryExists_returnsFalse_whenCategoryDoesntExist(self):
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
        # Arrange
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

        #Act
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
        mock_user = fake_user()
        mock_db = fake_db()

        mock_db.execute.side_effect = DatabaseError("Database error occurred")

        with unittest.mock.patch('app.api.routes.categories.service.logging.error'):
            result = get_categories(mock_user, mock_db)

        # Assertions
        self.assertEqual(result, []) 
    
    
    @patch('app.api.routes.categories.service.get_category_period_transactions')
    @patch('app.api.routes.categories.service.data_prep')
    @patch('app.api.routes.categories.service.visualise_report')
    def test_generateReport_returnsReportDataInTheCorrectFormat(
        self,
        mock_visualise_report,
        mock_data_prep,
        mock_get_category_period_transactions
        ):
        # Assign
        mock_db = fake_db()

        mock_get_category_period_transactions.return_value = None

        mock_category_names = ('Other',)
        mock_amounts = (100.0,)
        mock_percentages = [100.0]
        mock_data_prep.return_value = mock_category_names, mock_amounts, mock_percentages
        mock_visualise_report.return_value = (mock_category_names, mock_amounts, mock_percentages)
        
        #Act
        actual_result = generate_report(mock_category_names, mock_amounts, mock_percentages, mock_db)
        
        #Assert
        self.assertEqual((('Other',), (100.0,), [100.0]), actual_result)
        mock_get_category_period_transactions.assert_called_once()
        mock_data_prep.assert_called_once()
        mock_visualise_report.assert_called_once()


    def test_getCategoryPeriodTransactions_returnsResults_whenFindsRelevantTransactions(self):
        # Assign
        mock_db = fake_db()
        mock_user = fake_user()

        from_date = '2024-01-01'
        to_date = '2024-07-01'
        mock_db.execute.return_value.fetchall.return_value = [('Other', Decimal('100.00'))]
        
        #Act
        actual_result = get_category_period_transactions(
                                                        mock_user,
                                                        mock_db,
                                                        from_date, 
                                                        to_date, 
                                                        )
        
        #Assert
        self.assertEqual([('Other', Decimal('100.00'))], actual_result)


    def test_getCategoryPeriodTransactions_returnsHTTPException_whenNoRelevantTransactions(self):
        # Assign
        mock_db = fake_db()
        mock_user = fake_user()

        from_date = '2024-01-01'
        to_date = '2024-07-01'
        mock_db.execute.return_value.fetchall.return_value = []

        # Act & Assert 
        with self.assertRaises((HTTPException)) as context:
            get_category_period_transactions(
                                            mock_user,
                                            mock_db,
                                            from_date, 
                                            to_date, 
                                            )
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "There are no transactions in the relevant selected period.")


    def test_dataPrep_returnsResultsInCorrectFormat(self):
        # Assign
        fake_results = [('Other', Decimal('100.00'))]
        mock_results = fake_results

        #Act
        actual_result = data_prep(mock_results) 
        
        #Assert
        self.assertEqual((('Other',), (100.0,), [100.0]), actual_result)


    @patch('app.api.routes.categories.service.plt')
    def test_visualiseReport_plotsPieChart_whenSuccessful(
        self, 
        mock_plt
        ):
        #Arrage
        mock_db = fake_db()
        mock_category_names = ('Holidays', 'Other', 'Rent', 'Utilities')
        mock_amounts = (250.0, 100.0, 100.0, 100.0)
        mock_percentages = [45.45454545454545, 18.181818181818183, 18.181818181818183, 18.181818181818183]

        #Act
        actual_result = visualise_report(mock_category_names, mock_amounts, mock_percentages, mock_db)
        
        #Assert
        self.assertTrue(actual_result) 
        mock_plt.figure.assert_called_once()
        mock_plt.pie.assert_called_once()
        mock_plt.title.assert_called_once_with((f'Expenses by Category'))
        mock_plt.axis.assert_called_once_with('equal')
        mock_plt.savefig.assert_called_once_with('user_report_pie.png')
        mock_plt.show.assert_called_once()


    @patch('app.api.routes.categories.service.logging')
    @patch('app.api.routes.categories.service.plt')
    def test_visualiseReport_returnsHTTPException_whenSavefigFailsToSaveTheGraph(
        self, 
        mock_plt, 
        mock_logging
        ):
        #Arrage
        mock_db = fake_db()
        mock_category_names = ('Other',)
        mock_amounts = (100.0,)
        mock_percentages = [100.0]
        
        mock_plt.savefig.side_effect = Exception()

        # Act & Assert 
        with self.assertRaises((HTTPException)) as context:
                visualise_report(
                                mock_category_names, 
                                mock_amounts, 
                                mock_percentages, 
                                mock_db
                                )
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Graph savefig failed.")
        mock_logging.error.assert_called_once_with(f"Graph not saved: Graph savefig failed.")


    @patch('app.api.routes.categories.service.logging')
    def test_visualiseReport_closesDBConnectionAndLogsIt_whenSuccessful(self, mock_logging):
        #Arrage
        mock_db = fake_db()
        mock_category_names = ('Other',)
        mock_amounts = (100.0,67)
        mock_percentages = [100.0]

        # Assert
        visualise_report(mock_category_names, mock_amounts, mock_percentages, mock_db)
        
        # Assert
        mock_db.close.assert_called_once()
        mock_logging.info.assert_any_call("Database connection closed successfully.")

