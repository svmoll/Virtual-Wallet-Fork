import unittest
from hashlib import sha256

from app.api.utils.auth import hash_pass


class HashPassword_Should(unittest.TestCase):

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