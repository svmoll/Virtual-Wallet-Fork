from fastapi import APIRouter, Depends, HTTPException
from . import service
from core.db_dependency import get_db
from sqlalchemy.orm import Session
from .schemas import CardDTO
from ..users.schemas import UserViewDTO
from .service import create, delete
from ...auth_service import auth
from typing import Annotated
from ...utils import responses

card_router = APIRouter(prefix="/cards", tags=["Cards"])


@card_router.post("/")
def create_card(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)], db: Session = Depends(get_db)):
    created_card = service.create(current_user, db)

    return f"New card for username {current_user.username} is created successfully."



@card_router.delete("/")
def delete_card(card: CardDTO, current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)], db: Session = Depends(get_db)):
    try:
        current_user.id == card.account_id
        service.delete(current_user, db)
        return f"Your card with numbers {card.card_number} is deleted successfully."
    except: 
        raise responses.Forbidden

