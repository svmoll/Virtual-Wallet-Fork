from hashlib import sha256


def hash_pass(password):
    hashed_password = sha256(password.encode("utf-8")).hexdigest()
    return hashed_password
