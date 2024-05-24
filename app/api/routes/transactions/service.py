from .schemas import TransactionDTO
from sqlalchemy.orm import Session
from core.models import Transaction


def create_draft_transaction():
    raise NotImplementedError
