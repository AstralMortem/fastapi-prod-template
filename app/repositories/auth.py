import uuid
from app.models.auth import User
from core.repository import BaseRepository


class AuthRepository(BaseRepository[User, uuid.UUID]):
    model = User
