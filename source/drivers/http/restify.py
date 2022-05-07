from typing import Optional, Callable
from fastapi import Depends, Request, HTTPException
from fastapi.security.http import HTTPBase
from wampify.signals import entrypoint_signals
from sessions import *
from shared.jwtoken import *
from .fapi import http
from .entrypoint import HTTPEntrypoint
from ..shared.make_ellipsis_default import make_ellipsis_default
from settings import settings


class HTTPAuthorization(HTTPBase):

    def __init__(
        self,
        *,
        scheme: Optional[str] = 'custom',
        auto_error: bool = True,
    ):
        super(HTTPAuthorization, self).__init__(
            scheme=scheme,
            auto_error=auto_error
        )

    async def __call__(
        self,
        request: Request
    ) -> Optional[JWTToken]:
        credentials = await super(HTTPAuthorization, self).__call__(request=request)

        if not self.auto_error:
            return

        if not credentials:
            raise HTTPException(status_code=403, detail='Invalid authorization code.')
        if not credentials.scheme == 'JWT':
            raise HTTPException(status_code=403, detail='Invalid authentication scheme.')
        if not is_valid_token(credentials.credentials):
            raise HTTPException(status_code=403, detail='Invalid token or expired token.')

        try:
            return get_decoded_token(credentials.credentials)
        except Exception as e:
            raise HTTPException(status_code=403, detail=f'Cannot decode token {e}')


def restify(
    path: str,
    procedure: Callable,
    authorization_required: Optional[bool] = True,
    version=1
):
    assert not path.startswith('/'), 'First symbol can not be `/`'

    URL = f'/api/v{version}/{path}'
    custom_authorization_handler = HTTPAuthorization(auto_error=authorization_required)

    make_ellipsis_default(procedure)

    entrypoint = HTTPEntrypoint(procedure)

    # This function is executed when someone sends http request
    # Each event must have { token, payload }
    @http.post(URL)
    async def _(
        request: Request,
        token: Optional[JWTToken] = Depends(custom_authorization_handler)
    ):
        content_type = request.headers.get('content-type')
        if content_type == 'application/json':
            body = await request.json()
        else:
            # Otherwise content-type = 'multipart/form-data'
            form = await request.form()
            body = dict(form)

        @entrypoint_signals.on
        def opened(story):
            """
            Binds current customer to story
            """
            story.customer = None
            if authorization_required:
                story.customer = token.customer

        return await entrypoint(kwargs=body)

    print(URL, 'registered')

