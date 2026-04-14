# Cookbook

Receitas rápidas para tarefas frequentes.

## 1) Obter token e validar conta

1. Execute o fluxo OAuth do capítulo 01.
2. Teste o token:

```bash
curl -H "Authorization: Bearer SEU_ACCESS_TOKEN" https://api.mercadolibre.com/users/me
```

## 2) Exportar IDs de anúncios ativos

```bash
python examples/get_user_items.py --mode offset --status active --limit 100 --max-pages 10
```

Saída: `output/item_ids.json`.

## 3) Exportar detalhes para CSV

```bash
python examples/get_items_details.py --input output/item_ids.json --batch-size 20
```

Saídas: `output/items_details.csv` e `output/items_errors.csv`.

## 4) Atualizar preço/estoque com segurança

Dry-run:

```bash
python examples/update_items.py --input input/item_updates.example.json
```

Aplicar:

```bash
python examples/update_items.py --input input/item_updates.example.json --apply
```

## 5) Exportar pedidos pagos

```bash
python examples/get_orders.py --status paid --limit 50 --max-pages 5 --sort date_desc
```

Saídas: `output/orders_raw.json` e `output/orders_summary.csv`.
