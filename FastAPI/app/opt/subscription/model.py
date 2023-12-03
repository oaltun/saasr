from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.core.session import Base
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from app.config import settings


class Plan(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "plan"

    id = Column(String, primary_key=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    modified_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    features = Column(String, nullable=False)  # plan features stored as String
    is_active = Column(Boolean, nullable=False, default=True)


class BillingCycle(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "billing_cycle"

    id = Column(String, primary_key=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    modified_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    billing_period_in_months = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    remind_term_end_in_days = Column(Integer, nullable=False)
    grace_period_duration_in_days = Column(Integer, nullable=False)


class Price(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "price"
    ## id is just for counting. not primary key.
    id = Column(
        UUID(as_uuid=True),
        index=True,
        nullable=False,
        default=uuid4,
    )
    plan_id = Column(
        String,
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "plan.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    billing_cycle_id = Column(
        String,
        ForeignKey(
            settings.DATABASE_TABLE_PREFIX + "billing_cycle.id", ondelete="CASCADE"
        ),
        primary_key=True,
        nullable=False,
    )
    ######### billing cycle id and plan id composite primary key ##########

    price_per_month = Column(Numeric, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    modified_at = Column(TIMESTAMP(timezone=True))
    plan = relationship("Plan")
    billing_cycle = relationship("BillingCycle")
