---
title: 02 - Primeira consulta de anúncios
description: Consulta de anúncios com /users/{id}/items/search usando offset ou scan/scroll_id.
tags:
  - items
  - search
  - pagination
---

# 02 - Primeira consulta de anúncios (items/search)


Neste capítulo você vai consultar os anúncios de uma conta e entender os dois modos de paginação da API.

## Endpoint base

```text
GET https://api.mercadolibre.com/users/{USER_ID}/items/search
```

Headers:
- `Authorization: Bearer {ACCESS_TOKEN}`

## Modo 1: paginação por `offset` (até 1000 registros)

Use quando o volume de anúncios não exige paginação profunda.

Parâmetros comuns:
- `limit` (máximo 100)
- `offset` (0, 50, 100...)
- `status` (ex.: `active`, `paused`, `closed`)
- `include_filters=true` (se precisar de blocos de filtros na resposta)

Exemplo:

```text
GET /users/{USER_ID}/items/search?limit=100&offset=0&status=active
```

## Modo 2: paginação por `search_type=scan` (mais de 1000)

Para coletar grandes volumes, a documentação recomenda `scan` com `scroll_id`.

Fluxo:
1. Primeira chamada com `search_type=scan` (sem `offset`).
2. Guarde o `scroll_id` retornado (expira em ~5 minutos).
3. Faça próximas chamadas com `search_type=scan&scroll_id=...`.
4. Pare quando `results` vier vazio/null.

Exemplo inicial:

```text
GET /users/{USER_ID}/items/search?search_type=scan&limit=100
```

Exemplo próxima página:

```text
GET /users/{USER_ID}/items/search?search_type=scan&scroll_id=SEU_SCROLL_ID&limit=100
```

## Exemplo Python

Use o script [get_user_items.py](https://github.com/imparcialista/api-mercado-livre/blob/main/examples/get_user_items.py).

Variáveis de ambiente necessárias:
- `ML_ACCESS_TOKEN`
- `ML_USER_ID`

Modo `offset`:

```bash
python examples/get_user_items.py --mode offset --status active --limit 100 --max-pages 3
```

Modo `scan`:

```bash
python examples/get_user_items.py --mode scan --limit 100
```

Saída:
- imprime quantidade coletada
- salva IDs em `output/item_ids.json`

## Referências

- [Items & Searches (EN)](https://developers.mercadolivre.com.br/en_us/api-docs/items-and-searches)
- [Itens e Buscas (PT-BR)](https://developers.mercadolivre.com.br/pt_br/itens-e-buscas)


