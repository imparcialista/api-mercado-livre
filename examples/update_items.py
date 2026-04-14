"""Atualiza preco/estoque de itens do Mercado Livre com modo seguro dry-run.

Uso:
  $env:ML_ACCESS_TOKEN='...'
  python examples/update_items.py --input input/item_updates.json          # dry-run
  python examples/update_items.py --input input/item_updates.json --apply  # aplica
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Atualiza itens no Mercado Livre")
    parser.add_argument("--input", required=True, help="JSON com lista de updates")
    parser.add_argument("--apply", action="store_true", help="Aplica atualizacoes (sem isto fica em dry-run)")
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=float, default=2.0)
    return parser.parse_args()


def validate_operation(op: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(op.get("item_id"), str) or not op["item_id"].strip():
        return False, "item_id ausente ou invalido"

    has_direct = any(k in op for k in ("price", "available_quantity"))
    has_variations = isinstance(op.get("variations"), list) and len(op["variations"]) > 0

    if not has_direct and not has_variations:
        return False, "informe price/available_quantity e/ou variations"

    if "price" in op and not isinstance(op["price"], (int, float)):
        return False, "price deve ser numero"

    if "available_quantity" in op and not isinstance(op["available_quantity"], int):
        return False, "available_quantity deve ser inteiro"

    if has_variations:
        for v in op["variations"]:
            if not isinstance(v, dict):
                return False, "cada variacao deve ser objeto"
            if "id" not in v:
                return False, "variacao sem id"
            if "available_quantity" in v and not isinstance(v["available_quantity"], int):
                return False, "available_quantity da variacao deve ser inteiro"

    return True, ""


def build_payload(op: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}

    if "price" in op:
        payload["price"] = op["price"]

    if "available_quantity" in op:
        payload["available_quantity"] = op["available_quantity"]

    if isinstance(op.get("variations"), list) and op["variations"]:
        payload["variations"] = []
        for v in op["variations"]:
            row = {"id": v["id"]}
            if "available_quantity" in v:
                row["available_quantity"] = v["available_quantity"]
            payload["variations"].append(row)

    return payload


def apply_update(item_id: str, payload: Dict[str, Any], token: str, max_retries: int, retry_sleep: float) -> Dict[str, Any]:
    url = f"{BASE_URL}/items/{item_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    attempts = 0
    while True:
        attempts += 1
        response = requests.put(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 409 and attempts <= (max_retries + 1):
            time.sleep(retry_sleep)
            continue

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}

        return {
            "http_status": response.status_code,
            "ok": response.ok,
            "response": data,
            "attempts": attempts,
        }


def main() -> None:
    args = parse_args()
    token = getenv_required("ML_ACCESS_TOKEN")

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Arquivo nao encontrado: {input_path}")
        sys.exit(1)

    try:
        operations = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("JSON invalido no arquivo de entrada")
        sys.exit(1)

    if not isinstance(operations, list):
        print("O arquivo deve conter uma lista de operacoes")
        sys.exit(1)

    results: List[Dict[str, Any]] = []
    ok_count = 0
    err_count = 0
    dry_count = 0

    for op in operations:
        if not isinstance(op, dict):
            results.append({"ok": False, "error": "operacao invalida (nao e objeto)", "operation": op})
            err_count += 1
            continue

        valid, reason = validate_operation(op)
        if not valid:
            results.append({"ok": False, "error": reason, "operation": op})
            err_count += 1
            continue

        item_id = op["item_id"].strip()
        payload = build_payload(op)

        if not args.apply:
            results.append(
                {
                    "ok": True,
                    "dry_run": True,
                    "item_id": item_id,
                    "payload": payload,
                }
            )
            dry_count += 1
            continue

        applied = apply_update(item_id, payload, token, args.max_retries, args.retry_sleep)
        row = {
            "item_id": item_id,
            "payload": payload,
            **applied,
        }
        results.append(row)

        if applied["ok"]:
            ok_count += 1
        else:
            err_count += 1

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "item_updates_results.json"
    output_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Modo: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Sucesso: {ok_count}")
    print(f"Falha: {err_count}")
    print(f"Dry-run: {dry_count}")
    print(f"Resultado: {output_file.resolve()}")


if __name__ == "__main__":
    main()
