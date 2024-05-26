from fastapi import FastAPI
from app.core.database import engine
from app.core import models
from api.routes.categories.router import category_router
from api.routes.users.router import user_router
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(category_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000)
