# import unittest
# from unittest.mock import patch, MagicMock
# from sqlalchemy.orm import Session
# from app.api.models.models import User  # Import only User for simplicity
# from app.core.database import engine

# class DataLoad_Should(unittest.TestCase):

#     @patch('core.database.engine', autospec=True)
#     def test_addUsers_to_database(self, mock_engine):
#         with patch('core.database.engine') as engine:
#         # Arrange (Mocking)
#         mock_session = MagicMock(spec=Session)
#         mock_engine.Session.return_value = engine ####

#         # Act
#         admin = User(username="admin", password="adminADMIN123", email="admin@admin.com", phone_number="0888111111")
#         user = User(username="user", password="userUSER123", email="user@user.com", phone_number="0888222222")
#         users_to_load = [admin, user]

#         with Session(engine) as session:
#             session.add_all(users_to_load)
#             session.commit()
#             session.refresh(users_to_load)

#         # Assertions
#         mock_session.add_all.assert_called_once_with(users_to_load)
#         mock_session.commit.assert_called_once()
#         mock_session.refresh.assert_called_once_with(users_to_load)

#     @patch('core.database.engine', autospec=True)
#     def test_session_operations(self, mock_engine):
#         # Arrange (Mocking)
#         mock_session = MagicMock(spec=Session)
#         mock_engine.Session.return_value = mock_session

#         # Act
#         admin = User(username="admin", password="adminADMIN123", email="admin@admin.com", phone_number="0888111111")
#         user = User(username="user", password="userUSER123", email="user@user.com", phone_number="0888222222")
#         users_to_load = [admin, user]

#         with Session(engine) as session:
#             session.add_all(users_to_load)
#             session.commit()
#             session.refresh(users_to_load)

#         # Assert
#         mock_engine.Session.assert_called_once()
#         mock_session.add_all.assert_called_once_with(users_to_load)
#         mock_session.commit.assert_called_once()
#         mock_session.refresh.assert_called_once_with(users_to_load)


