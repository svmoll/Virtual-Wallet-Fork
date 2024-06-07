from .schemas import CategoryDTO
from sqlalchemy.orm import Session
from app.core.models import Category, Transaction
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.api.utils.responses import BadRequest
import logging

def create(category: CategoryDTO, db: Session):
    
    try:
        if category_exists(category, db):
            raise HTTPException(
                status_code=400, 
                detail="Category already exists. Please use the existing one or try a different name."
                )
        else:
            category = CategoryDTO(
                id=category.id,
                name=category.name, 
                color_hex=category.color_hex
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


def category_exists(category, db):
    category = db.query(Category).filter(Category.name == category.name).first()
    return True if category else False

def get_categories(user,db):
    # user_categories = db.query(Transaction).filter_by(Transaction.sender_account == user.username).all()
    # # select distinct category_id 
    # # where transaction.sender_account == user.username
    pass
    