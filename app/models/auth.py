import uuid
from sqlalchemy import UUID, String, ForeignKey
from core.db import Model
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.config import settings

# Many-to-many User and Role
class UserRole(Model):
    __without_default_pk__ = True
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)


# Many-to-many Role and Permission
class RolePermission(Model):
    __without_default_pk__ = True
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )


# Main USER Model
class User(Model):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(250), unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=settings.USER_IS_ACTIVE_DEFAULT)

    roles: Mapped[list["Role"]] = relationship(
        secondary=UserRole.__table__, back_populates="users",
        lazy="joined"
    )
    refresh_token: Mapped["RefreshToken | None"] = relationship(
        lazy="joined", back_populates="user"
    )


class Role(Model):
    codename: Mapped[str] = mapped_column(unique=True, index=True)
    users: Mapped[list["User"]] = relationship(
        secondary=UserRole.__table__, back_populates="roles"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=RolePermission.__table__, back_populates="roles",
        lazy="joined"
    )


class Permission(Model):
    codename: Mapped[str] = mapped_column(unique=True, index=True)
    roles: Mapped[list[Role]] = relationship(
        secondary=RolePermission.__table__, back_populates="permissions"
    )


class RefreshToken(Model):
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    refresh_token: Mapped[str]

    user: Mapped[User] = relationship(back_populates="refresh_token")
