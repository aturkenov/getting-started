class AuthorizationException(Exception):
    status_code = 400
    cause = 'Invalid email or password'


class TokenRequired(Exception):
    status_code = 400
    cause = 'Token Required'


class InvalidToken(Exception):
    status_code = 400
    cause = 'Invalid Token'


class PasswordHashingFailedException(Exception):
    status_code = 500
    cause = 'Passed password text was not hashed'
    code = 'Exception was raised on service layer'