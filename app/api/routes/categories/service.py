from .schemas import CreateCategoryDTO
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.models import Category, Transaction
from fastapi import HTTPException
from app.api.utils.responses import (
                                    DatabaseError, 
                                    CategoryExistsError, 
                                    NoRelevantTransactionsError,
                                    GraphNotSavedError
                                    )
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import logging


def create(
    category: CreateCategoryDTO, 
    db: Session
    ):
    
    try:
        if category_exists(category, db):
            raise CategoryExistsError()
        else:
            category = Category(
                name=category.name
                )
            
            db.add(category)
            db.commit()
            db.refresh(category)
            return category

    except CategoryExistsError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


def category_exists(
    category, 
    db: Session
    ):
    query = select(Category).filter(Category.name == category.name)
    category = db.execute(query).fetchone() 
    return True if category else False

def get_categories(user,db):
    try:
        user_categories = db.execute(
                            select(Category)
                            .join(Transaction, Transaction.category_id == Category.id)
                            .filter(Transaction.sender_account == user.username)
                            .distinct()
                            ).scalars().all()

        user_categories = [
            {
                "category_id": category.id,
                "category_name": category.name
            }
            for category in user_categories
        ]
        return user_categories
    except DatabaseError as e:
        logging.error(f"Database error occurred: {e}")
    

def generate_report(
    current_user,
    db: Session,
    from_date, 
    to_date, 
    ):
    results = get_category_period_transactions(current_user,db,from_date, to_date)
    category_names, amounts, percentages = data_prep(results)
    report_data = visualise_report(category_names, amounts, percentages, db)
    return report_data


def get_category_period_transactions(
    current_user,
    db: Session,
    from_date, 
    to_date, 
    ):
    try:
        query = (
            select(Category.name, func.sum(Transaction.amount))
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(Transaction.sender_account == current_user.username and 
                    # Transaction.transaction_date >= '2024-01-01', Transaction.transaction_date <= '2024-07-01')
                    Transaction.transaction_date >= from_date, Transaction.transaction_date <= to_date)
            .group_by(Category.name)
            )
        results = db.execute(query).fetchall()
        logging.info(f'DB query results:{results}')
        if results:
            return results
        else:
            raise NoRelevantTransactionsError()
    except NoRelevantTransactionsError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        # Handle exceptions
        logging.error(f"Error occurred: {e}")



def data_prep(results):
    columns = [(category, float(amount)) for category, amount in results]
    category_names, amounts = zip(*columns)
    percentages = [amount / sum(amounts) * 100 for amount in amounts]
    return category_names, amounts, percentages


def visualise_report(category_names, amounts, percentages, db):
    try:
        def autopct_format(pct):
            amount = (pct / 100. * sum(amounts))
            return f'{pct:.1f}%\n${amount:.0f}'

        my_explode = [0.01] * len(category_names)

        plt.figure(figsize=(8, 8))
        pie_graph_result = plt.pie(amounts, 
                labels=category_names, 
                autopct=autopct_format,
                startangle=140,
                explode=my_explode
                )
        autotexts = pie_graph_result[2]
        for autotext in autotexts:
            autotext.set_fontsize(12)
            autotext.set_color('white')

        plt.title(f'Expenses by Category')
        plt.axis('equal')
        plt.tight_layout()

        try: 
            plt.savefig('user_report_pie.png')
            logging.info("Graph is saved successfully as 'user_report_pie.png'")
            # plt.close()
        except:
            raise GraphNotSavedError()
    
        plt.show()
        return True
    except GraphNotSavedError as e:
            logging.error(f"Graph not saved: {e.message}")
            raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        # Handles other exceptions
        logging.error(f"Error occurred: {e}")
        return False
    
    finally:
        try:
            db.close()
            logging.info("Database connection closed successfully.")
        except DatabaseError as e:
            logging.error(f"Error closing database connection: {e}")
            
    
