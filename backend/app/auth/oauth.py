from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from dotenv import load_dotenv
import os

load_dotenv()

# OAuth Configuration
oauth = OAuth()

# Configure GitHub OAuth
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user repo read:org'},
)