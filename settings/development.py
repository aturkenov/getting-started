from datetime import timedelta


# WAMP
WAMP_DOMAIN = 'com.orionm2m.ami'
WAMP_ROUTER = 'ws://crossbar:8989/private'
WAMP_REALM = 'ami'
WAMP_AUTHID = 'AMI'
WAMP_TICKET = 'secret'

WAMP_PUBLIC_ROLE = 'public'

WAMP_TOKEN_EXPIRATION_DELTA = timedelta(days=5)


# WWW (FastAPI)
HTTP_HOST = '0.0.0.0'
HTTP_PORT = 8000
HTTP_WORKERS = 1
HTTP_DOMAIN = '/api/v1/'


# Datetime configs
USE_TIMEZONE = True
DATETIME_FORMAT = '%d-%m-%y %H:%M:%S'
DATE_FORMAT = '%d-%m-%y'


# Token
JWT_TOKEN_EXPIRATION_DAYS = 7


# (En/De)cryption
ENCRYPTION_ALGORITHM = 'RS256'
RSA_PRIVATE_KEY_PATH = './settings/rsa'
with open(RSA_PRIVATE_KEY_PATH, 'rb') as rsa_private_key_file:
    RSA_PRIVATE_KEY = rsa_private_key_file.read().strip()

RSA_PUBLIC_KEY_PATH = './settings/rsa.pub'
with open(RSA_PUBLIC_KEY_PATH, 'rb') as rsa_public_key_file:
    RSA_PUBLIC_KEY = rsa_public_key_file.read().strip()


# Redis
REDIS_HOST = 'localhost'
REDIS_PASSWORD = 'secret'
REDIS_PORT = 6379
REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
REDIS_POOL_SIZE = 100
REDIS_WAIT_TIMEOUT = 60


# Database
DB_HOST = 'localhost'
DB_NAME = 'ami'
DB_USER = 'ami'
DB_PASSWORD = 'secret'
DB_PORT = 5432


# SQLAlchemy settings
SQLALCHEMY_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SQLALCHEMY_ECHO = False
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 10

ASYNC_SQLALCHEMY_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


# TimescaleDB
TDB_HOST = 'localhost'
TDB_NAME = 'ami'
TDB_USER = 'ami'
TDB_PASSWORD = 'secret'
TDB_PORT = 5432
TDB_PSYCOPG_ADDITIONAL_PARAMS = ''
TDB_ASYNCPG_ADDITIONAL_PARAMS = ''

# Timescale SQLAlchemy settings
TIMESCALE_SQLALCHEMY_URL = f'postgresql+psycopg2://{TDB_USER}:{TDB_PASSWORD}@{TDB_HOST}:{TDB_PORT}/{TDB_NAME}'
TIMESCALE_SQLALCHEMY_ECHO = False
TIMESCALE_SQLALCHEMY_POOL_SIZE = 40
TIMESCALE_SQLALCHEMY_MAX_OVERFLOW = 10

ASYNC_TIMESCALE_SQLALCHEMY_URL = f'postgresql+asyncpg://{TDB_USER}:{TDB_PASSWORD}@{TDB_HOST}:{TDB_PORT}/{TDB_NAME}'


# Robber ASYNCPG Configs
ASYNCPG_DSN = f'postgres://{TDB_USER}:{TDB_PASSWORD}@{TDB_HOST}:{TDB_PORT}/{TDB_NAME}'
ASYNCPG_MIN_CONNECTIONS_SIZE = 1
ASYNCPG_MAX_CONNECTIONS_SIZE = 50
ASYNCPG_MAX_QUERIES = 50000
ASYNCPG_MAX_INACTIVE_CONNECTIONS_LIFETIME = 300.0


# Logging
SQL_FILE_PATH = '/var/log/orionm2m/sql'
ERROR_FILE_PATH = '/var/log/orionm2m/error'
INFO_FILE_PATH = '/var/log/orionm2m/info'


# Cloud Storage
# from google.oauth2 import service_account
# GOOGLE_APPLICATION_CREDENTIALS_PATH = './settings/credentials.json'
# GS_CREDENTIALS = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS_PATH)

# GS_URL = 'https://storage.googleapis.com/orionm2m-ami/'
# GS_BUCKET_NAME = 'orionm2m-ami'

# FOLDER_PREFIX = 'development'

# URL_EXPIRATION_TIME = 604800  # 7 days
# UPLOAD_TIMEOUT = 60  # 1 minute

