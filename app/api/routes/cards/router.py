from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from . import service
from ....core.db_dependency import get_db
from sqlalchemy.orm import Session
from .schemas import CardDTO
from ..users.schemas import UserDTO
from .service import create
from ...auth_service import auth
from typing import Annotated
from ...utils import responses

card_router = APIRouter(prefix="/cards", tags=["Cards"])


@card_router.post("/")
def create_card(current_user: Annotated[UserDTO, Depends(auth.get_user_or_raise_401)], db: Session = Depends(get_db)):
    created_card = service.create(current_user, db)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": f"New card for username {current_user.username} is created successfully."
        },
    )


