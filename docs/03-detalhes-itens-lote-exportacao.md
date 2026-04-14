# 03 - Buscar detalhes dos itens em lote e exportar CSV/XLSX

Com os IDs coletados no capítulo 02, agora vamos buscar os detalhes dos anúncios e exportar para arquivo.

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

## Exemplo Python

Use o script [get_items_details.py](/C:/Users/Lucas/Documents/GitHub/api-mercado-livre/examples/get_items_details.py).

Variáveis de ambiente obrigatórias:
- `ML_ACCESS_TOKEN`

Exemplo de execução:

```bash
python examples/get_items_details.py --input output/item_ids.json --batch-size 20 --xlsx
```

Saídas geradas:
- `output/items_details.csv`
- `output/items_errors.csv`
- `output/items_details.xlsx` (se `--xlsx` e `pandas` + `openpyxl` instalados)

## Campos exportados (CSV)

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

## Referências

- [Items & Searches (EN)](https://developers.mercadolivre.com.br/en_us/api-docs/items-and-searches)
- [Itens e Buscas (PT-BR)](https://developers.mercadolivre.com.br/pt_br/itens-e-buscas)
