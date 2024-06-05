from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes.home.router import home_router
from app.core.database import engine
from app.core.db_dependency import get_db
from app.core import models
from app.core.db_population import initialize_special_accounts
from app.api.routes.categories.router import category_router
from app.api.routes.users.router import user_router
from app.api.routes.transactions.router import transaction_router
from app.api.routes.cards.router import card_router
from app.api.routes.accounts.router import account_router
from app.api.routes.admin.router import admin_router
import uvicorn
import logging


# Basic configuration
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Log to the console
        # You can add more handlers here (e.g., logging to a file)
    ],
)

logger = logging.getLogger(__name__)  # Create a logger for this module


models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize special accounts during application startup
    db_gen = get_db()
    db = next(db_gen)
    try:
        initialize_special_accounts(db)
    finally:
        db_gen.close()

    yield  # Control is passed to the application

    # Shutdown logic if needed
    # No specific shutdown logic in this case


# Initialize the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

app.include_router(category_router)
app.include_router(user_router)
app.include_router(transaction_router)
app.include_router(home_router)
app.include_router(card_router)
app.include_router(account_router)
app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
