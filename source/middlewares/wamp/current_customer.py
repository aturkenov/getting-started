from typing import Callable
from wampify.story import *
from wampify.requests import BaseRequest
from shared.jwtoken import get_decoded_token
from exceptions import TokenRequired, InvalidToken


async def CurrentCustomer(
    nest: Callable,
    request: BaseRequest
):
    """
    Sets request.customer to story
    Also decodes passed token
    """
    story = get_current_story()
    enabled = story._endpoint_options_.middlewares.get('token-required', True)
    if not enabled:
        return await nest(request)
    token = request.kwargs.pop('__token__', None)
    if token is None:
        raise TokenRequired()
    # Decodes and validates token
    try:
        _token = get_decoded_token(token)
    except:
        raise InvalidToken()
    customer_uuid = request.details.caller_authid or request.details.publisher_authid
    if str(_token.customer.uuid) != str(customer_uuid):
        raise InvalidToken()
    story.customer = _token.customer
    return await nest(request)

