import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.models import Base
from app.main import app
from app.core.db_dependency import get_db
from app.api.auth_service.auth import create_token, hash_pass
from app.core.models import User
from datetime import timedelta

# Create a test database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create the database tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TestTransactionEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = client
        self.username = "testuser"
        self.password = "testpassword"
        self.db = TestingSessionLocal()

        # Create a test user
        test_user = User(username=self.username, password=hash_pass(self.password))
        self.db.add(test_user)
        self.db.commit()

        # Generate a valid token
        self.token = self.get_valid_token(self.username)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        # Clean up actions after each test can be done here
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()

    def get_valid_token(self, username: str) -> str:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_token(data={"sub": username}, expires_delta=access_token_expires)

    def test_make_draft_transaction(self):
        response = self.client.post(
            "/transactions/draft",
            json={
                "receiver_account": "receiver123",
                "amount": 100.0,
                "category_id": 1,
                "description": "Test transaction",
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            "You are about to send 100.0 to receiver123", response.json()["message"]
        )

    def test_edit_draft_transaction(self):
        # First create a draft transaction
        create_response = self.client.post(
            "/transactions/draft",
            json={
                "receiver_account": "receiver123",
                "amount": 100.0,
                "category_id": 1,
                "description": "Test transaction",
            },
            headers=self.headers,
        )
        draft_id = (
            create_response.json()["message"].split("[Draft ID: ")[1].split("]")[0]
        )

        # Edit the created draft transaction
        response = self.client.put(
            f"/transactions/{draft_id}",
            json={
                "receiver_account": "receiver456",
                "amount": 150.0,
                "category_id": 2,
                "description": "Updated transaction",
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("You've successfully edited Draft ID", response.json()["message"])

    def test_confirm_transaction(self):
        # First create a draft transaction
        create_response = self.client.post(
            "/transactions/draft",
            json={
                "receiver_account": "receiver123",
                "amount": 100.0,
                "category_id": 1,
                "description": "Test transaction",
            },
            headers=self.headers,
        )
        draft_id = (
            create_response.json()["message"].split("[Draft ID: ")[1].split("]")[0]
        )

        # Confirm the created draft transaction
        response = self.client.post(
            f"/transactions/{draft_id}/confirm", headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Your transfer to receiver123 is pending", response.json()["message"]
        )


if __name__ == "__main__":
    unittest.main()


# import asyncio
# import unittest
# from urllib import response
# from sqlalchemy.orm import sessionmaker
# from unittest.mock import patch, Mock, MagicMock, create_autospec
# from fastapi.testclient import TestClient
# from app.main import app
# from app.api.auth_service.auth import authenticate_user
# from app.api.routes.users.schemas import UserDTO, UpdateUserDTO, UserViewDTO
# from app.core.models import Transaction
# from app.api.routes.transactions.schemas import TransactionDTO
# from app.api.routes.transactions.router import (
#     confirm_transaction,
#     make_draft_transaction,
# )


# client = TestClient(app)


# def fake_transaction():
#     transaction = Transaction(
#         sender_account="test_sender",
#         receiver_account="test_receiver",
#         amount=11.20,
#         category_id=1,
#         description="test_description",
#         transaction_date=None,
#         status="draft",
#         is_recurring=False,
#         recurring_interval=None,
#         is_flagged=False,
#     )
#     transaction.id = 2
#     return transaction


# def fake_pending_transaction():
#     transaction = Transaction(
#         sender_account="test_sender",
#         receiver_account="receiver_test",
#         amount=11.20,
#         category_id=1,
#         description="test_description",
#         transaction_date=None,
#         status="pending",
#         is_recurring=False,
#         recurring_interval=None,
#         is_flagged=False,
#     )
#     transaction.id = 2
#     return transaction


# def fake_transaction_dto():
#     return TransactionDTO(
#         receiver_account="test_receiver",
#         amount=11.30,
#         category_id=1,
#         description="test_description",
#     )


# Session = sessionmaker()


# def fake_db():
#     return MagicMock()


# def fake_user_view():
#     return UserViewDTO(id=1, username="testuser")


# class TransactionRouter_Should(unittest.TestCase):

#     @patch("app.core.db_dependency.get_db")
#     @patch("app.api.routes.transactions.service.create_draft_transaction")
#     @patch("app.api.auth_service.auth.get_user_or_raise_401")
#     def test_makeDraftTransaction_IsSuccessful(
#         self, mock_get_db, create_draft_transaction_mock, get_user_mock
#     ):
#         # Arrange
#         get_user_mock.return_value = fake_user_view()
#         transaction_dto = fake_transaction_dto()
#         mock_get_db.return_value = fake_db()
#         db = fake_db()
#         create_draft_transaction_mock.return_value = fake_transaction()
#         user = fake_user_view()

#         # Act
#         response = make_draft_transaction(user, transaction_dto, db)

#         # Assert
#         self.assertEqual(
#             response, "You are about to send 11.20 to test_receiver [Draft ID: 2]"
#         )

#     @patch("app.core.db_dependency.get_db")
#     @patch("app.api.routes.transactions.service.create_draft_transaction")
#     @patch("app.api.auth_service.auth.get_user_or_raise_401")
#     def test_confirmTransaction_returnsCorrectMessage(
#         self, mock_get_db, mock_confirm_draft_transaction, mock_get_user
#     ):

#         # Arrange
#         mock_get_user.return_value = fake_user_view()
#         mock_get_db.return_value = fake_db()
#         db = fake_db()
#         mock_confirm_draft_transaction.return_value = fake_pending_transaction()
#         user = fake_user_view()
#         transaction = fake_pending_transaction()
#         transaction_id = 2

#         # Act
#         response = confirm_transaction(user, transaction_id, db)

#         # Assert
#         self.assertEqual(response, "Your transfer to receiver_test is pending!")
