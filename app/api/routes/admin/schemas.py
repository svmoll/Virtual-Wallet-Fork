from datetime import datetime

from pydantic import BaseModel


class UsersfrimlistDTO(BaseModel):
    username: str
    email: str
    password: str

class TransactionViewDTO(BaseModel):
    id: int
    sender: str
    receiver: str
    amount: int
    category: str | None = None
    description: str | None = None
    transaction_date: datetime | None = None
    status: str
    is_flagged: bool
    type: str