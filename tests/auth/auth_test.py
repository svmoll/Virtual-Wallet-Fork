import unittest
from datetime import timedelta, datetime, timezone
from hashlib import sha256
from unittest.mock import MagicMock, patch, Mock

from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from app.api.utils.auth import hash_pass, authenticate_user, ALGORITHM, SECRET_KEY, create_token, decode_access_token, \
    is_authenticated, from_token, get_user_or_raise_401, blacklist_token, blacklisted_tokens, is_token_blacklisted


Session = sessionmaker()
def fake_db():
    return MagicMock(spec=Session)

class Authentication_Should(unittest.TestCase):

    def test_hashPassword_returnsCorrectHashedPassword(self):
        password = "password1"
        expected_hash = sha256(password.encode("utf-8")).hexdigest()
        self.assertEqual(hash_pass(password), expected_hash)

    def test_hashPassword_hashesDifferentPasswordsInDifferentWay(self):
        password1 = "password1"
        password2 = "password2"
        self.assertNotEqual(hash_pass(password1), hash_pass(password2))

    def test_hashPassword_hashesPasswordTheSameEveryTime(self):
        password = "password1"
        hash1 = hash_pass(password)
        hash2 = hash_pass(password)
        self.assertEqual(hash1, hash2)


    @patch('app.api.utils.auth.hash_pass')
    def test_authenticateUser_success(self,mock_hash_pass):
        db = fake_db()
        mock_user = MagicMock( )
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.password = 'hashedpassword'
        db.execute = Mock()
        db.select = Mock()

        mock_hash_pass.return_value = 'hashedpassword'
        db.select.return_value.where.return_value = 'mocked statement'
        db.execute.return_value.scalar_one.return_value = mock_user

        result = authenticate_user(db, 'testuser', 'password')

        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'testuser')
        mock_hash_pass.assert_called_once_with('password')

    @patch('app.api.utils.auth.hash_pass')
    def test_authenticateUser_failureWhenNoUserIsFound(self, mock_hash_pass):
        db = fake_db( )
        db.execute = Mock()

        mock_hash_pass.return_value = 'hashedpassword'
        db.execute.return_value.scalar_one.side_effect = NoResultFound

        result = authenticate_user(db, 'testuser', 'password')

        self.assertIsNone(result)

    def test_createToken_withExpiry(self):
        data = {'sub': 'testuser'}
        expires_delta = timedelta(minutes=5)
        result = create_token(data, expires_delta)

        decoded = jwt.decode(result, SECRET_KEY, algorithms=[ALGORITHM])

        self.assertIn('exp', decoded)
        self.assertAlmostEqual(
            decoded['exp'],
            int((datetime.now(timezone.utc) + expires_delta).timestamp( )),
            delta=1
        )

    def test_createToken_withoutExpiry(self):
        data = {'sub': 'testuser'}
        result = create_token(data)

        decoded = jwt.decode(result, SECRET_KEY, algorithms=[ALGORITHM])

        self.assertIn('exp', decoded)
        self.assertAlmostEqual(
            decoded['exp'],
            int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp( )),
            delta=1
        )

    def test_decodeAccessToken(self):
        data = {'sub': 'testuser'}
        token = create_token(data)
        result = decode_access_token(token)

        self.assertEqual(result['sub'], 'testuser')

    @patch('app.api.utils.auth.decode_access_token')
    def test_isAuthenticated_success(self, mock_decode):
        db = fake_db( )
        db.execute = Mock()
        mock_user = MagicMock( )
        mock_user.id = 1
        mock_user.username = 'testuser'

        mock_decode.return_value = {'sub': 'testuser', 'exp': datetime.now(timezone.utc).timestamp( )}
        db.execute.return_value.scalar_one.return_value = mock_user

        result = is_authenticated(db, 'token')

        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'testuser')

    @patch('app.api.utils.auth.decode_access_token')
    def test_isAuthenticated_failureWhenUserNotFound(self, mock_decode):
        db = fake_db( )
        db.execute = Mock()

        mock_decode.return_value = {'sub': 'testuser', 'exp': datetime.now(timezone.utc).timestamp( )}
        db.execute.return_value.scalar_one.side_effect = NoResultFound

        with self.assertRaises(HTTPException) as context:
            is_authenticated(db, 'token')

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Please log in to proceed")

    @patch('app.api.utils.auth.decode_access_token')
    def test_fromToken_success(self, mock_decode):
        db = fake_db( )
        db.execute = Mock()
        mock_user = MagicMock( )
        mock_user.id = 1
        mock_user.username = 'testuser'

        mock_decode.return_value = {'sub': 'testuser', 'exp': datetime.now(timezone.utc).timestamp( )}
        db.execute.return_value.scalar_one.return_value = mock_user

        result = from_token(db, 'token')

        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'testuser')

    @patch('app.api.utils.auth.decode_access_token')
    def test_fromToken_failureWhenNotFound(self, mock_decode):
        db = fake_db( )
        db.execute = Mock()

        mock_decode.return_value = {'sub': 'testuser', 'exp': datetime.now(timezone.utc).timestamp( )}
        db.execute.return_value.scalar_one.side_effect = NoResultFound

        result = from_token(db, 'token')

        self.assertIsNone(result)

    @patch('app.api.utils.auth.is_token_blacklisted')
    @patch('app.api.utils.auth.is_authenticated')
    @patch('app.api.utils.auth.from_token')
    def test_getUserOrRaise401_success(self, mock_from_token, mock_is_authenticated, mock_is_token_blacklisted):
        db = fake_db()
        mock_is_token_blacklisted.return_value = False
        mock_is_authenticated.return_value = MagicMock()
        mock_from_token.return_value = MagicMock()

        token = 'valid_token'

        result = get_user_or_raise_401(db, token)

        mock_is_token_blacklisted.assert_called_once_with(token)
        mock_is_authenticated.assert_called_once_with(db, token)
        mock_from_token.assert_called_once_with(db, token)
        self.assertIsNotNone(result)

    @patch('app.api.utils.auth.is_token_blacklisted')
    @patch('app.api.utils.auth.is_authenticated')
    @patch('app.api.utils.auth.from_token')
    def test_getUserOrRaise401_userDoesntExist(self, mock_from_token, mock_is_authenticated,
                                                     mock_is_token_blacklisted):
        db = fake_db( )
        mock_is_token_blacklisted.return_value = False
        mock_is_authenticated.side_effect = HTTPException(status_code=401, detail="User doesn't exist")
        mock_from_token.return_value = None

        token = 'invalid_token'

        with self.assertRaises(HTTPException) as context:
            get_user_or_raise_401(db, token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "User doesn't exist")
        mock_is_token_blacklisted.assert_called_once_with(token)
        mock_is_authenticated.assert_called_once_with(db, token)
        mock_from_token.assert_not_called( )

    @patch('app.api.utils.auth.is_token_blacklisted')
    @patch('app.api.utils.auth.is_authenticated')
    @patch('app.api.utils.auth.from_token')
    def test_getUserOrRaise401_invalidToken(self, mock_from_token, mock_is_authenticated, mock_is_token_blacklisted):
        db = fake_db()
        mock_is_token_blacklisted.return_value = False
        mock_is_authenticated.side_effect = JWTError("Invalid token")
        mock_from_token.return_value = None

        token = 'invalid_token'

        with self.assertRaises(HTTPException) as context:
            get_user_or_raise_401(db, token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid token")
        mock_is_token_blacklisted.assert_called_once_with(token)
        mock_is_authenticated.assert_called_once_with(db, token)
        mock_from_token.assert_not_called()

    @patch('app.api.utils.auth.is_token_blacklisted')
    def test_getUserOrRaise401_blacklistedToken(self, mock_is_token_blacklisted):
        mock_is_token_blacklisted.return_value = True

        token = 'blacklisted_token'
        session = MagicMock( )

        with self.assertRaises(HTTPException) as context:
            get_user_or_raise_401(session, token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "You Are logged out, please log in again to proceed")

    def test_blacklistToken(self):
        token = 'token_to_blacklist'
        blacklist_token(token)
        self.assertIn(token, blacklisted_tokens)

    def test_isTokenBlacklisted(self):
        token = 'blacklisted_token'
        blacklisted_tokens.add(token)
        self.assertTrue(is_token_blacklisted(token))

        non_blacklisted_token = 'non_blacklisted_token'
        self.assertFalse(is_token_blacklisted(non_blacklisted_token))