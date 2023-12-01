from email.policy import default
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from app.core.session import Base
from app.config import settings


class TeamParticipation(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "team_participation"

    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "team.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    is_admin = Column(Boolean, nullable=False, default=False)
    recurring_payer = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    user = relationship("User")
    team = relationship("Team", viewonly=True)


def default_team_name():
    return "Team " + str(uuid4())


class Team(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "team"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    plan_id = Column(
        String,
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "plan.id", ondelete="CASCADE"),
        nullable=True,
    )
    plan_id_next_term = Column(String, nullable=True)
    billing_cycle_id = Column(
        String,
        ForeignKey(
            settings.DATABASE_TABLE_PREFIX + "billing_cycle.id", ondelete="CASCADE"
        ),
        nullable=True,
    )
    billing_cycle_id_next_term = Column(String, nullable=True)

    name = Column(String, unique=False, default=default_team_name)
    number_of_licenses = Column(Integer, default=0)
    number_of_licenses_next_term = Column(Integer, nullable=False, default=0)
    recurring_billing_is_on = Column(Boolean, nullable=False, default=True)
    term_end_date = Column(TIMESTAMP(timezone=True), nullable=True)

    billing_cycle = relationship("BillingCycle")
    plan = relationship("Plan")
    invitations = relationship("TeamInvitation")
    participations = relationship("TeamParticipation")


class TeamInvitation(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "team_invitation"
    id = Column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid4,
    )
    email = Column(
        String,
        primary_key=True,
        nullable=False,
    )

    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "team.id", ondelete="CASCADE"),
        nullable=False,
    )
    team = relationship("Team", viewonly=True)

    inviter_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        nullable=False,
    )
    inviter = relationship("User", viewonly=True)

    is_admin = Column(Boolean, primary_key=True, default=False, nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
