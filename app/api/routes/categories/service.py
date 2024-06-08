from .schemas import CreateCategoryDTO
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, func
from app.core.models import Category, Transaction
from fastapi import HTTPException
from app.api.utils.responses import DatabaseError
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import logging



def create(
    category: CreateCategoryDTO, 
    db: Session
    ):
    
    try:
        if category_exists(category, db):
            raise HTTPException(
                status_code=400, 
                detail="Category already exists. Please use the existing one or try a different name."
                )
        else:
            category = Category(
                name=category.name
                )
            
            db.add(category)
            db.commit()
            db.refresh(category)
            return category
        
    except HTTPException as e:
        raise e
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
    # except SQLAlchemyError as e:
        logging.error(f"Database error occurred: {e}")
        return []
    

def generate_report(
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
        report_data = data_prep(results, db)
        
        return report_data
    except Exception as e:
        # Handle exceptions
        logging.error(f"Error occurred: {e}")
        return None


def data_prep(results,db):
    columns = [(category, float(amount)) for category, amount in results]
    category_names, amounts = zip(*columns)
    percentages = [amount / sum(amounts) * 100 for amount in amounts]
    return visualise_report(category_names, amounts, percentages, db)


def visualise_report(category_names, amounts, percentages, db):
    try:
        def autopct_format(pct):
            amount = (pct / 100. * sum(amounts))
            return f'{pct:.1f}%\n${amount:.0f}'

        my_explode = [0.05] * len(category_names)

        plt.figure(figsize=(8, 8))
        _,_,autotexts = plt.pie(amounts, 
                labels=category_names, 
                autopct=autopct_format,
                startangle=140,
                explode=my_explode
                )
        for autotext in autotexts:
            autotext.set_fontsize(12)
            autotext.set_color('white')

        plt.title(f'Expenses by Category')
        plt.axis('equal')
        plt.tight_layout()

        plt.savefig('user_report_pie.png') #Where to save it?
        logging.info("Plot is saved successfully as 'user_report_pie.png'")
        plt.show()
        # plt.close()

        report_data = category_names, amounts, percentages

        try:
            db.close()
            logging.info("Database connection closed successfully.")
        except Exception as e:
            logging.error(f"Error closing database connection: {e}")
            #create a test to ensure it is closed
        return report_data 

    except Exception as e:
        # Handle exceptions
        logging.error(f"Error occurred: {e}")
        return None
    
