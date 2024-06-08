from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.db_dependency import get_db
from sqlalchemy.orm import Session
from ..users.schemas import UserViewDTO
from ...auth_service import auth
from .schemas import CreateCategoryDTO
from fastapi.responses import JSONResponse, Response
from app.api.utils.responses import BadRequest
from .service import create, get_categories, generate_report
from datetime import date
import logging


category_router = APIRouter(prefix="/categories", tags=["Categories"])


@category_router.post("/")
def create_category(
    category: CreateCategoryDTO,
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db)
):
    created_category = create(category, db)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": f"{created_category.name} category is created successfully"
        }
    )


@category_router.get("/list")
def get_user_categories(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db)
):
    categories_list = get_categories(current_user,db)

    if not categories_list:
        return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"There are no associated categories with your username: {current_user.username}."
                },
            )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"This is your list of categories:",
                "categories": categories_list
            }
        )
    

@category_router.get("/report")
def create_user_report(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db),
    from_date: date = '2024-01-01',
    to_date: date = '2024-07-01'
    ):
    generated_report = generate_report(current_user, db, from_date, to_date)
    
    logging.info(f'Generated report: {generated_report}')
    
    if generated_report:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": f"Your expenses are summarised in the graph."
            }
        )
    # else:
    #     return JSONResponse(
    #         status_code=status.HTTP_204_NO_CONTENT,
    #         content={
    #             "message": f"Report could not be generated."
    #         }
    #     )