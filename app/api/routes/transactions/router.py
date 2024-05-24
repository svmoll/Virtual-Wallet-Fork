from typing import Annotated
from fastapi import APIRouter, Depends
from core.db_dependency import get_db
from .schemas import TransactionDTO
from sqlalchemy.orm import Session
from .service import create_transaction as ct
from ..users.schemas import UserViewDTO
from ...auth_service import auth


transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])
