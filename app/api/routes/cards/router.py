from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from . import service
from ....core.db_dependency import get_db
from sqlalchemy.orm import Session
from ..users.schemas import UserViewDTO
from .service import create,delete
from ...auth_service import auth
from typing import Annotated
from ...utils import responses

card_router = APIRouter(prefix="/cards", tags=["Cards"])


@card_router.post("/")
def create_card(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)], db: Session = Depends(get_db)):
        created_card = create(current_user, db)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": f"New card for username {current_user.username} is created successfully."
            },
        )
         


@card_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
        id: int, 
        current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)], 
        db: Session = Depends(get_db)
        ):
        # Assumption: User's cards are shown to him in front end, so no checks for whether the card belongs to them.
        delete(id, db)
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content={
            "message": f"Your card has been deleted successfully."
            },
        )
        # To determine how to handle when card expires?


