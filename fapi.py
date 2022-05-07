import sys
sys.path.append('./source/')


from settings import settings
from driver.http.fapi import http
from api.urls import *


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        f'{__name__}:http',
        host=settings.WWW_HOST,
        port=settings.WWW_PORT,
        workers=settings.WWW_WORKERS
    )

