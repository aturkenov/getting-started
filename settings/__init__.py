from os import environ
from dotenv import load_dotenv


__all__ = ('settings')


settings = None
if settings is None:
    print('.env is loading')
    load_dotenv(dotenv_path='./settings/.env')

    is_dev = environ.get('DEVELOPMENT_MODE', False)
    if is_dev == 't':
        print('Development mode. Please disable it in production')
        from . import development
        settings = development
        settings.DEBUG = True
    else:
        from . import main
        settings = main
        settings.DEBUG = False

