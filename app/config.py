from os import getenv
from dotenv import load_dotenv

load_dotenv()

# App
SECRET_KEY = getenv('SECRET_KEY', 'yyyyyyyyyyyyy')
SERVER_NAME = getenv('SERVER_NAME', '127.0.0.1:5000')
SITE_NAME = getenv('SITE_NAME', 'Raffler')
TEMPLATES_AUTO_RELOAD = getenv('TEMPLATES_AUTO_RELOAD', True)

# DB
DB_USER = getenv('DB_USER', 'raffler')
DB_PASS = getenv('DB_PASS', 'xxxxxxxxxxx')
DB_NAME = getenv('DB_NAME', 'raffler')
DB_HOST = getenv('DB_HOST', '127.0.0.1')
DB_PORT = getenv('DB_PORT', '5432')

# Auth
# Configuration
GOOGLE_CLIENT_ID = getenv('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = getenv('GOOGLE_CLIENT_SECRET', None)
GOOGLE_DISCOVERY_URL = (
    'https://accounts.google.com/.well-known/openid-configuration'
)
