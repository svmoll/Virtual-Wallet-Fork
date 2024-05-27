from pydantic import BaseModel, StringConstraints
from typing import Annotated
from datetime import date


class CardDTO(BaseModel):
    id: int | None = None
    account_id: int
    card_number: str
    expiration_date: date 
    card_holder: str 
    cvv: str
    design_path: str | None = None
