"""Renova access token no Mercado Livre usando refresh token.

Uso (PowerShell):
  $env:ML_CLIENT_ID='...'
  $env:ML_CLIENT_SECRET='...'
  $env:ML_REFRESH_TOKEN='...'
  python examples/oauth_refresh_token.py
"""

from __future__ import annotations

import os
import sys

import requests

TOKEN_URL = "https://api.mercadolibre.com/oauth/token"


def getenv_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"Variavel obrigatoria ausente: {name}")
        sys.exit(1)
    return value


def main() -> None:
    payload = {
        "grant_type": "refresh_token",
        "client_id": getenv_required("ML_CLIENT_ID"),
        "client_secret": getenv_required("ML_CLIENT_SECRET"),
        "refresh_token": getenv_required("ML_REFRESH_TOKEN"),
    }

    response = requests.post(
        TOKEN_URL,
        data=payload,
        headers={
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        },
        timeout=30,
    )

    print(f"HTTP {response.status_code}")
    try:
        data = response.json()
    except ValueError:
        print(response.text)
        sys.exit(1)

    if response.ok:
        print("new_access_token:", data.get("access_token"))
        print("new_refresh_token:", data.get("refresh_token"))
        print("expires_in:", data.get("expires_in"))
    else:
        print(data)
        sys.exit(1)


if __name__ == "__main__":
    main()
