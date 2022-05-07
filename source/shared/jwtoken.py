from datetime import datetime, timedelta
from typing import Union
import jwt
from pydantic import BaseModel
from settings import settings
import domain


class JWTToken(BaseModel):
    customer: domain.Customer
    created_date: str

    def to_primitive(
        self,
        *args,
        **kwargs
    ) -> dict:
        data = self.dict(*args, **kwargs)
        data['customer']['uuid'] = str(self.customer.uuid)
        if self.customer.last_activity:
            data['customer']['last_activity'] = self.customer.last_activity.isoformat()
        data['customer']['date_joined'] = self.customer.date_joined.isoformat()
        return data


def get_encoded_token(
    customer: domain.Customer,
) -> bytes:
    created_date = datetime.utcnow().isoformat()
    jwt_token = JWTToken(customer=customer, created_date=created_date)

    return jwt.encode(
        jwt_token.to_primitive(exclude={'customer': {'password'}}),
        settings.RSA_PRIVATE_KEY,
        algorithm=settings.ENCRYPTION_ALGORITHM
    )


def is_valid_token(
    token: Union[str, bytes],
) -> bool:
    try:
        jwt_token_dict: dict = jwt.decode(token, settings.RSA_PUBLIC_KEY, algorithms=[settings.ENCRYPTION_ALGORITHM])
    except Exception:
        return False

    try:
        created_date = jwt_token_dict['created_date']
        d = datetime.utcnow() - datetime.fromisoformat(created_date)
        if d > timedelta(days=settings.JWT_TOKEN_EXPIRATION_DAYS):
            return False
    except Exception:
        return False

    return True


def get_decoded_token(
    token: Union[str, bytes]
) -> JWTToken:
    try:
        jwt_token_dict: dict = jwt.decode(token, settings.RSA_PUBLIC_KEY, algorithms=[settings.ENCRYPTION_ALGORITHM])
    except Exception:
        raise

    return JWTToken(**jwt_token_dict)

