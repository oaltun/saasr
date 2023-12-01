import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlanBase(BaseModel):
    is_active: bool
    name: str
    description: str
    features: str
    id: str


class PlanDB(PlanBase):
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class Plan(PlanBase):
    class Config:
        orm_mode = True


class PlanOut(PlanDB):
    pass
# --------------------------------------


class BillingCycleBase(BaseModel):
    name: str
    id: str
    description: str
    billing_period_in_months: int
    remind_term_end_in_days: int
    grace_period_duration_in_days: int
    is_active: bool


class BillingCycleCreate(BillingCycleBase):
    pass


class BillingCycleUpdate(BillingCycleBase):
    modified_at: Optional[datetime]


class BillingCycle(BillingCycleBase):
    class Config:
        orm_mode = True


###-------------------------------
class PriceBase(BaseModel):
    plan_id: str
    billing_cycle_id: str
    price_per_month: float


class PriceOut(PriceBase):
    class Config:
        orm_mode = True


Price = PriceOut


class PriceCreate(PriceBase):
    pass


class PriceUpdate(PriceBase):
    pass
