# Compatibility shim for tests expecting top-level `settings` module
from utils.settings import *

__all__ = ["SECRET_KEY", "JWT_HASH_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES", "REFRESH_TOKEN_EXPIRE_DAYS"]
