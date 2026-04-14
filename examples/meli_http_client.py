"""Cliente HTTP reutilizavel para API Mercado Livre com retry/backoff.

Demonstra tratamento para: timeout, erros de conexao, 429 e 5xx.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class RetryConfig:
    max_attempts: int = 5
    base_sleep_seconds: float = 0.5
    timeout_seconds: float = 30.0


class MeliHttpClient:
    def __init__(self, access_token: Optional[str] = None, retry: Optional[RetryConfig] = None) -> None:
        self.base_url = "https://api.mercadolibre.com"
        self.access_token = access_token
        self.retry = retry or RetryConfig()

    def _headers(self) -> Dict[str, str]:
        headers = {"accept": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}{path}"
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.retry.max_attempts + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self._headers(),
                    timeout=self.retry.timeout_seconds,
                    **kwargs,
                )

                if response.status_code == 429:
                    if attempt == self.retry.max_attempts:
                        return response

                    retry_after = response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        sleep_seconds = float(retry_after)
                    else:
                        sleep_seconds = self._backoff_with_jitter(attempt)

                    print(f"[retry] 429 recebido. Aguardando {sleep_seconds:.2f}s (tentativa {attempt}).")
                    time.sleep(sleep_seconds)
                    continue

                if 500 <= response.status_code <= 599:
                    if attempt == self.retry.max_attempts:
                        return response

                    sleep_seconds = self._backoff_with_jitter(attempt)
                    print(f"[retry] {response.status_code} recebido. Aguardando {sleep_seconds:.2f}s (tentativa {attempt}).")
                    time.sleep(sleep_seconds)
                    continue

                return response

            except (requests.Timeout, requests.ConnectionError) as exc:
                last_exception = exc
                if attempt == self.retry.max_attempts:
                    break

                sleep_seconds = self._backoff_with_jitter(attempt)
                print(f"[retry] erro de rede ({type(exc).__name__}). Aguardando {sleep_seconds:.2f}s (tentativa {attempt}).")
                time.sleep(sleep_seconds)

        if last_exception:
            raise last_exception
        raise RuntimeError("Falha inesperada sem resposta e sem excecao registrada")

    def _backoff_with_jitter(self, attempt: int) -> float:
        exponential = self.retry.base_sleep_seconds * (2 ** (attempt - 1))
        jitter = random.uniform(0.0, 0.3)
        return exponential + jitter


def main() -> None:
    import os

    token = os.getenv("ML_ACCESS_TOKEN")
    client = MeliHttpClient(access_token=token)

    if token:
        resp = client.request("GET", "/users/me")
    else:
        resp = client.request("GET", "/sites")

    print(f"HTTP {resp.status_code}")
    try:
        print(resp.json())
    except ValueError:
        print(resp.text)


if __name__ == "__main__":
    main()
