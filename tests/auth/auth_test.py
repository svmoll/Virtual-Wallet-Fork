import unittest
from datetime import timedelta, datetime, timezone
from hashlib import sha256
from unittest.mock import MagicMock, patch, Mock

from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from app.api.auth_service.auth import hash_pass, authenticate_user, ALGORITHM, SECRET_KEY, create_token, decode_access_token, \
    is_authenticated, from_token, get_user_or_raise_401, blacklist_token, blacklisted_tokens, is_token_blacklisted


Session = sessionmaker()
def fake_db():
    return MagicMock(spec=Session)

class Authentication_Should(unittest.TestCase):

    def test_hashPassword_returnsCorrectHashedPassword(self):
        # Arrange
        password = "password1"

        # Act
        expected_hash = sha256(password.encode("utf-8")).hexdigest()

        # Assert
        self.assertEqual(hash_pass(password), expected_hash)

    def test_hashPassword_hashesDifferentPasswordsInDifferentWay(self):
        # Arrange
        password1 = "password1"
        password2 = "password2"

        # Assert
        self.assertNotEqual(hash_pass(password1), hash_pass(password2))

    def test_hashPassword_hashesPasswordTheSameEveryTime(self):
        # Arrange
        password = "password1"

        # Act
        hash1 = hash_pass(password)
        hash2 = hash_pass(password)

        # Assert
        self.assertEqual(hash1, hash2)


    @patch('app.api.auth_service.auth.hash_pass')
    def test_authenticateUser_success(self,mock_hash_pass):
        #Arrange
        db = fake_db()
        mock_user = MagicMock( )
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.password = 'hashedpassword'
        db.execute = Mock()
        db.select = Mock()
        db.select.where = Mock()
        mock_hash_pass.return_value = 'hashedpassword'
        db.select.return_value.where.return_value = 'mocked statement'
        db.execute.return_value.scalar_one.return_value = mock_user

        # Act
        result = authenticate_user(db, 'testuser', 'password')

        # Assert
        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'testuser')
        mock_hash_pass.assert_called_once_with('password')

    @patch('app.api.auth_service.auth.hash_pass')
    def test_authenticateUser_failureWhenNoUserIsFound(self, mock_hash_pass):
        #Arrange
        db = fake_db( )
        db.execute = Mock()
        mock_hash_pass.return_value = 'hashedpassword'
        db.execute.return_value.scalar_one.side_effect = NoResultFound

        # Act
        result = authenticate_user(db, 'testuser', 'password')

        # Assert
        self.assertIsNone(result)

    def test_createToken_withExpiry(self):
        # Arrange
        data = {'sub': 'testuser'}
        expires_delta = timedelta(minutes=5)
        result = create_token(data, expires_delta)

        # Act
        decoded = jwt.decode(result, SECRET_KEY, algorithms=[ALGORITHM])

        # Assert
        self.assertIn('exp', decoded)
        self.assertAlmostEqual(
            decoded['exp'],
            int((datetime.now(timezone.utc) + expires_delta).timestamp( )),
            delta=1
        )

    def test_createToken_withoutExpiry(self):
        # Arrange
        data = {'sub': 'testuser'}
        result = create_token(data)

        # Act
        decoded = jwt.decode(result, SECRET_KEY, algorithms=[ALGORITHM])

        # Assert
        self.assertIn('exp', decoded)
        self.assertAlmostEqual(
            decoded['exp'],
            int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp( )),
            delta=1
        )

    def test_decodeAccessToken(self):
        # Arrange
        data = {'sub': 'testuser'}
        token = create_token(data)

        # Act
        result = decode_access_token(token)

        # Assert
        self.assertEqual(result['sub'], 'testuser')

    @patch('app.api.auth_service.auth.decode_access_token')
    def test_isAuthenticated_success(self, mock_decode):
        # Arrange
        db = fake_db( )
        db.execute = Mock()
        mock_user = MagicMock( )
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_decode.return_value = {'sub': 'testuser', 'exp': datetime.now(timezone.utc).timestamp( )}
        db.execute.return_value.scalar_one.return_value = mock_user

        # Act
        result = is_authenticated(db, 'token')

        # Assert
        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'testuser')

    @patch('app.api.auth_service.auth.decode_access_token')
    def test_isAuthenticated_failureWhenUserNotFound(self, mock_decode):
        # Arrange
        db = fake_db( )
        db.execute = Mock()
        mock_decode.return_value = {'sub': 'testuser', 'exp': datetime.now(timezone.utc).timestamp( )}
        db.execute.return_value.scalar_one.side_effect = NoResultFound

        # Assert
        with self.assertRaises(HTTPException) as context:
            is_authenticated(db, 'token')
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Please log in to proceed")

    @patch('app.api.auth_service.auth.decode_access_token')
    def test_fromToken_success(self, mock_decode):
        # Arrange
        db = fake_db( )
        db.execute = Mock()
        mock_user = MagicMock( )
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_decode.return_value = {'sub': 'testuser', 'exp': datetime.now(timezone.utc).timestamp( )}
        db.execute.return_value.scalar_one.return_value = mock_user

        # Act
        result = from_token(db, 'token')

        # Assert
        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'testuser')

    @patch('app.api.auth_service.auth.decode_access_token')
    def test_fromToken_failureWhenNotFound(self, mock_decode):
        # Arrange
        db = fake_db( )
        db.execute = Mock()
        mock_decode.return_value = {'sub': 'testuser', 'exp': datetime.now(timezone.utc).timestamp( )}
        db.execute.return_value.scalar_one.side_effect = NoResultFound

        # Act
        result = from_token(db, 'token')

        # Assert
        self.assertIsNone(result)

    @patch('app.api.auth_service.auth.is_restricted')
    @patch('app.api.auth_service.auth.is_token_blacklisted')
    @patch('app.api.auth_service.auth.is_authenticated')
    @patch('app.api.auth_service.auth.from_token')
    def test_getUserOrRaise401_success(self, mock_from_token, mock_is_authenticated, mock_is_token_blacklisted,
                                       mock_is_restricted):
        # Arrange
        db = fake_db()
        mock_is_restricted.return_value = False
        mock_is_token_blacklisted.return_value = False
        mock_is_authenticated.return_value = MagicMock()
        mock_from_token.return_value = MagicMock()
        token = 'valid_token'

        # Assert
        result = get_user_or_raise_401(token, db)
        mock_is_token_blacklisted.assert_called_once_with(token)
        mock_is_authenticated.assert_called_once_with(db, token)
        self.assertIsNotNone(result)

    @patch('app.api.auth_service.auth.is_restricted')
    @patch('app.api.auth_service.auth.is_token_blacklisted')
    @patch('app.api.auth_service.auth.is_authenticated')
    @patch('app.api.auth_service.auth.from_token')
    def test_getUserOrRaise401_userDoesntExist(self, mock_from_token, mock_is_authenticated,
                                                     mock_is_token_blacklisted, mock_is_restricted):
        # Arrange
        db = fake_db( )
        mock_is_restricted.return_value = False
        mock_is_token_blacklisted.return_value = False
        mock_is_authenticated.side_effect = HTTPException(status_code=401, detail="User doesn't exist")
        mock_from_token.return_value = None
        token = 'invalid_token'

        # Assert
        with self.assertRaises(HTTPException) as context:
            get_user_or_raise_401(token, db)
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "User doesn't exist")
        mock_is_token_blacklisted.assert_called_once_with(token)
        mock_is_authenticated.assert_called_once_with(db, token)

    @patch('app.api.auth_service.auth.is_restricted')
    @patch('app.api.auth_service.auth.is_token_blacklisted')
    @patch('app.api.auth_service.auth.is_authenticated')
    @patch('app.api.auth_service.auth.from_token')
    def test_getUserOrRaise401_invalidToken(self, mock_from_token, mock_is_authenticated, mock_is_token_blacklisted, mock_is_restricted):
        # Arrange
        db = fake_db()
        mock_is_restricted.return_value = False
        mock_is_token_blacklisted.return_value = False
        mock_is_authenticated.side_effect = JWTError("Invalid token")
        mock_from_token.return_value = None
        token = 'invalid_token'

        # Assert
        with self.assertRaises(HTTPException) as context:
            get_user_or_raise_401(token, db)
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid token")
        mock_is_token_blacklisted.assert_called_once_with(token)
        mock_is_authenticated.assert_called_once_with(db, token)

    @patch('app.api.auth_service.auth.is_token_blacklisted')
    def test_getUserOrRaise401_blacklistedToken(self, mock_is_token_blacklisted):
        # Arrange
        mock_is_token_blacklisted.return_value = True
        token = 'blacklisted_token'
        session = MagicMock( )

        # Assert
        with self.assertRaises(HTTPException) as context:
            get_user_or_raise_401(token, session)
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "You Are logged out, please log in again to proceed")

    def test_blacklistToken(self):
        # Arrange
        token = 'token_to_blacklist'

        # Act
        blacklist_token(token)

        # Assert
        self.assertIn(token, blacklisted_tokens)

    def test_isTokenBlacklisted(self):
        # Arrange
        token = 'blacklisted_token'

        # Act
        blacklisted_tokens.add(token)

        # Assert
        self.assertTrue(is_token_blacklisted(token))
        non_blacklisted_token = 'non_blacklisted_token'
        self.assertFalse(is_token_blacklisted(non_blacklisted_token))