from pydantic import BaseModel, ValidationError, validator
import uuid
from pydantic import BaseModel
from typing import Optional


class Price(BaseModel):
    price: str
    class Config:
        orm_mode = True

    @validator('price')
    def price_should_be_good(cls, price):
        f = float(price)
        return price



class Address(BaseModel):
    country: str
    state: Optional[str] = None
    city: str
    street_address: str
    postal_code: Optional[str] = None


class Buyer(BaseModel):
    name: str
    surname: str
    gsm_number: str
    address: Address

# class BillingAddress(BaseModel):
#     contactName: str
#     address: Address

class BasketItem(BaseModel):
    id: str
    itemType: str
    name: str
    category1: str
    price: float    

class CardBase(BaseModel):
    cardHolderName : str
    cardNumber : str
    expireYear : str
    expireMonth : str

class PaymentCard(CardBase):
    cvc : str
    registerCard : int = 1

class PaymentCardUpdate(CardBase):
    pass

class PaymentCardOut(BaseModel):
    lastFourDigits: str
  


class CompanyInfo(BaseModel):
    company_name: str
    company_tax_number: str
    company_tax_office: str
    address: Address

class PaymentForm(BaseModel):
    price: Optional[str] = None
    #currency : str
    number_of_licenses: int
    billing_cycle_id : str
    plan_id: str
    user_agrees_to_terms_and_conditions:bool=False
    
    buyer : Buyer
    payment_card : PaymentCard
    billing_address : Address
    user_is_company_representer: bool
    company_info: Optional[CompanyInfo]

class PaymentFormAddLicense(BaseModel):
    team_id: uuid.UUID
    number_of_licenses: int

    @validator('number_of_licenses')
    def number_of_licenses_must_be_gt_zero(cls, v:int):
        if v<1:
            raise ValueError('must be greater than zero')
        return v

class PaymentRespondParameters(BaseModel):
    checkoutFormContent: str
    paymentPageUrl: str
    token: str
    tokenExpireTime: int
    status: str
    errorCode: str
    errorMessage: str
    errorGroup: str
    locale: str
    systemTime: int
    conversationId: str

class PaymentCancelForm(BaseModel):
    ip: Optional[str] = None
    team_id: uuid.UUID
    purchase_id: uuid.UUID 
    user_id: uuid.UUID # cancel işlemini site yöneticisi yapacağı için eklendi

class PaymentOutputAddLicense(BaseModel):
    payment_status:str
    paid_price: str
    iyzico_paymentId: str
    team_id : uuid.UUID 
    billing_cycle_id : str
    plan_id : str
    purchase_id : uuid.UUID 
    user_id : uuid.UUID
    team_number_of_licenses: int 

class PaymentOutputInitialBuy(BaseModel):
    payment_status:str
    paid_price: str
    iyzico_paymentId: str
    team_id : uuid.UUID 
    billing_cycle_id : str
    plan_id : str
    purchase_id : uuid.UUID 
    user_id : uuid.UUID
    team_number_of_licenses: int 
