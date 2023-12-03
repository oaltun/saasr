from email.policy import default
from typing import Tuple
from sqlalchemy import Boolean, Column, Integer, String

from app.core.session import Base
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.config import settings


class User(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "user"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid4,
    )
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)


class UserSecret(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "user_secret"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    token = Column(
        String,
        nullable=False,
        primary_key=True,
    )

    is_verification = Column(Boolean, default=False, nullable=False)
    is_reset = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )

    valid_for_hours = Column(
        Integer,
        nullable=False,
    )
