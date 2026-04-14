import os
import requests

BASE_URL = "https://api.mercadolibre.com"
headers = {"Authorization": f"Bearer {os.environ['ML_ACCESS_TOKEN']}"}

params = {
    "seller": os.environ["ML_SELLER_ID"],
    "order.status": "paid",
    "sort": "date_desc",
    "limit": 50,
    "offset": 0,
}

resp = requests.get(f"{BASE_URL}/orders/search", params=params, headers=headers, timeout=30)
print(resp.status_code)
print(resp.json())
