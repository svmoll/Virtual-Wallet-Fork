from pydantic import BaseModel


class CategoryDTO(BaseModel):
    id: int | None = None
    name: str
    color_hex: str | None = None
