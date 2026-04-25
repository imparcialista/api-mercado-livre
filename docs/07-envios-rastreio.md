---
title: Capítulo 07 · Envios, logística e rastreio
description: Como consultar dados de envio, status logístico e rastreio a partir de pedidos do Mercado Livre.
tags:
  - shipments
  - logistics
  - tracking
  - orders
---

# Capítulo 07 · Envios, logística e rastreio

## Para quem é este capítulo

Para integradores que já importam pedidos e precisam acompanhar expedição, status logístico, prazos e dados de rastreio.

## Pré-requisitos

- `ML_ACCESS_TOKEN`
- `ORDER_ID` ou `SHIPMENT_ID`
- Pedido pertencente ao vendedor autenticado

O pedido nem sempre carrega todos os dados logísticos. Em integrações atuais, trate o envio como um recurso próprio e consulte `/shipments/{shipment_id}` quando precisar de detalhes.

## Fluxo recomendado

1. Busque o pedido em `/orders/{order_id}` ou liste pedidos em `/orders/search`.
2. Identifique o envio associado ao pedido.
3. Consulte `/orders/{order_id}/shipments` quando precisar descobrir os envios vinculados.
4. Consulte `/shipments/{shipment_id}` para obter o detalhe logístico.
5. Normalize status e status detail para a linguagem do seu sistema.
6. Grave snapshots, porque status de envio muda ao longo do tempo.

## Endpoints

```text
GET https://api.mercadolibre.com/orders/{ORDER_ID}/shipments
GET https://api.mercadolibre.com/shipments/{SHIPMENT_ID}
GET https://api.mercadolibre.com/shipments/{SHIPMENT_ID}/lead_time
GET https://api.mercadolibre.com/shipments/{SHIPMENT_ID}/payments
```

Headers:

- `Authorization: Bearer {ACCESS_TOKEN}`
- `x-format-new: true` quando a documentação oficial do recurso solicitar o JSON atualizado

## Exemplo de consulta

Consultar envios do pedido:

```bash
curl -H "Authorization: Bearer $ML_ACCESS_TOKEN" \
  "https://api.mercadolibre.com/orders/$ORDER_ID/shipments"
```

Consultar detalhe do envio:

```bash
curl -H "Authorization: Bearer $ML_ACCESS_TOKEN" \
  -H "x-format-new: true" \
  "https://api.mercadolibre.com/shipments/$SHIPMENT_ID"
```

Consultar prazo operacional:

```bash
curl -H "Authorization: Bearer $ML_ACCESS_TOKEN" \
  "https://api.mercadolibre.com/shipments/$SHIPMENT_ID/lead_time"
```

## Campos que vale persistir

Para uma primeira versão de integração, salve pelo menos:

- `id`
- `order_id` local associado
- `status`
- `status_detail`
- `substatus`, quando existir
- `logistic_type`
- `mode`
- `tracking_number`
- `tracking_method`
- `date_created`
- `last_updated`
- prazos retornados por `lead_time`, quando usados no painel

Evite depender apenas do texto exibido no painel do Mercado Livre. O sistema deve tomar decisões por códigos e só traduzir para o usuário na camada de apresentação.

## Estados operacionais comuns

| Situação | Como tratar no sistema |
| --- | --- |
| Envio criado, mas sem postagem | Mostrar como aguardando expedição ou etiqueta pendente. |
| Envio em trânsito | Atualizar rastreio e previsão de entrega. |
| Envio entregue | Fechar rotina logística e evitar novas cobranças operacionais. |
| Envio cancelado | Verificar se pedido, pagamento e estoque também precisam ser reconciliados. |
| Envio com divergência | Criar alerta manual em vez de sobrescrever dados silenciosamente. |

## Boas práticas

- Não consulte todos os envios em loop infinito. Combine importação por período com notificações do capítulo 09.
- Guarde o `shipment_id` mesmo quando o painel exibir apenas o pedido.
- Separe status de pedido, pagamento e envio; eles mudam em momentos diferentes.
- Faça idempotência por `shipment_id` e `last_updated`.
- Em tela administrativa, mostre o status bruto em área técnica ou expansível para facilitar suporte.

## Falhas comuns

- `401`: token inválido ou expirado.
- `403`: envio não pertence ao vendedor autenticado.
- `404`: `shipment_id` inexistente ou indisponível para a conta.
- Dados de envio ausentes no pedido: consulte o recurso de shipments em vez de depender somente do JSON de orders.

## Referências oficiais

- [Shipments](https://developers.mercadolivre.com.br/en_us/products-analitics-benchmarking/shipment-handling)
- [Custom shipping](https://developers.mercadolivre.com.br/en_us/getting-started/custom-shipping)

