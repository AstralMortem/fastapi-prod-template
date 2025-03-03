from app.models.auth import User
from .permission import HasRole, Authorization
from core.config import settings

class FalseAuth(Authorization):
    def has_access(self, user: User):
        return False


SuperUser = HasRole(settings.SUPERUSER_DEFAULT_ROLE_NAME) if settings.SUPERUSER_DEFAULT_ROLE_NAME else FalseAuth()
