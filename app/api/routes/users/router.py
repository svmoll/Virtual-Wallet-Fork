from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from . import service
from core.db_dependency import get_db
from sqlalchemy.orm import Session
from .schemas import UserDTO, UserViewDTO
from ...auth_service import auth


user_router = APIRouter(prefix="/users", tags=["Users"])


class Token(BaseModel):
    access_token: str
    token_type: str


@user_router.post("/register")
async def register_user(user: UserDTO, db: Session = Depends(get_db)):
    created_user = service.create(user, db)

    return f"User {created_user.username} created successfully."


@user_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_token(
        data={form_data.username: form_data.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/logout", response_model=None)
async def logout(token: Annotated[str, Depends(auth.get_token)]):
    auth.blacklisted_tokens.clear()
    auth.blacklist_token(token)
    return {"msg": "Successfully logged out"}


@user_router.get("/me", response_model=None)
async def read_users_me(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
):
    return current_user
