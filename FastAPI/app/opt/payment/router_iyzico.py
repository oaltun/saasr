from datetime import datetime
from typing import Dict, Union, cast

import uuid
from app.core.auth import get_current_active_user_or_400
from app.core.schema import ErrorDetail
from app.core.session import get_db
from app.opt.payment.model import CreditCard, Purchase,BillingInfo
from app.team.model import Team, TeamParticipation

from app.user.model import User
from app.core.auth import get_current_active_superuser_or_403
from app.team.crud import create_team
from app.opt.subscription.model import BillingCycle, Plan, Price
from app.core.error import error_detail
import iyzipay
import json
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter, Depends, status,  Request, HTTPException


from app.opt.payment import schema
from app.opt.payment.crud import (
    calculate_new_term_end,
    iyzico_options,
    calculate_additional_subscription_price_or_409,
    payment_request_add_license_input_control_or_401_404_406,
    is_purchase_expired,
    payment_form_as_string,
    save_user_infos_to_db,
)


payment_router = router = APIRouter()






# =============================
# /payment_request_initial_buy:
# =============================

@router.post(
    "/payment_request_initial_buy",
    response_model=schema.PaymentOutputInitialBuy,
    responses={
        400: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
        406: {"model": ErrorDetail },
        409: {"model": ErrorDetail },
    }
)
def payment_request_initial_buy(
    payment_form: schema.PaymentForm,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    # ============ #
    #     Input validation
    if not payment_form.user_agrees_to_terms_and_conditions:
        print("(v1234d8)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("USER_NEEDS_TO_ACCEPT_CONDITIONS")
        )
 
    if payment_form.payment_card.registerCard != 1:
        print("(a2b2f4d8)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("CARD_NEEDS_TO_BE_REGISTERED")
        )
 
    if payment_form.number_of_licenses < 1:
        print("(e5a3)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("AT_LEAST_I_LICENCE_REQUIRED_IV")
        )

    
    billing_cycle = (
        db.query(BillingCycle)
        .filter(BillingCycle.id == payment_form.billing_cycle_id)
        .first()
    )


    if not billing_cycle:
        print("(4167)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("BILLING_CYCLE_DOES_NOT_EXIST_IV")
        )

    if not billing_cycle.is_active:
        print("(9e0e)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("BILLING_CYCLE_IS_NOT_ACTIVE_II")
        )

    plan = (
        db.query(Plan)
        .filter(Plan.id == payment_form.plan_id)
        .first()
    )

    if not plan:
        print("(6548)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("PLAN_DOES_NOT_EXIST_III")
        )

    if not plan.is_active:
        print("(49c0)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("PLAN_IS_NOT_ACTIVE")
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
        print("(98ba)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("PRICING_DOES_NOT_EXIST_II")
        )

    price_per_license = price_db.price_per_month * billing_cycle.billing_period_in_months
        

    total_price = (price_per_license * payment_form.number_of_licenses) 
    total_price_str = str(round(total_price, 2))
    if payment_form.price and str(payment_form.price) !=  total_price_str:
        print("(d810)")
        raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_detail("PRICE_TOTAL_WRONG")
            )

    # ============ 
    #     Create iyzico request dict

    iyzico_request = dict()

    
    iyzico_request["locale"] = "en"
    iyzico_request["price"] = total_price_str
    iyzico_request["paidPrice"] = total_price_str
    iyzico_request["currency"] = "USD"
    iyzico_request["installment"] = "1"

    paym_card = dict([("cardNumber", payment_form.payment_card.cardNumber)])
    paym_card["expireYear"] = payment_form.payment_card.expireYear
    paym_card["expireMonth"] = payment_form.payment_card.expireMonth
    paym_card["cvc"] = payment_form.payment_card.cvc
    paym_card["cardHolderName"] = payment_form.payment_card.cardHolderName
    paym_card["registerCard"] = "1"
    iyzico_request["paymentCard"]= paym_card # type: ignore

    current_buyer = dict([("id", str(current_user.id))])
    current_buyer["name"] = payment_form.buyer.name
    current_buyer["surname"] = payment_form.buyer.surname
    if payment_form.buyer.gsm_number:
        current_buyer["gsm_number"] = payment_form.buyer.gsm_number
    current_buyer["email"] = current_user.email  # type: ignore
    current_buyer["identityNumber"] = "74300864791"
    # current_buyer["lastLoginDate"] = '2015-10-05 12:43:35'
    if payment_form.buyer.address.state:
        current_buyer["registrationAddress"] = payment_form.buyer.address.street_address + ", State: "+payment_form.buyer.address.state
    else:
        current_buyer["registrationAddress"] = payment_form.buyer.address.street_address
    current_buyer["ip"] = '85.34.78.112' # ip
    current_buyer["city"] = payment_form.buyer.address.city
    current_buyer["country"] = payment_form.buyer.address.country
    if payment_form.buyer.address.postal_code:
        current_buyer["zipCode"] = payment_form.buyer.address.postal_code
    iyzico_request["buyer"] = current_buyer  # type: ignore

    
    bill_address=dict()
    bill_address["contactName"] = payment_form.buyer.name + " "+payment_form.buyer.surname
    bill_address["city"] = payment_form.billing_address.city
    bill_address["country"] = payment_form.billing_address.country
    if payment_form.billing_address.state:
        bill_address["address"]= payment_form.billing_address.street_address + ", State: " +payment_form.billing_address.state
    else:
        bill_address["address"]= payment_form.billing_address.street_address

    if payment_form.billing_address.postal_code:
        bill_address["zipCode"]= payment_form.billing_address.postal_code
#    iyzico_request["billingAddress"] = bill_address
    iyzico_request["billingAddress"] = bill_address  # type: ignore
    iyzico_request["shippingAddress"] = bill_address  # type: ignore

    bask_item = dict([("id", str(payment_form.billing_cycle_id))])
    bask_item["itemType"] = "VIRTUAL"
    bask_item["name"] = "Billing Cycle id: " + str(payment_form.billing_cycle_id)
    bask_item["category1"] = "Electronics"
    bask_item["price"] = total_price_str
    bask_items = []
    bask_items.append(bask_item)
    iyzico_request["basketItems"] = bask_items  # type: ignore


    # ============ #
    #     Get paid

    payment = iyzipay.Payment().create(iyzico_request, iyzico_options)
    iyzico_return_json = payment.read().decode("utf-8")
    iyzico_returned_json_object = json.loads(iyzico_return_json)
    iyzico_status = iyzico_returned_json_object["status"]
    if iyzico_status == "failure":
        error_message = iyzico_returned_json_object["errorMessage"]
        error_code = iyzico_returned_json_object["errorCode"]
        print("(45ba)")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail("PAYMENT_GATEWAY_STATUS_FAILURE_II")
        )

    iyzico_paymentId = iyzico_returned_json_object["paymentId"]
    payment_transaction_id = iyzico_returned_json_object["itemTransactions"][0]["paymentTransactionId"]

    # TODO: paid_at = db.query(func.now()).scalar()
    paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "+03"
    iyzico_sent_json = payment_form_as_string(iyzico_request)


    # ============ #
    #     Save card to our db


    if (
        "paymentCard" in iyzico_request
        and "registerCard" in iyzico_request["paymentCard"]
        and int(iyzico_request["paymentCard"]["registerCard"]) == 1
    ):
        card_token = iyzico_returned_json_object["cardToken"]
        card_user_key = iyzico_returned_json_object["cardUserKey"]
        new_card = CreditCard()
        new_card.user_id = uuid.UUID(iyzico_request["buyer"]["id"])  # type: ignore
        new_card.iyzico_credit_card_token_id = card_token
        new_card.iyzico_credit_card_user_key = card_user_key
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        # saving card

    # ============ #
    #     Create a new team and save it to db


    team: Team = create_team({
        "plan_id":plan.id,
        "plan_id_next_term":plan.id,
        "billing_cycle_id": billing_cycle.id,
        "billing_cycle_id_next_term":billing_cycle.id,
        "number_of_licenses":payment_form.number_of_licenses,
        "number_of_licenses_next_term": payment_form.number_of_licenses,
        "recurring_billing_is_on": True,
        "term_end_date": calculate_new_term_end(billing_cycle),
    },current_user,db)

    # ============ #
    #     Purchase info in db

    new_purchase = Purchase()
    new_purchase.is_paid = True # type: ignore
    new_purchase.iyzico_returned_json = iyzico_return_json
    new_purchase.iyzico_sent_json = iyzico_sent_json
    new_purchase.number_of_licenses = payment_form.number_of_licenses # type: ignore
    new_purchase.paid_at = paid_at# type: ignore
    new_purchase.iyzico_paymentId = iyzico_paymentId
    new_purchase.payment_transaction_id = payment_transaction_id
    new_purchase.payment_amount = iyzico_request["price"]# type: ignore
    new_purchase.team_id = team.id
    new_purchase.user_id = current_user.id
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)

    # ============ #
    #     Save billing info to db
    save_user_infos_to_db(payment_form, current_user, db)


    # ============ #
    #     Return

    output= schema.PaymentOutputInitialBuy(
        payment_status=iyzico_returned_json_object["status"],
        paid_price= iyzico_returned_json_object["paidPrice"],
        iyzico_paymentId= iyzico_returned_json_object["paymentId"],
        team_id = team.id,
        billing_cycle_id = team.billing_cycle_id,
        plan_id = team.plan_id,
        purchase_id = new_purchase.id,
        user_id = current_user.id,
        team_number_of_licenses = team.number_of_licenses
    )
   
    return output





# ============ #
#/payment_request_current_price:
# ============ #


@router.get(
    "/payment_request_current_price", 
    response_model=schema.Price,
    responses={
        400: {"model": ErrorDetail },
        401: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
        406: {"model": ErrorDetail },
        409: {"model": ErrorDetail },
    }

)
def payment_request_current_price(
    team_id,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    team_existing,price_db,billing_cycle,  =payment_request_add_license_input_control_or_401_404_406(
        team_id,
        1, 
        db,
        current_user
    )

    price_per_license = 0
    if team_existing.number_of_licenses == 0:
        price_per_license = (
            price_db.price_per_month * billing_cycle.billing_period_in_months
        )
    else:
        # eğer aktif kullanımda lisans varsa, 
        # termin bitime kadar olan günler kadar total price çıkartır
        price_per_license = calculate_additional_subscription_price_or_409(team_existing, db)
        if price_per_license == 0:
            print("(d4ab)")
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_detail("NO_PURCHASES_ON_TERM_END_DAY")
            )
    if price_per_license <= 0:
        print("(4ab0)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("PRICE_MORE_THAN_ZERO")
        )

    price_per_license_str = str(round(price_per_license, 2))
    return schema.Price(price=price_per_license_str)









# ============ #
# /payment_request_add_license:
# ============ #

@router.post(
    "/payment_request_add_license", 
    response_model=schema.PaymentOutputAddLicense,
    responses={
        400: {"model": ErrorDetail },
        406: {"model": ErrorDetail },
        409: {"model": ErrorDetail },
    }
)
def payment_request_add_license(
    payment_form: schema.PaymentFormAddLicense,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    team_existing,price_db,billing_cycle,  =payment_request_add_license_input_control_or_401_404_406(
        payment_form.team_id,
        payment_form.number_of_licenses, 
        db,
        current_user
    )

    if team_existing.number_of_licenses == 0:
        price_per_license = (
            price_db.price_per_month * billing_cycle.billing_period_in_months
        )
    else:
        # eğer aktif kullanımda lisans varsa, 
        # termin bitime kadar olan günler kadar total price çıkartır
        price_per_license = calculate_additional_subscription_price_or_409(team_existing, db)
        if price_per_license == 0:
            print("(d4ab)")
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=error_detail("NO_PURCHASES_ON_TERM_END_DAY")
            )
    if price_per_license <= 0:
        print("(4ab0)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("PRICE_MORE_THAN_ZERO")
        )

    total_price = (price_per_license * payment_form.number_of_licenses) 
    total_price_str = str(round(total_price, 2))

    # ============ #
    #     Iyzico request preparation
    
    credit_card = (
        db.query(CreditCard).filter(CreditCard.user_id == current_user.id).first()
    )
    if not credit_card:
        raise Exception(
            "No credit card info for user with id : " + str(current_user.id)
        )

    card_dict = {
        "cardToken": credit_card.iyzico_credit_card_token_id,
        "cardUserKey": credit_card.iyzico_credit_card_user_key,
    }
    
    iyzico_request = dict([("locale", "en")])
    iyzico_request["price"] = total_price_str
    iyzico_request["paidPrice"] = total_price_str
    iyzico_request["currency"] = "USD"
    iyzico_request["installment"] = "1"
    iyzico_request["paymentCard"] = card_dict# type: ignore

    
    billing_info :BillingInfo= (
        db.query(BillingInfo).filter(BillingInfo.user_id == current_user.id).first()
    )
    print(billing_info)
    if not billing_info:
        raise Exception("No billing info for user with id : " + str(current_user.id))

    current_buyer = dict([("id", str(current_user.id))])
    current_buyer["name"] = current_user.name# type: ignore
    current_buyer["surname"] = current_user.surname# type: ignore
    if billing_info.gsm_number:
        current_buyer["gsm_number"] = billing_info.gsm_number# type: ignore
    current_buyer["email"] = current_user.email# type: ignore
    current_buyer["identityNumber"] = "74300864791"
    if billing_info.buyer_address_state:
        current_buyer["registrationAddress"] = billing_info.buyer_address_street_address + ", State: "+billing_info.buyer_address_state# type: ignore
    else:
        current_buyer["registrationAddress"] = billing_info.buyer_address_street_address# type: ignore
    current_buyer["ip"] = "85.34.78.112"
    current_buyer["city"] = billing_info.buyer_address_city # type: ignore
    current_buyer["country"] = billing_info.buyer_address_country # type: ignore
    if billing_info.buyer_address_postal_code:
        current_buyer["zipCode"] = billing_info.buyer_address_postal_code # type: ignore
    iyzico_request["buyer"] = current_buyer # type: ignore
    
    bill_address=dict()
    bill_address["contactName"] = current_user.name + " " + current_user.surname
    bill_address["city"] = billing_info.billing_address_city
    bill_address["country"] = billing_info.billing_address_country
    if billing_info.billing_address_state:
        bill_address["address"]= billing_info.billing_address_street_address + ", State: " +billing_info.billing_address_state
    else:
        bill_address["address"]= billing_info.billing_address_street_address
    if billing_info.billing_address_postal_code:
        bill_address["zipCode"]= billing_info.billing_address_postal_code
    iyzico_request["billingAddress"] = bill_address # type: ignore
    iyzico_request["shippingAddress"] = bill_address # type: ignore
    
    bask_item = dict([("id", str(team_existing.billing_cycle_id))])
    bask_item["itemType"] = "VIRTUAL"
    bask_item["name"] = "Billing Cycle id: " + str(
        team_existing.billing_cycle_id
    )
    bask_item["category1"] = "Electronics"
    bask_item["price"] = total_price_str
    bask_items = []
    bask_items.append(bask_item)
    iyzico_request["basketItems"] = bask_items # type: ignore

    # ============ #
    #     Make payment

    payment = iyzipay.Payment().create(iyzico_request, iyzico_options)
    iyzico_return_json = payment.read().decode("utf-8")
    iyzico_returned_json_object = json.loads(iyzico_return_json)

    iyzico_status = iyzico_returned_json_object["status"]
    if iyzico_status == "failure":
        error_message = iyzico_returned_json_object["errorMessage"]
        error_code = iyzico_returned_json_object["errorCode"]
        print("(ab0d)")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail("PAYMENT_GATEWAY_STATUS_FAILURE_IV")
        )

    iyzico_paymentId = iyzico_returned_json_object["paymentId"]
    payment_transaction_id = iyzico_returned_json_object["itemTransactions"][0]["paymentTransactionId"]
    paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "+03"
    iyzico_sent_json = payment_form_as_string(iyzico_request)

    # ============ #
    #     Team info update
    
    new_license_count = team_existing.number_of_licenses + payment_form.number_of_licenses
    team_existing.number_of_licenses = new_license_count
    team_existing.number_of_licenses = new_license_count
    db.commit()
    db.refresh(team_existing)
    
    # ============ #
    #     Purchase info addition 
    new_purchase = Purchase()
    new_purchase.is_paid = True # type: ignore
    new_purchase.iyzico_returned_json = iyzico_return_json
    new_purchase.iyzico_sent_json = iyzico_sent_json
    new_purchase.number_of_licenses = payment_form.number_of_licenses # type: ignore
    new_purchase.paid_at = paid_at # type: ignore
    new_purchase.iyzico_paymentId = iyzico_paymentId
    new_purchase.payment_transaction_id = payment_transaction_id
    new_purchase.payment_amount = total_price_str # type: ignore
    new_purchase.team_id = team_existing.id
    new_purchase.user_id = current_user.id
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)




    # save_user_infos_to_db(payment_form, current_user, db)
    # ============ #
    #     Return

    output= schema.PaymentOutputAddLicense(
        payment_status=iyzico_returned_json_object["status"],
        paid_price= iyzico_returned_json_object["paidPrice"],
        iyzico_paymentId= iyzico_returned_json_object["paymentId"],
        team_id = team_existing.id,
        billing_cycle_id = team_existing.billing_cycle_id,
        plan_id = team_existing.plan_id,
        purchase_id = new_purchase.id,
        user_id = current_user.id,
        team_number_of_licenses = team_existing.number_of_licenses
    )
   
    return output






####iptal ve refund kısmı henüz tamamlanmadı.
@router.post(
    "/payment_cancel",
    responses={
        401: {"model": ErrorDetail },
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
        406: {"model": ErrorDetail },
        409: {"model": ErrorDetail },
    }
)
def payment_cancel(  # is_paid refund edildi yerine geçer mi?
    # refund ederken, takımdaki kullanıcı sayısına bak, eğer lisans sayısı aktif kullanıcı sayısından daha az oluyorsa exception oluştur
    cancel_form: schema.PaymentCancelForm,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser_or_403),
):
    if not current_user.is_superuser:
        print("(b0df)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("PURCHASE_CANCEL_NOT_ACCESIBLE")
        )
    team_existing: Team = (
        db.query(Team).filter(Team.id == cancel_form.team_id).first()
    )

    if not team_existing:
        print("(0dfb)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error_detail("TEAM_DOES_NOT_EXIST")
        )
    
    user_existing = (
        db.query(User).filter(User.id == cancel_form.user_id).first()
    )
    if not user_existing:
        print("(f552)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error_detail("USER_DOES_NOT_EXIST")
        )
    
    team_admin: TeamParticipation = (
        db.query(TeamParticipation)
        .filter(
            TeamParticipation.team_id == cancel_form.team_id,
            TeamParticipation.user_id == cancel_form.user_id,
        )
        .first()
    )
    
    if not team_admin:
        print("(45ef)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("USER_NOT_TEAM_ADMIN_III")
        )
    
    if not team_admin.is_admin:
        print("(bf8b)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("USER_NOT_TEAM_ADMIN_VI")
        )

    purchase: Union[Purchase,None] = (
        db.query(Purchase)
        .filter(Purchase.id == cancel_form.purchase_id)
        .first()
    )
    if not purchase:
        print("(535b)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error_detail("PURCHASE_DOES_NOT_EXIST")
        )

    if is_purchase_expired(team_existing.term_end_date):
        print("(35ba)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("PURCHASE_EXPIRED")
        )
    team_licensers = (
        db.query(TeamParticipation)
        .filter(TeamParticipation.is_admin == False)
        .all()
    )
    if team_licensers and (
        len(team_licensers)
        > (team_existing.number_of_licenses - purchase.number_of_licenses)
    ):
        print("(5ba1)")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=error_detail("MEMBER_COUNT_WOULD_BE_MORE_THAN_LICENSE_COUNT_IV")
        )
    cancel_request = dict([("locale", "en")])
    cancel_request["paymentId"] = purchase.iyzico_paymentId # type: ignore
    cancel_request["ip"] = request.client.host # type: ignore 
    cancel_request["reason"] = "other"
    cancel_request["description"] = "nothing"
    cancel = iyzipay.Cancel()
    cancel_response = cancel.create(cancel_request, iyzico_options)
    cancel_resp_dict = json.loads(cancel_response.read().decode("utf-8"))
    if cancel_resp_dict["status"] == "failure":
        print("(ba15)")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail("PAYMENT_GATEWAY_CANCEL_STATUS_FAILURE_I")
        )
    updated_inv = db.query(Purchase).filter(
        Purchase.id == cancel_form.purchase_id
    )
    updated_inv.update({"is_refunded": True})
    db.commit()
    team_qry = db.query(Team).filter(Team.id == cancel_form.team_id)
    team = team_qry.first() 
    if team is None:
        raise HTTPException(
            status_code=404,
            detail=error_detail("TEAM_DOES_NOT_EXIST_II")
        )
    team = cast(Team,team)
    
    if team.number_of_licenses == purchase.number_of_licenses:
        team_qry.update(
            {
                "number_of_licenses": 0, 
                "term_end_date": None
            }
        )
    else:
        numb_of_licenses = team.number_of_licenses
        team_qry.update(
            {
                "number_of_licenses": numb_of_licenses
                - purchase.number_of_licenses
            }
        )
    db.commit()
    return


@router.post(
    "/payment_refund",
    responses={
        401: {"model": ErrorDetail },
        403: {"model": ErrorDetail },
        404: {"model": ErrorDetail },
        409: {"model": ErrorDetail },
    }
)
def payment_refund(
    refund_form: schema.PaymentCancelForm,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser_or_403),
):
    if not current_user.is_superuser:
        print("(a151)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail("USER_NOT_SUPERUSER_I")
        )
    team_existing = (
        db.query(Team).filter(Team.id == refund_form.team_id).first()
    )
    if not team_existing:
        print("(151b)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error_detail("TEAM_DOES_NOT_EXIST_I")
        )
    team_admin = (
        db.query(TeamParticipation)
        .filter(
            TeamParticipation.team_id == refund_form.team_id,
            TeamParticipation.user_id == refund_form.user_id,
            TeamParticipation.is_admin == True,
        )
        .first()
    )
    if not team_admin:
        print("(51b7)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("USER_NOT_TEAM_ADMIN_IV")
        )
    purchase = (
        db.query(Purchase)
        .filter(Purchase.id == refund_form.purchase_id)
        .first()
    )
    if not purchase:
        print("(1b7b)")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=error_detail("PURCHASE_DOES_NOT_EXIST_II")
        )

    refund_request = dict([("locale", "en")])
    refund_request["paymentTransactionId"] = purchase.payment_transaction_id # type: ignore
    refund_request["ip"] = request.client.host # type: ignore
    refund_price = calculate_additional_subscription_price_or_409(team_existing, db)
    refund_request["price"] = str(round(refund_price, 2))
    refund = iyzipay.Refund()
    refund_response = refund.create(refund_request, iyzico_options)
    refund_resp_dict = json.loads(refund_response.read().decode("utf-8"))

    if refund_resp_dict["status"] == "failure":
        print("(b7bf )")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_detail("PAYMENT_GATEWAY_REFUND_STATUS_FAILURE_I")
        )

    updated_inv = db.query(Purchase).filter(
        Purchase.id == refund_form.purchase_id
    )
    updated_inv.update({"is_refunded": True})
    db.commit()
    team_qry = db.query(Team).filter(Team.id == refund_form.team_id)
    team=team_qry.first()
    if team is None:
        raise HTTPException(
            status_code=404,
            detail=error_detail("TEAM_DOES_NOT_EXIST_III")
        )
    team = cast(Team,team)
    

    if team.number_of_licenses == purchase.number_of_licenses:
        team_qry.update(
            {
                "number_of_licenses": 0, 
                "term_end_date": None
            }
        )
    else:
        numb_of_licenses = team.number_of_licenses
        team_qry.update(
            {
                "number_of_licenses": numb_of_licenses
                - purchase.number_of_licenses
            }
        )
    db.commit()
    return
