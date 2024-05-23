from typing import Annotated

from fastapi import APIRouter, Depends
from app.core.db_dependency import get_db
from .schemas import CategoryDTO
from sqlalchemy.orm import Session
from .service import create_category as cs
from ..users.schemas import UserViewDTO
from ...auth_service import auth

# from .service import CategoryService


category_router = APIRouter(prefix="/categories", tags=["Category"])


@category_router.post("/")
def create_category(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)], category: CategoryDTO, db: Session = Depends(get_db)):
    created_category = cs(category, db)

    return {"message": "Category created successfully", "category": created_category}
