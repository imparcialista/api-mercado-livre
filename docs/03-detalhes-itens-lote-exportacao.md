---
title: Capítulo 03 · Detalhes de itens em lote e exportação
description: Busca detalhes com /items?ids e exporta CSV/XLSX com tratamento de sucesso/erro por item.
tags:
  - items
  - batch
  - export
---

# Capítulo 03 · Detalhes de itens em lote e exportação

## Para quem é este capítulo

Para quem já tem IDs de anúncios e precisa montar base analítica para integração, pricing ou auditoria.

Com os IDs coletados no capítulo 02, agora vamos buscar os detalhes dos anúncios e exportar para arquivo.

## Pré-requisitos

- `ML_ACCESS_TOKEN`
- `output/item_ids.json` gerado no capítulo 02

## Endpoint

```text
GET https://api.mercadolibre.com/items?ids=MLB1,MLB2,MLB3
```

Headers:
- `Authorization: Bearer {ACCESS_TOKEN}`

## Como funciona

- A API aceita múltiplos IDs na query `ids` (separados por vírgula).
- A resposta é uma lista, um objeto por item solicitado.
- Cada objeto costuma trazer:
  - `code` (HTTP por item, ex.: 200, 404)
  - `body` (detalhes do item, quando existe)

## Estratégia recomendada

1. Ler os IDs do arquivo `output/item_ids.json`.
2. Dividir em lotes (ex.: 20 por chamada).
3. Chamar `/items?ids=...` em loop.
4. Guardar sucesso/erro por item.
5. Exportar CSV para análise.
6. Opcional: gerar XLSX.

## Exemplo executável (Python)

Use o script [get_items_details.py](https://github.com/imparcialista/api-mercado-livre/blob/main/examples/get_items_details.py).

Exemplo de execução:

```bash
python examples/get_items_details.py --input output/item_ids.json --batch-size 20 --xlsx
```

Saídas geradas:
- `output/items_details.csv`
- `output/items_errors.csv`
- `output/items_details.xlsx` (se `--xlsx` e `pandas` + `openpyxl` instalados)

## Saída esperada

- `id`
- `title`
- `status`
- `price`
- `currency_id`
- `available_quantity`
- `sold_quantity`
- `condition`
- `permalink`
- `date_created`
- `last_updated`

## Falhas comuns

- `400`: lote inválido no parâmetro `ids`.
- `401`: token inválido.
- `404` por item: item inexistente ou sem acesso.

## Referências oficiais

- [Items & Searches (EN)](https://developers.mercadolivre.com.br/en_us/api-docs/items-and-searches)
- [Itens e Buscas (PT-BR)](https://developers.mercadolivre.com.br/pt_br/itens-e-buscas)


