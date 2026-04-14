# 06 - Consultar pedidos (orders) e exportar resultados


Este capítulo mostra como buscar pedidos de vendedor usando `/orders/search` e exportar os resultados para análise.

## Endpoint

```text
GET https://api.mercadolibre.com/orders/search
```

Headers:
- `Authorization: Bearer {ACCESS_TOKEN}`

## Filtros úteis

Parâmetros comuns:
- `seller={SELLER_ID}`
- `order.status=paid,confirmed,...`
- `q=` (busca por id de order, item, título ou nickname)
- `order.date_created.from=`
- `order.date_created.to=`
- `order.date_last_updated.from=`
- `order.date_last_updated.to=`
- `sort=date_desc` (ou `date_asc`)
- `limit` e `offset`

Exemplo:

```text
/orders/search?seller=123456789&order.status=paid&sort=date_desc&limit=50&offset=0
```

## Exemplo Python

Use o script [get_orders.py](https://github.com/imparcialista/api-mercado-livre/blob/main/examples/get_orders.py).

Variáveis obrigatórias:
- `ML_ACCESS_TOKEN`
- `ML_SELLER_ID`

Exemplo de execução:

```bash
python examples/get_orders.py --status paid --limit 50 --max-pages 3 --sort date_desc
```

Com filtro de data:

```bash
python examples/get_orders.py --status paid --date-from 2026-01-01T00:00:00.000-03:00 --date-to 2026-01-31T23:59:59.999-03:00
```

## Saídas

- `output/orders_raw.json`: resposta consolidada.
- `output/orders_summary.csv`: resumo por order.

Campos no CSV:
- `id`
- `status`
- `status_detail`
- `date_created`
- `date_closed`
- `last_updated`
- `total_amount`
- `paid_amount`
- `currency_id`
- `buyer_id`
- `buyer_nickname`
- `seller_id`
- `tags`

## Referências

- [Order management (EN)](https://developers.mercadolivre.com.br/en_us/manage-sales/order-management)
- [Gerenciamento de vendas (PT-BR)](https://developers.mercadolivre.com.br/pt_br/imovel-consulta-de-usuarios/gerenciamento-de-vendas)

