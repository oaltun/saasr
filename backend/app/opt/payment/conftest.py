import pytest
import requests
from app.opt.payment.schema import PaymentOutputInitialBuy
from app.opt.subscription.model import Price


def payment_data(name:str, surname:str, number_of_licenses: int, billing_cycle_id: str, plan_id: str):
    return {
        "number_of_licenses": number_of_licenses,
        "billing_cycle_id": billing_cycle_id,
        "plan_id":plan_id,
        "user_agrees_to_terms_and_conditions":True,
        "buyer": {
            "name": name,
            "surname": surname,
            "gsm_number": "23123123123",
            "address":{
                "country": "türkiye",
                "state":"",
                "city": "istanbul",
                "street_address": "str",
                "postal_code":"24321",
            }
        },
        "payment_card": {
            "cardHolderName": "abc def",
            "cardNumber": "5400010000000004",
            "expireYear": "2024",
            "expireMonth": "05",
            "cvc": "123",
            "registerCard": 1,
        },
        "billing_address": {
            "country": "USA",
            "state": "alabama",
            "city": "new york",
            "street_address": "asdf asdf",
            "postal_code": "12323"
        },
        "user_is_company_representer": True,
        "company_info": {
            "company_name": "Acme Corp",
            "company_tax_number": "1234",
            "company_tax_office": "321",
            "address": {
                "country": "USA",
                "state": "alabama",
                "city": "sdfsf",
                "street_address": "asdfsdf",
                "postal_code": "12323"
            },
        },
    }


@pytest.fixture
def initial_payment(initial_data,client, user_token_headers, test_db):
    name="Elton"
    surname="Smith"
    number_of_licenses = 3
    plan_id = "lite"
    billing_cycle_id = "1_month"
    
    res: requests.Response = client.post(
        "/api/v1/payment_request_initial_buy",
        json=payment_data(name,surname, number_of_licenses, billing_cycle_id,plan_id),
        headers=user_token_headers,
    )
    res_dict = res.json()


    payment = PaymentOutputInitialBuy(**res_dict)

    assert res.status_code == 200

    assert payment.payment_status == "success"

        ### assert paid price is right
    price_obj: Price = (
        test_db.query(Price)
        .filter(
            Price.billing_cycle_id == billing_cycle_id,
            Price.plan_id == plan_id,
        )
        .first()
    )
    price_per_month = price_obj.price_per_month
    billing_period_in_months = price_obj.billing_cycle.billing_period_in_months
    
    assert str(payment.paid_price) == str(
        price_per_month * billing_period_in_months * number_of_licenses
    )


    return payment



@pytest.fixture
def initial_payment_single_license(initial_data,client, user_token_headers, test_db):
    name="Elton"
    surname="Smith"
    number_of_licenses = 1
    plan_id = "lite"
    billing_cycle_id = "12_months"
    
    res: requests.Response = client.post(
        "/api/v1/payment_request_initial_buy",
        json=payment_data(name,surname, number_of_licenses, billing_cycle_id,plan_id),
        headers=user_token_headers,
    )
    res_dict = res.json()


    payment = PaymentOutputInitialBuy(**res_dict)

    assert res.status_code == 200

    assert payment.payment_status == "success"

        ### assert paid price is right
    price_obj: Price = (
        test_db.query(Price)
        .filter(
            Price.billing_cycle_id == billing_cycle_id,
            Price.plan_id == plan_id,
        )
        .first()
    )
    price_per_month = price_obj.price_per_month
    billing_period_in_months = price_obj.billing_cycle.billing_period_in_months
    
    assert str(payment.paid_price) == str(
        price_per_month * billing_period_in_months * number_of_licenses
    )


    return payment
