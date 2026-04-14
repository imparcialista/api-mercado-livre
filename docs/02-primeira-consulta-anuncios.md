---
title: Capítulo 02 · Consultar anúncios (items/search)
description: Consulta de anúncios com /users/{id}/items/search usando offset/limit ou scan/scroll_id.
tags:
  - items
  - search
  - pagination
---

# Capítulo 02 · Consultar anúncios (items/search)

## Para quem é este capítulo

Para integradores que já possuem `access_token` e precisam listar anúncios com paginação confiável.

## Pré-requisitos

- `ML_ACCESS_TOKEN`
- `ML_USER_ID`

Neste capítulo você vai consultar anúncios de uma conta e entender os dois modos de paginação da API.

## Endpoint

```text
GET https://api.mercadolibre.com/users/{USER_ID}/items/search
```

Headers:
- `Authorization: Bearer {ACCESS_TOKEN}`

## Estratégia A · paginação por `offset` (até 1000 registros)

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

## Estratégia B · paginação por `search_type=scan` (volumes altos)

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

## Exemplo executável (Python)

Use o script [get_user_items.py](https://github.com/imparcialista/api-mercado-livre/blob/main/examples/get_user_items.py).

Variáveis obrigatórias:
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

## Falhas comuns

- `401`: token expirado ou inválido.
- `403`: token sem permissão para o usuário consultado.
- `429`: excesso de chamadas; aplique retry com backoff.

## Referências oficiais

- [Items & Searches (EN)](https://developers.mercadolivre.com.br/en_us/api-docs/items-and-searches)
- [Itens e Buscas (PT-BR)](https://developers.mercadolivre.com.br/pt_br/itens-e-buscas)


