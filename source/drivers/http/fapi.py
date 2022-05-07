from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from middlewares import HTTP_MIDDLEWARES


http = FastAPI()


for mw in HTTP_MIDDLEWARES:
    http.add_middleware(BaseHTTPMiddleware, dispatch=mw)

