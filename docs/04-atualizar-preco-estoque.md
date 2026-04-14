---
title: 04 - Atualizar preço e estoque
description: Atualização segura de anúncios com dry-run, suporte a variações e retry para conflitos.
tags:
  - items
  - updates
  - pricing
  - inventory
---

# 04 - Atualizar preço e estoque com segurança (dry-run)


Este capítulo mostra como atualizar anúncios com `PUT /items/{item_id}` usando um fluxo seguro.

## Endpoint

```text
PUT https://api.mercadolibre.com/items/{ITEM_ID}
```

Headers:
- `Authorization: Bearer {ACCESS_TOKEN}`
- `Content-Type: application/json`

## Regras importantes (2026)

- Atualizar **somente** `price` pode ser rejeitado para itens com automação de preços ativa.
- Para evitar erro operacional, valide primeiro se o item usa automação de preços.
- Em itens com variações, normalmente o estoque é atualizado por `variations`.
- Em concorrência de atualização, pode ocorrer `409 conflict` (`optimistic locking`), então tente novamente após alguns segundos.

## Formato do arquivo de entrada

Use um JSON com lista de operações, por exemplo `input/item_updates.json`:

```json
[
  {
    "item_id": "MLB1234567890",
    "price": 129.9,
    "available_quantity": 10
  },
  {
    "item_id": "MLB1234567891",
    "variations": [
      {"id": 177123456789, "available_quantity": 3},
      {"id": 177123456790, "available_quantity": 8}
    ]
  }
]
```

## Exemplo Python

Use o script [update_items.py](https://github.com/imparcialista/api-mercado-livre/blob/main/examples/update_items.py).

Variáveis de ambiente obrigatórias:
- `ML_ACCESS_TOKEN`

Dry-run (padrão, não altera nada):

```bash
python examples/update_items.py --input input/item_updates.json
```

Execução real:

```bash
python examples/update_items.py --input input/item_updates.json --apply
```

## Saídas

- `output/item_updates_results.json`: resultado completo por item.
- Resumo no terminal: sucesso, falha, dry-run.

## Referências

- [Sincronização de publicações (PT-BR)](https://developers.mercadolivre.com.br/pt_br/produto-sincronizacao-de-publicacoes)
- [Automatizações de preços (PT-BR)](https://developers.mercadolivre.com.br/pt_br/pessoas-interessadas/automatizacoes-de-precos)
- [Sync and modify listings (EN)](https://developers.mercadolivre.com.br/en_us/ship-products/products-sync-listings)


