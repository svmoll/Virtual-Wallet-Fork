from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Body, status
from fastapi.openapi.models import Response
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


@admin_router.get("/view/transactions")
def view_transactions(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
                      sender: Optional[str] = Query(None, description="Username of sender"),
                      receiver: Optional[str] = Query(None, description="Username of receiver"),
                      status: Optional[str] = Query(None, description="Status of transaction"),
                      flagged: Optional[str] = Query(None, description="Flagged transactions (Only accepts 'yes' or 'no')"),
                      sort: Optional[str] = Query(None, description="Sort order"),
                      page: Optional[int] = Query(None, description="Page Number"),
                      limit: Optional[int] = Query(None, description="Limit on page"),
                      db: Session = Depends(get_db)
                      ):

    if not service.check_is_admin(current_user.id, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    transactions = service.view_transactions(sender, receiver, status, flagged, sort, page, limit, db)

    if not transactions:
        return JSONResponse(status_code=404, content={"message": "Transactions not found"})

    return transactions

@admin_router.put("/deny/transactions")
def deny_transaction(current_user: Annotated[UserViewDTO, Depends(auth.get_user_or_raise_401)],
                     transaction_id: Optional[int] = Query(None, description="Transaction ID"),
                     db: Session = Depends(get_db)):
    if not service.check_is_admin(current_user.id, db):
        raise HTTPException(status_code=403, detail="Forbidden")

    service.deny_transaction(transaction_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


