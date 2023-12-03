import asyncio
from app import config
from app.core.auth import get_current_active_user_or_400
from app.core.session import get_db
from app.lib import db_get_item_or_error
from app.opt.payment.model import BillingInfo, CreditCard, Purchase
from app.opt.subscription.model import BillingCycle, Price
from app.team.model import Team, TeamParticipation
from app.user.model import User
from app.core.error import error_detail
import iyzipay
import json
from datetime import datetime
# from dateutil import relativedelta # type: ignore
from dateutil.relativedelta import relativedelta # type: ignore
from fastapi import Depends, status, HTTPException
from fastapi_mail import MessageSchema # type: ignore
from app.opt.payment import schema
import uuid


from sqlalchemy.orm import Session


iyzico_options = {
    "api_key": config.settings.SAASR_IYZICO_API_KEY,
    "secret_key": config.settings.SAASR_IYZICO_SECRET_KEY,
    "base_url": config.settings.IYZICO_BASE_URL,
}


def payment_form_as_string(iyzico_request):
    sent_json = json.dumps(iyzico_request)
    return sent_json


def create_iyzico_request(
    payment_form: schema.PaymentForm, user_id, user_email,ip
):
    iyzico_request = dict([("locale", "en")])
    iyzico_request["price"] = payment_form.price # type: ignore
    iyzico_request["paidPrice"] = payment_form.price # type: ignore
    iyzico_request["currency"] = "USD"
    iyzico_request["installment"] = "1"

    paym_card = dict([("cardNumber", payment_form.payment_card.cardNumber)])
    paym_card["expireYear"] = payment_form.payment_card.expireYear
    paym_card["expireMonth"] = payment_form.payment_card.expireMonth
    paym_card["cvc"] = payment_form.payment_card.cvc
    paym_card["cardHolderName"] = payment_form.payment_card.cardHolderName
    paym_card["registerCard"] = "1"
    iyzico_request["paymentCard"] = paym_card # type: ignore

    current_buyer = dict([("id", str(user_id))])
    current_buyer["name"] = payment_form.buyer.name
    current_buyer["surname"] = payment_form.buyer.surname
    current_buyer["identityNumber"] = "74300864791"
    current_buyer["city"] = payment_form.buyer.address.city
    current_buyer["country"] = payment_form.buyer.address.country
    current_buyer["email"] = user_email
    current_buyer["ip"] = '85.34.78.112' # ip
    current_buyer["registrationAddress"] = payment_form.buyer.address.street_address
    if payment_form.buyer.address.state:
        current_buyer["registrationAddress"] = payment_form.buyer.address.street_address + " ,"+payment_form.buyer.address.state

    if payment_form.buyer.address.postal_code:
        current_buyer["zipCode"] = payment_form.buyer.address.postal_code
    iyzico_request["buyer"] = current_buyer # type: ignore

    bill_address=dict()
    bill_address["city"] = payment_form.billing_address.city
    bill_address["country"] = payment_form.billing_address.country
    bill_address["contactName"] = payment_form.buyer.name + " "+payment_form.buyer.surname
    bill_address["address"]= payment_form.billing_address.street_address + " ," + payment_form.billing_address.state # type: ignore
    bill_address["zipCode"]= payment_form.billing_address.postal_code # type: ignore
    iyzico_request["billingAddress"] = bill_address # type: ignore

    bask_item = dict([("id", str(payment_form.billing_cycle_id))])
    bask_item["itemType"] = "VIRTUAL"
    bask_item["name"] = "Billing Cycle id: " + str(payment_form.billing_cycle_id)
    bask_item["category1"] = "Electronics"
    bask_item["price"] = payment_form.price # type: ignore
    bask_items = []
    bask_items.append(bask_item)
    iyzico_request["basketItems"] = bask_items # type: ignore
    return iyzico_request


def calculate_additional_subscription_price_or_409(team: Team, db):
    term_end = datetime.strptime(
        str(team.term_end_date.year)
        + "-"
        + str(team.term_end_date.month)
        + "-"
        + str(team.term_end_date.day),
        "%Y-%m-%d",
    )
    # 71st row makes, team.term_end column as a datetime object into term_end variable
    now = datetime.now()  # current time
    if now >= term_end:  # if current time already passed term_end
        print("(31817bbe)")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail("TERM_ALREADY_ENDED")
        )
    price_db = (
        db.query(Price)
        .filter(
            Price.billing_cycle_id == team.billing_cycle_id,
            Price.plan_id == team.plan_id,
        )
        .first()
    )  # we look for price in db for selected billing cycle and plan
    price_per_day = (
        price_db.price_per_month / 30
    )  # we assumed that, 1 month equals to 30 days
    date_difference = relativedelta(term_end, now)
    # relativedelta function substracts 2 dates and return an object which contains
    # year, month, day fields. This fields equals to difference of 2 dates.
    # ex: d1: 2022-03-22, d2:2021-01-17 -> 1 year 2 months and 5 days
    months = date_difference.months + (12 * date_difference.years)
    # so our difference in months equals to 12*difference in years + difference in months
    days = date_difference.days
    # and difference in days equals to date_differences days field
    # finally, we calculate additional price as:
    # price_per_day* difference in days+ price_per_month* difference in months
    return (price_per_day * days) + (price_db.price_per_month * months)


def is_purchase_expired(term_end_date):
    d1 = datetime.strptime(
        str(term_end_date.year)
        + "-"
        + str(term_end_date.month)
        + "-"
        + str(term_end_date.day),
        "%Y-%m-%d",
    )
    d2 = datetime.now()
    return d1 <= d2


def save_user_infos_to_db(
    payment_form: schema.PaymentForm,
    current_user: User,
    db: Session = Depends(get_db),
):
    # add name and surname to user
    # current_user.update({"name":payment_form.buyer.name, "surname":payment_form.buyer.surname})
    current_user.name = payment_form.buyer.name # type: ignore
    current_user.surname = payment_form.buyer.name # type: ignore
    db.commit()
    db.refresh(current_user)
    
    billing_info = (
        db.query(BillingInfo)
        .filter(BillingInfo.user_id == current_user.id)
        .first()
    )

    if (billing_info):  
        # TODO: rewrite billing info to db
        # billing info is not none, then users billing info already saved into db so we can return
        return

    info=dict()
    info["user_id"] = current_user.id

    info["user_is_company_representer"]= payment_form.user_is_company_representer # type: ignore
    if payment_form.user_is_company_representer:
        info["company_name"] = payment_form.company_info.company_name # type: ignore
        info["company_tax_number"] = payment_form.company_info.company_tax_number # type: ignore
        info["company_tax_office"] = payment_form.company_info.company_tax_office # type: ignore

        info["company_address_country"] = payment_form.company_info.address.country # type: ignore
        info["company_address_state"] = payment_form.company_info.address.state # type: ignore
        info["company_address_city"] = payment_form.company_info.address.city # type: ignore
        info["company_address_street_address"] = payment_form.company_info.address.street_address # type: ignore
        info["company_address_postal_code"] = payment_form.company_info.address.postal_code # type: ignore
    
    info["billing_address_country"] = payment_form.billing_address.country # type: ignore
    info["billing_address_state"] = payment_form.billing_address.state # type: ignore
    info["billing_address_city"] = payment_form.billing_address.city # type: ignore
    info["billing_address_street_address"] = payment_form.billing_address.street_address # type: ignore
    info["billing_address_postal_code"] = payment_form.billing_address.postal_code # type: ignore

    
    info["buyer_address_country"] = payment_form.buyer.address.country # type: ignore
    info["buyer_address_state"] = payment_form.buyer.address.state # type: ignore
    info["buyer_address_city"] = payment_form.buyer.address.city # type: ignore
    info["buyer_address_street_address"] = payment_form.buyer.address.street_address # type: ignore
    info["buyer_address_postal_code"] = payment_form.buyer.address.postal_code # type: ignore
    info["gsm_number"] = payment_form.buyer.gsm_number # type: ignore


    billing_info = BillingInfo(**info)
    db.add(billing_info)
    db.commit()
    db.refresh(billing_info)
    return


def make_payment_or_409(iyzico_request, db, number_of_licenses, team_id):
    billing_cycle = (
        db.query(BillingCycle)
        .filter(BillingCycle.id == iyzico_request["basketItems"][0]["id"])
        .first()
    )
    payment = iyzipay.Payment().create(iyzico_request, iyzico_options)
    iyzico_return_json = payment.read().decode("utf-8")
    json_object = json.loads(iyzico_return_json)

    iyzico_status = json_object["status"]
    if iyzico_status == "failure":
        error_message = json_object["errorMessage"]
        error_code = json_object["errorCode"]
        print("(2bacf1cd)")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail("PAYMENT_GATEWAY_STATUS_FAILURE_I")
        )

    iyzico_paymentId = json_object["paymentId"]
    payment_transaction_id = json_object["itemTransactions"][0]["paymentTransactionId"]

    if (
        "paymentCard" in iyzico_request
        and "registerCard" in iyzico_request["paymentCard"]
        and int(iyzico_request["paymentCard"]["registerCard"]) == 1
    ):
        card_token = json_object["cardToken"]
        card_user_key = json_object["cardUserKey"]
        new_card = CreditCard()
        new_card.user_id = uuid.UUID(iyzico_request["buyer"]["id"])
        new_card.iyzico_credit_card_token_id = card_token
        new_card.iyzico_credit_card_user_key = card_user_key
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        # saving card

    paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "+03"
    iyzico_sent_json = payment_form_as_string(iyzico_request)

    new_purchase = Purchase()
    new_purchase.is_paid = True
    new_purchase.iyzico_returned_json = iyzico_return_json
    new_purchase.iyzico_sent_json = iyzico_sent_json
    new_purchase.number_of_licenses = number_of_licenses
    new_purchase.paid_at = paid_at
    new_purchase.iyzico_paymentId = iyzico_paymentId
    new_purchase.payment_transaction_id = payment_transaction_id
    new_purchase.payment_amount = iyzico_request["price"]
    new_purchase.team_id = team_id
    new_purchase.user_id = uuid.UUID(iyzico_request["buyer"]["id"])
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)

    team = db.query(Team).filter(Team.id == team_id)
    if team.first().number_of_licenses == 0:
        team.update(
            {
                "number_of_licenses": new_purchase.number_of_licenses,
                "billing_cycle_id": billing_cycle.id,
                "term_end_date": calculate_new_term_end(billing_cycle),
            }
        )
    else:
        current_license_number = team.first().number_of_licenses
        team.update(
            {
                "number_of_licenses": current_license_number
                + new_purchase.number_of_licenses
            }
        )
    db.commit()
    return {
        "status": json_object["status"],
        "price": json_object["price"],
        "paidPrice": json_object["paidPrice"],
        "installment": json_object["installment"],
        "paymentId": json_object["paymentId"],
    }


def prepare_recurring_billing_iyzico_request(
    user_id, team_id, db: Session = Depends(get_db)
):
    try:
        (
            user,
            team,
            billing_cycle,
            price,
            billing_info,
            credit_card,
        ) = check_recurring_billing_exceptions(user_id, team_id, db)
    except:
        return None
    
    card_dict = {
        "cardToken": credit_card.iyzico_credit_card_token_id,
        "cardUserKey": credit_card.iyzico_credit_card_user_key,
    }

    total_price = (
        price.price_per_month
        * billing_cycle.billing_period_in_months
        * team.number_of_licenses_next_term
    )
    
    iyzico_request = dict([("locale", "en")])
    iyzico_request["price"] = str(total_price)
    iyzico_request["paidPrice"] = str(total_price)
    iyzico_request["currency"] = "USD"
    iyzico_request["installment"] = "1"
    iyzico_request["paymentCard"] = card_dict # type: ignore


    current_buyer = dict([("id", str(user_id))])
    current_buyer["name"] = user.name
    current_buyer["surname"] = user.surname
    current_buyer["identityNumber"] = "74300864791"
    current_buyer["city"] = billing_info.buyer_address_city
    current_buyer["country"] = billing_info.buyer_address_country
    current_buyer["email"] = user.email
    current_buyer["ip"] = "85.34.78.112"
    current_buyer["registrationAddress"] = billing_info.buyer_address_street_address
    iyzico_request["buyer"] = current_buyer # type: ignore
    
    bill_address = dict([("address", billing_info.billing_address_street_address)])
    bill_address["city"] = billing_info.billing_address_city
    bill_address["country"] = billing_info.billing_address_country
    bill_address["contactName"] = user.name + " " + user.surname
    iyzico_request["billingAddress"] = bill_address # type: ignore

    iyzico_request["shippingAddress"] = bill_address # type: ignore
    
    bask_item = dict([("id", str(team.billing_cycle_id_next_term))])
    bask_item["itemType"] = "VIRTUAL"
    bask_item["name"] = "Billing Cycle id: " + str(
        team.billing_cycle_id_next_term
    )
    bask_item["category1"] = "Electronics"
    bask_item["price"] = str(total_price)

    bask_items = []
    bask_items.append(bask_item)
    iyzico_request["basketItems"] = bask_items # type: ignore
    return iyzico_request


def make_recurring_billing(user_id: uuid.UUID, team_id: uuid.UUID, db):
    try:
        check_recurring_billing_exceptions(user_id, team_id, db)
    except:
        return {"status": "failure"}
    
    team = db.query(Team).filter(Team.id == team_id)
    team.update({"number_of_licenses": 0})
    db.commit()
    
    iyzico_request = prepare_recurring_billing_iyzico_request(
        user_id, team_id, db
    )
    
    if not iyzico_request:
        return {"status": "failure"}
    
    payment_response = make_payment_or_409(
        iyzico_request, db, team.first().number_of_licenses_next_term, team_id
    )
    
    return payment_response


def luhn_card_control(card_number: str):
    card_number_list = []
    for i in range(16):
        card_number_list.append(int(card_number[i]))
    for i in range(8):
        card_number_list[i * 2] = card_number_list[i * 2] * 2
        if card_number_list[i * 2] > 9:
            card_number_list[i * 2] = card_number_list[i * 2] - 9
    sum = 0
    for i in range(15):
        sum += card_number_list[i]

    mode_10 = sum % 10
    if mode_10 == 0:
        last_number = 0
    else:
        last_number = 10 - mode_10
    if last_number == card_number_list[15]:
        return True
    return False

def is_card_expired(expireYear, expireMonth):
    now = datetime.now()
    exp_year_int = int(expireYear)
    exp_month_int = int(expireMonth)
    if exp_month_int == 12:
        exp_year_int += 1
        exp_month_int = 1
    else:
        exp_month_int += 1
    exp_date = datetime(exp_year_int, exp_month_int, 1)
    return now > exp_date

def calculate_new_term_end(billing_cycle):
    term_end = datetime.now() + relativedelta(
        months=billing_cycle.billing_period_in_months
    )
    return term_end.strftime("%Y-%m-%d %H:%M:%S.%f") + "+03"

def check_payment_exceptions_or_400_401_404_406(
    team_existing: Team,
    payment_form: schema.PaymentForm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):
    if payment_form.number_of_licenses < 1:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("AT_LEAST_I_LICENCE_REQUIRED_II")
        )


    if (
        team_existing.number_of_licenses < 1
        and payment_form.number_of_licenses < 1
    ):
        print("(ee737376)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("AT_LEAST_I_LICENCE_REQUIRED_III")
        )

    team_admin = (
        db.query(TeamParticipation)
        .filter(
            TeamParticipation.team_id == team_existing.id,
            TeamParticipation.user_id == current_user.id,
        )
        .first()
    )
    
    if not team_admin:
        print("(e2adcc92)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("USER_NOT_IN_TEAM")
        )
    
    if not team_admin.is_admin:
        print("(8315c732)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("USER_NOT_TEAM_ADMIN")
        )
    
    billing_cycle = (
        db.query(BillingCycle)
        .filter(BillingCycle.id == payment_form.billing_cycle_id)
        .first()
    )

    if not billing_cycle:
        print("(1d726909)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("BILLING_CYCLE_DOES_NOT_EXIST_III")
        )

    if not billing_cycle.is_active:
        print("(73db5171)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("BILLING_CYCLE_IS_NOT_ACTIVE_I")
        )

    ## TODO: check plan_id exists

    ## payment card checks
    if len(payment_form.payment_card.cardNumber) != 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("INVALID_CARD_NUMBER")
        )
    # do not merge if controls, this provide also length control for luhm algorithm function
    if not luhn_card_control(payment_form.payment_card.cardNumber):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("INVALID_CARD_NUMBER_II")
        )
    if is_card_expired(
        payment_form.payment_card.expireYear,
        payment_form.payment_card.expireMonth,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("INVALID_CARD_TIME_EXPIRED")
        )

    

    ## get the price from db
    price_db = (
        db.query(Price)
        .filter(
            Price.billing_cycle_id == payment_form.billing_cycle_id,
            Price.plan_id == payment_form.plan_id,
        )
        .first()
    )
    if not price_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("PRICING_DOES_NOT_EXIST")
        )

    return price_db, billing_cycle


def check_recurring_billing_exceptions(
    user_id: uuid.UUID, team_id: uuid.UUID, db
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise Exception("There is no user with id : " + str(user_id))
    
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise Exception("There is no team with id : " + str(team_id))
    
    if team.number_of_licenses_next_term <= 0:
        raise Exception("Number of license cannot be equal or lower than 0")

    next_billing_cycle = (
        db.query(BillingCycle)
        .filter(BillingCycle.id == team.billing_cycle_id_next_term)
        .first()
    )
    
    if not next_billing_cycle:
        raise Exception(
            "There is no billing cycle with id : " + str(next_billing_cycle)
        )
    
    if not next_billing_cycle.is_active:
        raise Exception("Selected billing cycle is not active.")
    
    pricing = (
        db.query(Price)
        .filter(
            Price.billing_cycle_id == next_billing_cycle.id,
            Price.plan_id == team.plan_id,
        )
        .first()
    )
    if not pricing:
        raise Exception("No pricing for selected billing cycle and plan.")
    
    billing_info = (
        db.query(BillingInfo).filter(BillingInfo.user_id == user_id).first()
    )
    if not billing_info:
        raise Exception("No billing info for user with id : " + str(user_id))
    
    credit_card = (
        db.query(CreditCard).filter(CreditCard.user_id == user_id).first()
    )
    if not credit_card:
        raise Exception(
            "No credit card info for user with id : " + str(user_id)
        )
    return user, team, next_billing_cycle, pricing, billing_info, credit_card


async def send_mail_to_team_admins(team_participiants, db):

    user_ids = []
    for team_participiant in team_participiants:
        user_ids.append(team_participiant.user_id)

    team_admins_emails = (
        db.query(User.email).filter(User.id.in_(user_ids)).all()
    )
    emails = [value[0] for value in team_admins_emails]
    message = MessageSchema(
        subject="Saasr Recurring Billing Failure",
        recipients=emails,
        body=f"""
        Greetings, your team's license has expired and there was an error in repurchasing. 
        We recommend you to check your card details. 
        
        If you have any other problem, please contact us through mail@example.com
        
        
        """,
    )
    await fm.send_message(message)
    return


async def send_exception_mail_to_superuser(team_id):
    message = MessageSchema(
        subject="Saasr Recurring Billing Failure",
        recipients=["erenekren7@gmail.com"],
        body=f"""
        An error occured in reccurring billing for team with id : {team_id}
        """,
    )
    await fm.send_message(message)
    return


def try_make_payment(team_id, db):
    team_participiants = (
        db.query(TeamParticipation)
        .filter(
            TeamParticipation.team_id == team_id,
            TeamParticipation.recurring_payer == True,
        )
        .order_by(TeamParticipation.created_at.asc())
        .all()
    )
    if not team_participiants:
        asyncio.run(send_exception_mail_to_superuser(team_id))
        return {"status": "failure"}
    for team_participiant in team_participiants:
        response = make_recurring_billing(
            team_participiant.user_id, team_id, db
        )
        if response["status"] == "success":
            return {"status": "success"}
    asyncio.run(send_exception_mail_to_superuser(team_id=team_id))
    asyncio.run(
        send_mail_to_team_admins(team_participiants=team_participiants, db=db)
    )


# ============ #
# payment_request_add_license_input_control( ):
# ============ #


def payment_request_add_license_input_control_or_401_404_406(
    team_id,
    number_of_licenses,
    db,
    current_user,
):

    team_existing: Team = db_get_item_or_error(team_id, Team, "Team", db)
   
    if (
        team_existing.number_of_licenses < 1
        and number_of_licenses < 1
    ):
        print("(e2d7)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("AT_LEAST_I_LICENCE_REQUIRED_V")
        )

    team_admin = (
        db.query(TeamParticipation)
        .filter(
            TeamParticipation.team_id == team_existing.id,
            TeamParticipation.user_id == current_user.id,
        )
        .first()
    )
    
    if not team_admin:
        print("(cb87)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("USER_NOT_IN_TEAM_II")
        )
    
    if not team_admin.is_admin:
        print("(2e94)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("USER_NOT_TEAM_ADMIN_II")
        )

    billing_cycle_id = team_existing.billing_cycle_id
    
    if not billing_cycle_id:
        print("(8104)")
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_detail("TEAM_HAS_NO_BILLING_CYCLE_ID")
            )
    billing_cycle = db_get_item_or_error(billing_cycle_id, BillingCycle, "Billing Cycle", db)

    plan_id = team_existing.plan_id
    if not plan_id:
        print("(1045)")
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_detail("TEAM_HAS_NO_VALID_PLAN")
            )

    ## get the price from db
    price_db = (
        db.query(Price)
        .filter(
            Price.billing_cycle_id == team_existing.billing_cycle_id,
            Price.plan_id == team_existing.plan_id,
        )
        .first()
    )
    if not price_db:
        print("(045b)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("PRICING_DOES_NOT_EXIST_III")
        )
    return team_existing,price_db,billing_cycle

