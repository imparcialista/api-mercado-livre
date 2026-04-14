import os
import requests

TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

payload = {
    "grant_type": "authorization_code",
    "client_id": os.environ["ML_CLIENT_ID"],
    "client_secret": os.environ["ML_CLIENT_SECRET"],
    "code": os.environ["ML_AUTH_CODE"],
    "redirect_uri": os.environ["ML_REDIRECT_URI"],
}

response = requests.post(TOKEN_URL, data=payload, timeout=30)
print(response.status_code)
print(response.json())
