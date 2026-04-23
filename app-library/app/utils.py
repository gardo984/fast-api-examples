

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

password_hash = PasswordHash([BcryptHasher()])


def hash_password(value: str) -> str:
    return password_hash.hash(value)


def verify_password_hash(passwd: str, hashed_passwd: str) -> str:
    return password_hash.verify(passwd, hashed_passwd)
