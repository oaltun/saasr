from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP

from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

from app.core.session import Base
from app.config import settings


class Issue(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "support_issue"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        nullable=False,
    )
    owner = relationship("User", viewonly=True, foreign_keys=[owner_id])

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    title = Column(String, nullable=False)

    is_closed = Column(Boolean, nullable=False, default=False)
    closed_at = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=text("now()")
    )
    closer_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        nullable=True,
    )
    closer = relationship("User", viewonly=True, foreign_keys=[closer_id])

    messages = relationship("Message")


## TODO: https://docs.sqlalchemy.org/en/14/orm/relationship_persistence.html#post-update
class Message(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "support_message"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    issue_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            settings.DATABASE_TABLE_PREFIX + "support_issue.id", ondelete="CASCADE"
        ),
        nullable=False,
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        nullable=False,
    )
    owner = relationship("User", viewonly=True)

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    text = Column(Text, nullable=False)
