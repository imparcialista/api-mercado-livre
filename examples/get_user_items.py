"""Consulta anúncios do usuário no Mercado Livre (offset ou scan).

Uso (PowerShell):
  $env:ML_ACCESS_TOKEN='...'
  $env:ML_USER_ID='123456'

  # Modo offset
  python examples/get_user_items.py --mode offset --status active --limit 100 --max-pages 5

  # Modo scan
  python examples/get_user_items.py --mode scan --limit 100
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests

BASE_URL = "https://api.mercadolibre.com"


def getenv_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"Variavel obrigatoria ausente: {name}")
        sys.exit(1)
    return value


def make_request(path: str, token: str, params: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.get(
        f"{BASE_URL}{path}",
        params=params,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )

    if not response.ok:
        print(f"Erro HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json()


def fetch_with_offset(user_id: str, token: str, limit: int, status: str | None, max_pages: int | None) -> List[str]:
    item_ids: List[str] = []
    page = 0

    while True:
        params: Dict[str, Any] = {"limit": limit, "offset": page * limit}
        if status:
            params["status"] = status

        data = make_request(f"/users/{user_id}/items/search", token, params)
        results = data.get("results", [])

        if not results:
            break

        item_ids.extend(results)
        page += 1

        if max_pages is not None and page >= max_pages:
            break

        paging = data.get("paging", {})
        total = int(paging.get("total", 0))
        if page * limit >= total:
            break

    return item_ids


def fetch_with_scan(user_id: str, token: str, limit: int) -> List[str]:
    item_ids: List[str] = []

    params: Dict[str, Any] = {"search_type": "scan", "limit": limit}
    data = make_request(f"/users/{user_id}/items/search", token, params)

    while True:
        results = data.get("results", [])
        if not results:
            break

        item_ids.extend(results)
        scroll_id = data.get("scroll_id")
        if not scroll_id:
            break

        data = make_request(
            f"/users/{user_id}/items/search",
            token,
            {"search_type": "scan", "scroll_id": scroll_id, "limit": limit},
        )

    return item_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consulta anúncios do usuário no Mercado Livre")
    parser.add_argument("--mode", choices=["offset", "scan"], default="offset")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--status", default=None)
    parser.add_argument("--max-pages", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = getenv_required("ML_ACCESS_TOKEN")
    user_id = getenv_required("ML_USER_ID")

    if args.limit < 1 or args.limit > 100:
        print("--limit deve estar entre 1 e 100")
        sys.exit(1)

    if args.mode == "offset":
        item_ids = fetch_with_offset(user_id, token, args.limit, args.status, args.max_pages)
    else:
        item_ids = fetch_with_scan(user_id, token, args.limit)

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "item_ids.json"
    output_file.write_text(json.dumps(item_ids, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Total coletado: {len(item_ids)}")
    print(f"Arquivo gerado: {output_file.resolve()}")


if __name__ == "__main__":
    main()
