from core.auth import TokenManager, PasswordHasher
from fastapi_login import LoginManager
from web_server.settings import settings

token_manager = TokenManager()
password_hasher = PasswordHasher()
login_manager = LoginManager(settings.SECRET_KEY, tokenUrl="/auth/token")
