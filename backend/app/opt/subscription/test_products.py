
from fastapi.testclient import TestClient
import requests

from app.opt.subscription.schema import PriceOut


def test_get_price(product_info, client: TestClient):
    response: requests.Response = client.get("/api/v1/subscription_prices")

    response_dict = response.json()
    price = PriceOut(**response_dict[0])

    assert response.status_code == 200
