"""Troca authorization code por access token no Mercado Livre.

Uso (PowerShell):
  $env:ML_CLIENT_ID='...'
  $env:ML_CLIENT_SECRET='...'
  $env:ML_REDIRECT_URI='https://seu-app/callback'
  $env:ML_AUTH_CODE='TG-...'
  # Opcional (se PKCE estiver ativo no app):
  # $env:ML_CODE_VERIFIER='...'
  python examples/oauth_exchange_token.py
"""

from __future__ import annotations

import os
import sys
from typing import Dict

import requests

TOKEN_URL = "https://api.mercadolibre.com/oauth/token"


def getenv_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"Variavel obrigatoria ausente: {name}")
        sys.exit(1)
    return value


def build_payload() -> Dict[str, str]:
    payload = {
        "grant_type": "authorization_code",
        "client_id": getenv_required("ML_CLIENT_ID"),
        "client_secret": getenv_required("ML_CLIENT_SECRET"),
        "code": getenv_required("ML_AUTH_CODE"),
        "redirect_uri": getenv_required("ML_REDIRECT_URI"),
    }

    code_verifier = os.getenv("ML_CODE_VERIFIER", "").strip()
    if code_verifier:
        payload["code_verifier"] = code_verifier

    return payload


def main() -> None:
    payload = build_payload()

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
        print("access_token:", data.get("access_token"))
        print("refresh_token:", data.get("refresh_token"))
        print("expires_in:", data.get("expires_in"))
    else:
        print(data)
        sys.exit(1)


if __name__ == "__main__":
    main()
