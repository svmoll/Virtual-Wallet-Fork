from pydantic import BaseModel
from datetime import date


class CardDTO(BaseModel):
    id: int | None = None
    account_id: int
    card_number: str
    expiration_date: date
    card_holder: str 
    cvv: str
    design_path: str | None = None


class DeleteCardDTO(BaseModel):
    id: int | None = None
    account_id: int
    card_number: str


class CardViewDTO(BaseModel):
    card_number: str
    expiration_date: date
    cvv: str
