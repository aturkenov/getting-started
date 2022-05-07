from .wamp.jsonable import Jsonable as wampJsonable
from .wamp.current_customer import CurrentCustomer
from .http.jsonable import Jsonable as httpJsonable
from .http.streaming_response import ConvertToStreamingResponse


WAMP_MIDDLEWARES = [
    wampJsonable,
    CurrentCustomer,
]

HTTP_MIDDLEWARES = [
    httpJsonable,
    ConvertToStreamingResponse
]

