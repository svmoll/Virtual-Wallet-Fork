from .schemas import CategoryDTO
from sqlalchemy.orm import Session
from ...models.models import Category


def create_category(category: CategoryDTO, db: Session):
    category = Category(name=category.name, color_hex=category.color_hex)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
