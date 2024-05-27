from fastapi import APIRouter


home_router = APIRouter(tags=["Home"])


@home_router.get("/")
def home():
    return "Welcome to Virtual Wallet, please login to your account or register to be able to use the app"