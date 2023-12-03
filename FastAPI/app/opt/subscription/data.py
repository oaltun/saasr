from app.opt.subscription.crud import create_billing_cycle, create_plan, create_price
from app.opt.subscription.schema import BillingCycleCreate, PlanCreate, PriceCreate


plans = [
    {
        "id": "free",
        "name": "Free",
        "description": "Free",
        "features": "No sign up required -- Show hidden answers -- Delete answer controls",
        "is_active": True,
    },
    {
        "id": "lite",
        "name": "Lite",
        "description": "Exam Add-in -- Lite Subscription",
        "features": "All the free features -- Insert open ended answers -- Insert correct choices -- Insert fill-ins -- Team Management -- Consolidated billing -- Volume Discount",
        "is_active": True,
    },
    {
        "id": "pro",
        "name": "Pro",
        "description": "Exam Add-in Unlimited -- Pro Subscription",
        "features": "All the lite features -- Insert open ended answers (Beta)",
        "is_active": True,
    },
    # {
    #     "id": "unused",
    #     "name": "Unused",
    #     "description": "For testing.",
    #     "features": "None",
    #     "is_active": False,
    # },
]

billing_cycles = [
    {
        "id": "1_month",
        "name": "Monthly",
        "description": "Billed every month",
        "billing_period_in_months": 1,
        "is_active": True,
        "remind_term_end_in_days": 7,
        "grace_period_duration_in_days": 7,
    },
    {
        "id": "2_months",
        "name": "Per 2 months",
        "description": "Billed every 2 months",
        "billing_period_in_months": 2,
        "is_active": False,
        "remind_term_end_in_days": 7,
        "grace_period_duration_in_days": 7,
    },
    {
        "id": "3_months",
        "name": "Per 3 months",
        "description": "Billed every 3 months",
        "billing_period_in_months": 3,
        "is_active": False,
        "remind_term_end_in_days": 7,
        "grace_period_duration_in_days": 7,
    },
    {
        "id": "4_months",
        "name": "Per 4 months",
        "description": "Billed every 4 months",
        "billing_period_in_months": 4,
        "is_active": True,
        "remind_term_end_in_days": 7,
        "grace_period_duration_in_days": 7,
    },
    {
        "id": "6_months",
        "name": "Per 6 months",
        "description": "Billed every 6 months",
        "billing_period_in_months": 6,
        "is_active": False,
        "remind_term_end_in_days": 7,
        "grace_period_duration_in_days": 7,
    },
    {
        "id": "12_months",
        "name": "Annual",
        "description": "Billed every 12 months",
        "billing_period_in_months": 12,
        "is_active": True,
        "remind_term_end_in_days": 7,
        "grace_period_duration_in_days": 7,
    },
]


prices = [
    {"plan_id": "lite", "billing_cycle_id": "1_month", "price_per_month": 5.99},
    {
        "plan_id": "lite",
        "billing_cycle_id": "4_months",
        "price_per_month": 5.49,
    },
    {
        "plan_id": "lite",
        "billing_cycle_id": "12_months",
        "price_per_month": 4.99,
    },

    {"plan_id": "pro", "billing_cycle_id": "1_month", "price_per_month": 11.99},
    {
        "plan_id": "pro",
        "billing_cycle_id": "4_months",
        "price_per_month": 10.99,
    },
    {
        "plan_id": "pro",
        "billing_cycle_id": "12_months",
        "price_per_month": 9.99,
    },


]
def init_plans(db):

    return [create_plan(db, PlanCreate(**plan_json)) for plan_json in plans]


def init_billing_cycles(db):

    return [
        create_billing_cycle(db, BillingCycleCreate(**cycle))
        for cycle in billing_cycles
    ]


def init_prices(db):

    return [create_price(db, PriceCreate(**price)) for price in prices]