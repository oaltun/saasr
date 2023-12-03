from uuid import UUID

import requests


from app.opt.subscription.model import Price
from app.team.model import Team
from app.opt.payment.schema import PaymentOutputAddLicense, PaymentOutputInitialBuy

    
def test_payment_request_initial_buy(initial_payment,client, user_token_headers, test_db):
    payment = initial_payment

def test_payment_request_add_license(initial_payment:PaymentOutputInitialBuy,client,user_token_headers,test_db):
    number_of_licenses_to_add = 2
   
    res: requests.Response = client.post(
        "/api/v1/payment_request_add_license",
        json={
            "team_id": str(initial_payment.team_id),
            "number_of_licenses": number_of_licenses_to_add
        },
        headers=user_token_headers,
    )
    res_dict = res.json()
  


    assert res.status_code == 200

    payment = PaymentOutputAddLicense(**res_dict)
    assert payment.payment_status == "success"
    assert payment.team_number_of_licenses== initial_payment.team_number_of_licenses + number_of_licenses_to_add 
   