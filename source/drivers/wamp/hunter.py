from functools import partial
from wampify import Wampify
from ..base import wamp
from sessions import *
from settings import settings
from middlewares import WAMP_MIDDLEWARES


def _on_challenge(challenge):
    return settings.HUNTER_WAMP_TICKET


wampify = Wampify(
    debug=True,
    start_loop=False,
    router={
        'url': settings.HUNTER_WAMP_ROUTER
    },
    preuri=settings.HUNTER_WAMP_DOMAIN,
    wamps={
        'realm': settings.HUNTER_WAMP_REALM,
        'on_challenge': _on_challenge,
        'authid': settings.HUNTER_WAMP_AUTHID,
        'authrole': 'private',
        'authmethods': ['ticket'],
        'show_registered': True,
        'show_subscribed': True
    }
)


for mw in WAMP_MIDDLEWARES:
    wampify.add_middleware(mw)


wampify_register = partial(wamp.wampify_register, wampify)
wampify_subscribe = partial(wamp.wampify_subscribe, wampify)

