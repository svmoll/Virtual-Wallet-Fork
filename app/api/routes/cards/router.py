from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from . import service
from ....core.db_dependency import get_db
from sqlalchemy.orm import Session
from ..users.schemas import UserViewDTO
from .service import create, delete, get_card_by_id, get_view, get_account_by_username
from ...auth_service import auth
from typing import Annotated
from ...utils import responses

card_router = APIRouter(prefix="/cards", tags=["Cards"])


@card_router.post("/")
def create_card(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db),
):

    create(current_user, db)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": f"New card for username: {current_user.username} is created successfully."
        },
    )

@card_router.get("/")
def view_cards(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)], 
    db: Session = Depends(get_db)
    ):
        
    cards = get_view(current_user, db)

    if not cards:
        return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"There are no associated cards with your username: {current_user.username}."
                },
            )
    else:
        return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"The following cards are associated with username: {current_user.username}.",
                    "cards": cards
                },
            )


@card_router.delete("/{id}")
def delete_card(
    id: int,
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db),
):
# To determine how to handle when card expires?
    existing_card = get_card_by_id(id, db)

    account_id = get_account_by_username(current_user.username,db)

    if existing_card.account_id == account_id:
        delete(id, db)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"Your card with number: {existing_card.card_number} has been deleted successfully."
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": f"Card with ID of {id} does not belong to username: {current_user.username}. "
            },
        )


