---
title: Referência · Cookbook
description: Receitas operacionais para fluxos comuns de integração com a API Mercado Livre.
tags:
  - cookbook
  - operations
  - recipes
---

# Referência · Cookbook

## Para quem é esta página

Para programadores que precisam executar tarefas recorrentes rapidamente sem reabrir todos os capítulos.

## Pré-requisitos

- Variáveis de ambiente configuradas conforme cada script.
- Python 3.11+ e dependências do projeto instaladas.

## Receita 1 · Obter token e validar conta

1. Execute o fluxo OAuth do capítulo 01.
2. Valide o token:

```bash
curl -H "Authorization: Bearer SEU_ACCESS_TOKEN" https://api.mercadolibre.com/users/me
```

Saída esperada: dados da conta autenticada em JSON.

## Receita 2 · Exportar IDs de anúncios ativos

```bash
python examples/get_user_items.py --mode offset --status active --limit 100 --max-pages 10
```

Saída esperada: `output/item_ids.json`.

## Receita 3 · Exportar detalhes de anúncios para CSV

```bash
python examples/get_items_details.py --input output/item_ids.json --batch-size 20
```

Saída esperada:
- `output/items_details.csv`
- `output/items_errors.csv`

## Receita 4 · Atualizar preço/estoque com segurança

Dry-run (recomendado antes de produção):

```bash
python examples/update_items.py --input input/item_updates.example.json
```

Aplicar em produção:

```bash
python examples/update_items.py --input input/item_updates.example.json --apply
```

Saída esperada: `output/item_updates_results.json`.

## Receita 5 · Exportar pedidos pagos

```bash
python examples/get_orders.py --status paid --limit 50 --max-pages 5 --sort date_desc
```

Saída esperada:
- `output/orders_raw.json`
- `output/orders_summary.csv`
