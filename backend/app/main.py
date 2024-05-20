from fastapi import FastAPI
from core.database import engine
from api.models import models
from api.routes.categories.router import category_router
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(category_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000)
