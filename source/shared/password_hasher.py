import base64
import hashlib

import argon2.exceptions
from argon2 import PasswordHasher
from exceptions import PasswordHashingFailedException, EmptyStringException


def hash_password(
    password: str
) -> str:
    """
    Uses argon2 algorithm for hashing
    """
    # FIXME add password validators for common, numeric, length, similarity
    if not password:
        raise EmptyStringException

    password_hasher = PasswordHasher()

    hashed_password = password_hasher.hash(password)
    if password_hasher.check_needs_rehash(hashed_password):
        raise PasswordHashingFailedException

    return hashed_password

def is_match(
    password: str,
    hashed_password: str,
) -> bool:
    """
    Uses both argon2 algorithm and pbkdf2 algorithm to determine if password and hashed password matches
    """
    argon_password_hasher = PasswordHasher()
    try:
        argon_password_hasher.verify(hash=hashed_password, password=password)
        return True
    except argon2.exceptions.VerificationError:
        return False
    except argon2.exceptions.InvalidHash:
        pass

    if 'sha256' not in hashed_password:
        return False

    # django_algorithm_name equal to pbkdf2_sha256 which not can be pass to hashlib function
    # but it already should be in hashed password
    split_symbol = '$'  # split symbol in django
    django_algorithm_name, iteration, salt, hash_self = hashed_password.split(split_symbol)
    try:
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), int(iteration))
        new_hash = base64.b64encode(new_hash).decode('ascii').strip()
        new_django_like_hash = \
            f'{django_algorithm_name}{split_symbol}{iteration}{split_symbol}{salt}{split_symbol}{new_hash}'
        if hashed_password == new_django_like_hash:
            return True
    except BaseException as e:
        # TODO need to handle this
        pass

    return False
