from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.db_dependency import get_db
from sqlalchemy.orm import Session
from .service import create
from ..users.schemas import UserViewDTO
from ...auth_service import auth
from .schemas import CategoryDTO
from fastapi.responses import JSONResponse, Response
from app.api.utils.responses import BadRequest


category_router = APIRouter(prefix="/categories", tags=["Category"])


@category_router.post("/")
def create_category(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    category: CategoryDTO,
    db: Session = Depends(get_db),
):
    #if no categories_exists,
    created_category = create(category, db)
    # else
    #     raise BadRequest()
    #exceptions handling

    if created_category:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": f"{created_category.name} category is created successfully"
            },
        )
