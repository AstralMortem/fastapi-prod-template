import uuid
from app.models.auth import User, Role
from sqlalchemy import select
from core.repository import BaseRepository


class AuthRepository(BaseRepository[User, uuid.UUID]):
    model = User

    async def get_role_by_codename(self, rolename:str) -> Role | None:
        qs = select(Role).where(Role.codename == rolename)
        return await self.session.scalar(qs)