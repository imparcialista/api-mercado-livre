"""Busca detalhes de itens em lote e exporta CSV/XLSX.

Uso (PowerShell):
  $env:ML_ACCESS_TOKEN='...'
  python examples/get_items_details.py --input output/item_ids.json --batch-size 20 --xlsx
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

BASE_URL = "https://api.mercadolibre.com"


def getenv_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"Variavel obrigatoria ausente: {name}")
        sys.exit(1)
    return value


def chunks(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def fetch_batch(ids_batch: List[str], token: str) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{BASE_URL}/items",
        params={"ids": ",".join(ids_batch)},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )

    if not response.ok:
        print(f"Erro HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    return response.json()


def parse_results(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    ok_items: List[Dict[str, Any]] = []
    err_items: List[Dict[str, Any]] = []

    for row in rows:
        code = row.get("code")
        item_id = row.get("id")

        if code == 200 and isinstance(row.get("body"), dict):
            body = row["body"]
            ok_items.append(
                {
                    "id": body.get("id", item_id),
                    "title": body.get("title"),
                    "status": body.get("status"),
                    "price": body.get("price"),
                    "currency_id": body.get("currency_id"),
                    "available_quantity": body.get("available_quantity"),
                    "sold_quantity": body.get("sold_quantity"),
                    "condition": body.get("condition"),
                    "permalink": body.get("permalink"),
                    "date_created": body.get("date_created"),
                    "last_updated": body.get("last_updated"),
                }
            )
        else:
            err_items.append(
                {
                    "id": item_id,
                    "code": code,
                    "error": row.get("body", {}).get("error") if isinstance(row.get("body"), dict) else None,
                    "message": row.get("body", {}).get("message") if isinstance(row.get("body"), dict) else None,
                }
            )

    return ok_items, err_items


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx_if_requested(path: Path, rows: List[Dict[str, Any]], enabled: bool) -> None:
    if not enabled:
        return

    try:
        import pandas as pd  # type: ignore
    except ImportError:
        print("--xlsx foi solicitado, mas pandas nao esta instalado. Pulando XLSX.")
        return

    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Busca detalhes de itens em lote")
    parser.add_argument("--input", default="output/item_ids.json", help="Arquivo JSON com lista de IDs")
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--xlsx", action="store_true", help="Gera XLSX alem do CSV")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = getenv_required("ML_ACCESS_TOKEN")

    if args.batch_size < 1 or args.batch_size > 20:
        print("--batch-size deve estar entre 1 e 20")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Arquivo de entrada nao encontrado: {input_path}")
        sys.exit(1)

    try:
        item_ids = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"JSON invalido: {input_path}")
        sys.exit(1)

    if not isinstance(item_ids, list) or not all(isinstance(i, str) for i in item_ids):
        print("O arquivo de entrada deve conter uma lista JSON de strings (IDs MLB).")
        sys.exit(1)

    all_ok: List[Dict[str, Any]] = []
    all_err: List[Dict[str, Any]] = []

    for ids_batch in chunks(item_ids, args.batch_size):
        rows = fetch_batch(ids_batch, token)
        ok, err = parse_results(rows)
        all_ok.extend(ok)
        all_err.extend(err)

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    details_csv = output_dir / "items_details.csv"
    errors_csv = output_dir / "items_errors.csv"
    details_xlsx = output_dir / "items_details.xlsx"

    write_csv(
        details_csv,
        all_ok,
        [
            "id",
            "title",
            "status",
            "price",
            "currency_id",
            "available_quantity",
            "sold_quantity",
            "condition",
            "permalink",
            "date_created",
            "last_updated",
        ],
    )

    write_csv(errors_csv, all_err, ["id", "code", "error", "message"])
    write_xlsx_if_requested(details_xlsx, all_ok, args.xlsx)

    print(f"Itens com sucesso: {len(all_ok)}")
    print(f"Itens com erro: {len(all_err)}")
    print(f"CSV detalhes: {details_csv.resolve()}")
    print(f"CSV erros: {errors_csv.resolve()}")
    if args.xlsx:
        print(f"XLSX detalhes (se gerado): {details_xlsx.resolve()}")


if __name__ == "__main__":
    main()
