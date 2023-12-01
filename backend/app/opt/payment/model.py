from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

from app.core.session import Base
from app.config import settings


class BillingInfo(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "billing_info"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        nullable=False,
    )

    gsm_number = Column(String, nullable=True)
    currency = Column(String, nullable=False, default="USD")  # TL, USD, EUR, GBP

    ## company related info
    user_is_company_representer = Column(Boolean, nullable=False, default=False)
    company_name = Column(String, nullable=True)
    company_tax_number = Column(String, nullable=True)
    company_tax_office = Column(String, nullable=True)

    ## company address info
    company_address_country = Column(String, nullable=True)
    company_address_state = Column(String, nullable=True)
    company_address_city = Column(String, nullable=True)
    company_address_street_address = Column(String, nullable=True)
    company_address_postal_code = Column(String, nullable=True)

    ## billing address info
    billing_address_country = Column(String, nullable=False)
    billing_address_state = Column(String, nullable=True)
    billing_address_city = Column(String, nullable=False)
    billing_address_street_address = Column(String, nullable=False)
    billing_address_postal_code = Column(String, nullable=True)

    ## billing address info
    buyer_address_country = Column(String, nullable=False)
    buyer_address_state = Column(String, nullable=True)
    buyer_address_city = Column(String, nullable=False)
    buyer_address_street_address = Column(String, nullable=False)
    buyer_address_postal_code = Column(String, nullable=True)

    ## user relationship
    user = relationship("User")


class CreditCard(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "credit_card"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        nullable=False,
    )
    iyzico_credit_card_token_id = Column(String, nullable=False)
    iyzico_credit_card_user_key = Column(String, nullable=False)
    user = relationship("User")


class Purchase(Base):
    __tablename__ = settings.DATABASE_TABLE_PREFIX + "purchase"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    purchase_number = Column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid4,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "user.id", ondelete="CASCADE"),
        nullable=False,
    )
    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey(settings.DATABASE_TABLE_PREFIX + "team.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    paid_at = Column(TIMESTAMP(timezone=True))
    number_of_licenses = Column(Integer, nullable=False)
    payment_amount = Column(Numeric, nullable=False)
    iyzico_sent_json = Column(String)
    iyzico_returned_json = Column(String)
    is_paid = Column(Boolean, nullable=False, default=False)
    is_refunded = Column(Boolean, nullable=False, default=False)
    iyzico_paymentId = Column(String)
    payment_transaction_id = Column(String)
    user = relationship("User")
    team = relationship("Team")
