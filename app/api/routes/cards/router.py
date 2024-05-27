from fastapi import APIRouter, Depends
from . import service
from core.db_dependency import get_db
from sqlalchemy.orm import Session
from .schemas import CardDTO
from ..users.schemas import UserViewDTO
from .service import create
from ...auth_service import auth
from typing import Annotated

card_router = APIRouter(prefix="/cards", tags=["Cards"])


@card_router.post("/")
def create_card(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)], db: Session = Depends(get_db)):
    created_card = service.create(current_user, db)

    return f"New card for username {current_user.username} is created successfully."

