# services/__init__.py
from config import ALLOWED_USER_IDS
from config import ALLOWED_USER_IDS, ADMIN_IDS

def is_user_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS