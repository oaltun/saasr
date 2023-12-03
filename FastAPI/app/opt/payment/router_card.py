import json
from typing import cast
import uuid
from app.core.schema import ErrorDetail
from app.opt.payment.schema import PaymentCardUpdate, PaymentCardOut
from app.opt.payment.model import CreditCard
from app.core.crud import  raise_if
from app.core.error import error_detail
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import iyzipay

from app.core.auth import get_current_active_user_or_400
from app.core.session import get_db
from app.user.model import User
from app.opt.payment.crud import iyzico_options

card_router = router = APIRouter(prefix="")

# ============================================================================ #
# - Create Card Endpoint
# ============================================================================ #

@router.post(
    "/card_change",
    status_code=status.HTTP_201_CREATED,
    response_model=PaymentCardOut,
    responses={
        400: {"model": ErrorDetail },
    },
    description="create card or change",
)
def card_change(
    input: PaymentCardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):

    # ============================================================================ #
    # Get the old card info if exists

    card_existing:CreditCard = cast(CreditCard,
        db.query(CreditCard).filter(CreditCard.user_id==current_user.id).first()
    )
    raise_if(not card_existing, 400, "USER_DOES_NOT_HAVE_A_CREDIT_CARD")

    # ============================================================================ #
    # Prepare a new card info

    new_card_info = {
        'cardHolderName': input.cardHolderName,
        'cardNumber': input.cardNumber,
        'expireMonth': input.expireMonth,
        'expireYear': input.expireYear
    }


    iyzico_create_request = {
        'locale': 'en',
        'card': new_card_info,
        'cardUserKey': card_existing.iyzico_credit_card_user_key
    }
     
    # ============================================================================ #
    # Create the new card on iyzico

    iyzico_create_request_r = iyzipay.Card().create(iyzico_create_request, iyzico_options)
    iyzico_create_response_str = iyzico_create_request_r.read().decode('utf-8')
    iyzico_create_response = json.loads(iyzico_create_response_str)

    if not iyzico_create_response["status"]=="success":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("PAYMENT_GATEWAY_STATUS_NOT_SUCCESS")
        )
    new_card_token = iyzico_create_response["cardToken"]
    print("existing card user key: ",card_existing.iyzico_credit_card_user_key)
    print("new card iyzico info: ", iyzico_create_response_str)

    # ============================================================================ #
    # Delete old card in iyzico

    iyzico_delete_request = {
        'locale': 'en',
        'cardToken': card_existing.iyzico_credit_card_token_id,
        'cardUserKey': card_existing.iyzico_credit_card_user_key
    }

    iyzico_delete_request_r = iyzipay.Card().delete(iyzico_delete_request, iyzico_options)
    iyzico_delete_response_str = iyzico_delete_request_r.read().decode('utf-8')
    iyzico_delete_response = json.loads(iyzico_delete_response_str)
    if not iyzico_delete_response["status"]=="success":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail("PAYMENT_GATEWAY_CARD_DELETE_STATUS_NOT_SUCCESS")
        )    

    # ============================================================================ #
    # Update card in our db
    card_existing.iyzico_credit_card_token_id = new_card_token
    db.commit()
    db.refresh(card_existing)
        
    # ============================================================================ #
    # Return

    return PaymentCardOut(
        lastFourDigits = iyzico_create_response["lastFourDigits"],
    )

# ============================================================================ #
# - Get the card info
# ============================================================================ #

@router.get(
    "/card_get", 
    response_model=PaymentCardOut,
    responses={
        400: {"model": ErrorDetail },
    }
)
def card_get(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_or_400),
):
    card = db.query(CreditCard).filter(CreditCard.user_id==current_user.id).first()
    raise_if(not card, 400, "USER_DOES_NOT_HAVE_A_CREDIT_CARD_II")
    card = cast(CreditCard,card)

    request = {
        'locale': 'en',
        'cardUserKey': card.iyzico_credit_card_user_key
    }

    card_list = iyzipay.CardList().retrieve(request, iyzico_options)
    card_dict = json.loads(card_list.read().decode('utf-8'))
    
    return PaymentCardOut(
        lastFourDigits=card_dict['cardDetails'][0]['lastFourDigits']
    )