from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from ....core.db_dependency import get_db
from ..users.schemas import UserDTO
from app.core.models import Card, User
from datetime import timedelta, date
from hashlib import sha256, sha1
import random
import string


def create_card_number():
    digits = string.digits 
    random_card_number = ''.join(random.choice(digits) for _ in range(16)) # random.randint(0,9)
    formatted_card_number = '-'.join(random_card_number[i:i+4] for i in range(0, 16, 4))
    return formatted_card_number


def unique_card_number(db: Session):
    card_number = create_card_number()
    while db.query(Card).filter_by(card_number=card_number).first() is not None:
        card_number = create_card_number()
    return card_number


def create_expiration_date():
    return date.today() + timedelta(days=1826)


def create_cvv_number():
    digits = string.digits 
    random_cvv = ''.join(random.choice(digits) for _ in range(3))
    hashed_cvv = hash_cvv(random_cvv)
    return hashed_cvv


def hash_cvv(random_cvv):
    hashed_cvv = sha1(random_cvv.encode("utf-8")).hexdigest()
    return hashed_cvv


def get_user_fullname(current_user, db: Session):
    user = db.query(User).filter_by(username=current_user.username).first()
    return user


def create(current_user: UserDTO, db: Session):
    expiration_date = create_expiration_date()
    card_number = unique_card_number(db)
    cvv_number = create_cvv_number()
    user = get_user_fullname(current_user, db)

    new_card = Card(
        account_id=current_user.id,
        card_number=card_number,
        expiration_date=expiration_date,
        card_holder=user.fullname,
        cvv=cvv_number,
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


def get_card_by_id(id:int, db: Session) -> Card:
    card = db.query(Card).filter_by(id=id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found!")

    return card

def delete(id:int, db: Session):
    card_to_delete = get_card_by_id(id, db)

    db.delete(card_to_delete)
    db.commit()
    

#improving encryption using AES
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.primitives import padding
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from cryptography.hazmat.primitives import hashes
# import base64
# import os

# # Generate a secure random key for AES encryption
# def generate_aes_key():
#     return os.urandom(32)  # 256-bit key for AES-256

# # Encrypt CVV using AES and encode result in Base64
# def encrypt_cvv(cvv: str, key: bytes) -> str:
#     # Convert CVV to bytes
#     cvv_bytes = cvv.encode('utf-8')
    
#     # Generate a random IV (Initialization Vector)
#     iv = os.urandom(16)
    
#     # Initialize AES cipher with CBC mode
#     cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
#     encryptor = cipher.encryptor()
    
#     # Pad the CVV bytes to match block size (16 bytes for AES)
#     padder = padding.PKCS7(algorithms.AES.block_size).padder()
#     padded_cvv_bytes = padder.update(cvv_bytes) + padder.finalize()
    
#     # Encrypt the padded CVV
#     encrypted_cvv = encryptor.update(padded_cvv_bytes) + encryptor.finalize()
    
#     # Combine IV and encrypted CVV into a single string (Base64 encoded)
#     encrypted_data = base64.b64encode(iv + encrypted_cvv).decode()
    
#     return encrypted_data

# # Decrypt CVV using AES and decode from Base64
# def decrypt_cvv(encrypted_cvv: str, key: bytes) -> str:
#     # Decode Base64 and separate IV and encrypted CVV
#     encrypted_data = base64.b64decode(encrypted_cvv.encode())
#     iv = encrypted_data[:16]
#     encrypted_cvv_bytes = encrypted_data[16:]
    
#     # Initialize AES cipher with CBC mode and decrypt
#     cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
#     decryptor = cipher.decryptor()
#     decrypted_padded_cvv_bytes = decryptor.update(encrypted_cvv_bytes) + decryptor.finalize()
    
#     # Remove padding from decrypted CVV
#     unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
#     decrypted_cvv_bytes = unpadder.update(decrypted_padded_cvv_bytes) + unpadder.finalize()
    
#     # Convert decrypted CVV bytes to string
#     decrypted_cvv = decrypted_cvv_bytes.decode('utf-8')
    
#     return decrypted_cvv

# # Example usage:
# key = generate_aes_key()  # Generate a new AES key (should be securely stored)

# # Encrypt CVV
# original_cvv = '123'
# encrypted_cvv = encrypt_cvv(original_cvv, key)
# print(f"Encrypted CVV (Base64 encoded): {encrypted_cvv}")

# # Decrypt CVV
# decrypted_cvv = decrypt_cvv(encrypted_cvv, key)
# print(f"Decrypted CVV: {decrypted_cvv}")

