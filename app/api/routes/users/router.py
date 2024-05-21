from fastapi import APIRouter, Depends
from . import service
from ...utils.db_dependency import get_db
from sqlalchemy.orm import Session
from .schemas import UserDTO

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/register")
async def register_user(user: UserDTO, db: Session = Depends(get_db)):
    created_user = service.create(user, db)

    return f"User {created_user.username} created successfully."