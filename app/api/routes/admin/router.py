from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from starlette.responses import JSONResponse

from app.api.auth_service import auth
from app.api.routes.admin import service
from app.api.routes.users.schemas import UserViewDTO
from app.core.db_dependency import get_db
from sqlalchemy.orm import Session



admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.get("/search/users")
def search_users(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
    username: Optional[str] = Query(None, description="Find by username"),
    email: Optional[str] = Query(None, description="Find by email"),
    phone_number: Optional[str] = Query(None, description="Find by phone number"),
    page: Optional[int] = Query(None, description="Page Number"),
    limit: Optional[int] = Query(None, description="Limit on page"),
    db: Session = Depends(get_db)
):
    if not service.check_is_admin(current_user.id, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    users = service.search_user(username, email, phone_number, page, limit, db)

    return users

@admin_router.put("/status")
def change_status(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
                    username: Optional[str] = Body(None, description="Username to delete"),
                    db: Session = Depends(get_db)):
    if not service.check_is_admin(current_user.id, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    status = service.status(username, db)

    return JSONResponse(status_code=200, content={"action": status})