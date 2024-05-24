from pydantic import BaseModel


class TransactionDTO(BaseModel):
    receiver_account: str
    amount: float
    category_id: int | None = None
    description: str | None = None
