import requests
from app.opt.payment.schema import PaymentCardOut,  PaymentOutputInitialBuy

    

def test_card_change(initial_payment:PaymentOutputInitialBuy,client,user_token_headers,test_db):

    card_info = {
        'cardHolderName': 'John Doe',
        'cardNumber': '5528790000000008',
        'expireMonth': '12',
        'expireYear': '2030'
    }

    res: requests.Response = client.post(
        "/api/v1/card_change",
        headers=user_token_headers,
        json=card_info,
    )
    res_dict = res.json()
 
    assert res.status_code == 201

    card = PaymentCardOut(**res_dict)

    assert card.lastFourDigits == card_info['cardNumber'][-4:]

def test_card_get(initial_payment:PaymentOutputInitialBuy,client,user_token_headers,test_db):

    res: requests.Response = client.get(
        "/api/v1/card_get",
        headers=user_token_headers,
    )
    res_dict = res.json()
    assert res.status_code == 200

    card = PaymentCardOut(**res_dict)

    assert card.lastFourDigits=='0004'
