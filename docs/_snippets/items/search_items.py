import os
import requests

BASE_URL = "https://api.mercadolibre.com"
headers = {"Authorization": f"Bearer {os.environ['ML_ACCESS_TOKEN']}"}

params = {
    "limit": 50,
    "offset": 0,
    "status": "active",
}

user_id = os.environ["ML_USER_ID"]
resp = requests.get(f"{BASE_URL}/users/{user_id}/items/search", params=params, headers=headers, timeout=30)
print(resp.status_code)
print(resp.json())
