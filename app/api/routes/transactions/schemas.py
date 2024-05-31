from decimal import Decimal
from pydantic import BaseModel


class TransactionDTO(BaseModel):
    receiver_account: str
    amount: Decimal
    category_id: int | None = None
    description: str | None = None
