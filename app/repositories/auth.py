import uuid
from app.models.auth import User, Role
from sqlalchemy import select
from core.repository import BaseRepository
from core.config import settings

class AuthRepository(BaseRepository[User, uuid.UUID]):
    model = User

    async def get_role_by_codename(self, rolename:str) -> Role | None:
        qs = select(Role).where(Role.codename == rolename)
        return await self.session.scalar(qs)

class RoleRepository(BaseRepository[Role,settings.DEFAULT_PK_FIELD_TYPE]):
    model = Role
