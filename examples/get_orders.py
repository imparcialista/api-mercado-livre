"""Consulta pedidos no Mercado Livre e exporta JSON/CSV.

Uso:
  $env:ML_ACCESS_TOKEN='...'
  $env:ML_SELLER_ID='123456789'
  python examples/get_orders.py --status paid --limit 50 --max-pages 3
"""

from __future__ import annotations

import argparse
import csv
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


def make_request(token: str, params: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.get(
        f"{BASE_URL}/orders/search",
        params=params,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )

    if not response.ok:
        print(f"Erro HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consulta pedidos no Mercado Livre")
    parser.add_argument("--status", default=None, help="Ex: paid, confirmed")
    parser.add_argument("--q", default=None, help="Busca livre")
    parser.add_argument("--date-from", default=None, help="order.date_created.from")
    parser.add_argument("--date-to", default=None, help="order.date_created.to")
    parser.add_argument("--sort", choices=["date_desc", "date_asc"], default="date_desc")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-pages", type=int, default=5)
    return parser.parse_args()


def flatten_order(order: Dict[str, Any]) -> Dict[str, Any]:
    buyer = order.get("buyer") or {}
    seller = order.get("seller") or {}

    return {
        "id": order.get("id"),
        "status": order.get("status"),
        "status_detail": order.get("status_detail"),
        "date_created": order.get("date_created"),
        "date_closed": order.get("date_closed"),
        "last_updated": order.get("last_updated"),
        "total_amount": order.get("total_amount"),
        "paid_amount": order.get("paid_amount"),
        "currency_id": order.get("currency_id"),
        "buyer_id": buyer.get("id"),
        "buyer_nickname": buyer.get("nickname"),
        "seller_id": seller.get("id"),
        "tags": ",".join(order.get("tags", [])) if isinstance(order.get("tags"), list) else "",
    }


def main() -> None:
    args = parse_args()
    token = getenv_required("ML_ACCESS_TOKEN")
    seller_id = getenv_required("ML_SELLER_ID")

    if args.limit < 1 or args.limit > 50:
        print("--limit deve estar entre 1 e 50")
        sys.exit(1)

    if args.max_pages < 1:
        print("--max-pages deve ser >= 1")
        sys.exit(1)

    all_orders: List[Dict[str, Any]] = []

    for page in range(args.max_pages):
        params: Dict[str, Any] = {
            "seller": seller_id,
            "sort": args.sort,
            "limit": args.limit,
            "offset": page * args.limit,
        }

        if args.status:
            params["order.status"] = args.status
        if args.q:
            params["q"] = args.q
        if args.date_from:
            params["order.date_created.from"] = args.date_from
        if args.date_to:
            params["order.date_created.to"] = args.date_to

        payload = make_request(token, params)
        results = payload.get("results", [])

        if not results:
            break

        all_orders.extend(results)

        paging = payload.get("paging", {})
        total = int(paging.get("total", 0))
        if (page + 1) * args.limit >= total:
            break

    summary = [flatten_order(order) for order in all_orders]

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_file = output_dir / "orders_raw.json"
    csv_file = output_dir / "orders_summary.csv"

    raw_file.write_text(json.dumps(all_orders, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "id",
        "status",
        "status_detail",
        "date_created",
        "date_closed",
        "last_updated",
        "total_amount",
        "paid_amount",
        "currency_id",
        "buyer_id",
        "buyer_nickname",
        "seller_id",
        "tags",
    ]

    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)

    print(f"Pedidos coletados: {len(all_orders)}")
    print(f"Arquivo JSON: {raw_file.resolve()}")
    print(f"Arquivo CSV: {csv_file.resolve()}")


if __name__ == "__main__":
    main()
