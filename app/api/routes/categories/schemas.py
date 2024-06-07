from pydantic import BaseModel


class CreateCategoryDTO(BaseModel):
    name: str
