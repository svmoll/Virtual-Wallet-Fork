from .schemas import CreateCategoryDTO
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select
from app.core.models import Category, Transaction
from fastapi import HTTPException
from app.api.utils.responses import DatabaseError
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
        print(user_categories)

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
        return []
    
