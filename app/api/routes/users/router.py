from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from . import service
from app.core.db_dependency import get_db
from sqlalchemy.orm import Session
from .schemas import UserDTO, UserViewDTO, UpdateUserDTO, UserShowDTO
from ...auth_service import auth
from fastapi.responses import JSONResponse, Response


user_router = APIRouter(prefix="/users", tags=["Users"])


class Token(BaseModel):
    access_token: str
    token_type: str


@user_router.post("/register")
async def register_user(user: UserDTO  = Body(..., example={
        "username": "johndoe",
        "password": "Password1!!",
        "email": "johndoe@example.com",
        "phone_number": "5555555555",
        "fullname": "John Doe"
    }), db: Session = Depends(get_db)):
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


@user_router.get("/logout")
async def logout(token: Annotated[str, Depends(auth.get_token)]):
    auth.blacklist_token(token)
    return {"msg": "Successfully logged out"}


@user_router.get("/view", response_model=UserShowDTO)
def view(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db),
):
    user = service.get_user(current_user.id, db)
    return user


@user_router.put("/update")
def update(
    update_info: UpdateUserDTO,
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    db: Session = Depends(get_db),
):
    updated_user = service.update_user(current_user.id, update_info, db)

    return f"User {updated_user.username} updated profile successfully."

@user_router.get("/search")
def search(
    current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    username: Optional[str] = Query(None, description="Find by username"),
    email: Optional[str] = Query(None, description="Find by email"),
    phone_number: Optional[str] = Query(None, description="Find by phone number"),
    db: Session = Depends(get_db)
):
    if username is None and email is None and phone_number is None:
        raise HTTPException(status_code=400, detail="Username or Email or Phone Number is required for search")
    user = service.search_user(username, email, phone_number, db)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"username": user.username, "email": user.email,
        },
    )

@user_router.post("/contacts")
def add_contact(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
                username: Optional[str] = Body(None, description="Username to add"),
                db: Session = Depends(get_db)):

    if username is None:
        raise HTTPException(status_code=400, detail="Username should not be empty")

    create_contact = service.create_contact(username, current_user.username, db)
    if create_contact:
        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail":"Successfully added new contact"
        },
    )

@user_router.delete("/contacts")
def delete_contact(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
                   username: Optional[str] = Body(None, description="Username to delete"),
                   db: Session = Depends(get_db)):

    if username is None:
        raise HTTPException(status_code=400, detail="Username should not be empty")

    delete_success = service.delete_contact(username, current_user.username, db)
    if delete_success:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

@user_router.get("/view/contacts")
def view_contacts(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
                  page: Optional[int] = Query(None, description="Page Number"),
                  limit: Optional[int] = Query(None, description="Limit on page"),
                   db: Session = Depends(get_db)):

    contacts = service.view(current_user.username, page, limit, db)
    if len(contacts) < 1:
        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail":"No contacts found"
        }
    )
    return contacts

