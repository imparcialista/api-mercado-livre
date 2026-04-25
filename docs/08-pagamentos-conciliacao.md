---
title: Capítulo 08 · Pagamentos e conciliação
description: Como relacionar pedidos, pagamentos, cobranças e notificações de pagamento na API Mercado Livre.
tags:
  - payments
  - reconciliation
  - orders
  - billing
---

# Capítulo 08 · Pagamentos e conciliação

## Para quem é este capítulo

Para integradores que precisam auditar valores de pedidos, acompanhar pagamentos e preparar dados para financeiro, BI ou conciliação.

## Pré-requisitos

- `ML_ACCESS_TOKEN`
- `ORDER_ID`
- `PAYMENT_ID`, quando a rotina vier de uma notificação ou relatório financeiro

Pagamentos podem aparecer em mais de um contexto: dentro do pedido, em notificações do tópico `payments`, em recursos de cobrança/faturamento e em detalhes do Mercado Pago. Defina qual pergunta sua rotina precisa responder antes de escolher o endpoint.

## Perguntas que a integração deve separar

| Pergunta | Fonte inicial recomendada |
| --- | --- |
| O pedido foi pago? | `/orders/{order_id}` ou `/orders/search` |
| O pagamento mudou de status? | Notificação `payments` e consulta do recurso indicado |
| Quais taxas/cobranças foram associadas? | Relatórios de faturamento e cobranças |
| Existe custo de envio associado? | `/shipments/{shipment_id}/payments` |
| Preciso do detalhe transacional do Mercado Pago? | API do Mercado Pago, quando aplicável ao escopo da aplicação |

## Endpoints úteis

```text
GET https://api.mercadolibre.com/orders/{ORDER_ID}
GET https://api.mercadolibre.com/collections/{PAYMENT_ID}
GET https://api.mercadolibre.com/shipments/{SHIPMENT_ID}/payments
GET https://api.mercadolibre.com/billing/integration/payment/{PAYMENT_ID}/charges
```

Headers:

- `Authorization: Bearer {ACCESS_TOKEN}`

## Consultar pedido e pagamentos associados

```bash
curl -H "Authorization: Bearer $ML_ACCESS_TOKEN" \
  "https://api.mercadolibre.com/orders/$ORDER_ID"
```

Ao processar a resposta, salve os campos financeiros importantes em estrutura própria:

- `order_id`
- `status`
- `date_closed`
- `total_amount`
- `paid_amount`
- `currency_id`
- identificadores de pagamento retornados no pedido
- tags relevantes do pedido e do pagamento

Não use apenas `status=paid` como sinônimo de venda concluída. Cancelamentos, devoluções, tags e fluxo logístico podem exigir tratamento separado.

## Consultar pagamento recebido por notificação

Quando a aplicação estiver inscrita no tópico `payments`, a notificação informa um recurso parecido com `/collections/{payment_id}`. Use o ID recebido para buscar o detalhe.

```bash
curl -H "Authorization: Bearer $ML_ACCESS_TOKEN" \
  "https://api.mercadolibre.com/collections/$PAYMENT_ID"
```

Regras práticas:

- responda `200` rapidamente no webhook;
- coloque a notificação em fila;
- consulte o recurso oficial depois;
- deduplique por `topic`, `resource`, `application_id` e `sent`;
- não confie em ordem cronológica perfeita entre notificações.

## Conciliação financeira

Para rotinas financeiras, crie uma tabela intermediária em vez de misturar tudo na tabela de pedidos:

| Campo local | Observação |
| --- | --- |
| `order_id` | Chave de negócio para cruzar com vendas. |
| `payment_id` | Armazene como texto; relatórios podem ter IDs alfanuméricos. |
| `source` | `order`, `notification`, `billing`, `shipment_payment`. |
| `status` | Status bruto da origem. |
| `amount` | Valor informado pela origem. |
| `currency_id` | Não assuma sempre BRL se sua aplicação crescer para outros sites. |
| `raw_payload` | JSON original para auditoria e suporte. |

## Checklist antes de automatizar baixa financeira

- O pedido pertence ao vendedor autenticado?
- A moeda é a esperada?
- `paid_amount` bate com o valor que seu ERP considera recebido?
- Há cancelamento, chargeback, devolução ou tag que mude a interpretação?
- A cobrança de envio precisa ser tratada separadamente?
- O `payment_id` foi salvo como string?
- A rotina é idempotente se a mesma notificação chegar duas vezes?

## Falhas comuns

- `401`: token inválido ou expirado.
- `403`: pagamento ou pedido fora do escopo do token.
- `404`: pagamento não disponível no recurso consultado.
- Divergência de valor: compare pedido, pagamento, envio e cobrança antes de sobrescrever a conciliação.
- Campo numérico estourando: trate IDs como texto quando a documentação indicar identificadores alfanuméricos ou maiores que Int32.

## Referências oficiais

- [Gerenciamento de pagamentos](https://developers.mercadolivre.com.br/pt_br/produto-consulta-de-usuarios/gerenciamento-de-pagamentos)
- [Notificações de pagamentos](https://developers.mercadolivre.com.br/pt_br/mensagens-post-venda/produto-receba-notificacoes)
- [Relatórios de faturamento: pagamentos](https://developers.mercadolivre.com.br/pt_br/relatorios-de-faturamento/pagamentos)

