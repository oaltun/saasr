import uuid
from app.core import session
from app.lib import db_create, db_get
from app.opt.subscription import schema
from sqlalchemy.orm import Session
from app.opt.subscription import model

from app.opt.subscription.model import BillingCycle, Plan, Price

###------------


def create_plan(db: Session, plan: schema.PlanCreate) -> Plan:
    return db_create(db, Plan, plan)


def get_plan(db: Session, id: uuid.UUID):
    return db_get(db, Plan, id, "Plan")


###------------


def create_billing_cycle(
    db: Session, cycle: schema.BillingCycleCreate
) -> BillingCycle:
    return db_create(db, BillingCycle, cycle)


def get_billing_cycle(db: Session, id: uuid.UUID):
    return db_get(db, BillingCycle, id, "Billing Cycle")


###------------
def create_price(db, price: schema.PriceCreate) -> model.Price:
    return db_create(db, model.Price, price)


def get_price(db, plan_id: str, billing_cycle_id: str):
    return (
        db.query(Price)
        .filter(
            Price.billing_cycle_id == billing_cycle_id,
            Price.plan_id == plan_id,
        )
        .first()
    )
