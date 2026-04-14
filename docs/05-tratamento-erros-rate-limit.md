---
title: Capítulo 05 · Resiliência: erros, timeout e rate limit
description: Estratégias de resiliência para 429/5xx, timeout e retry com backoff/jitter.
tags:
  - resilience
  - rate-limit
  - errors
---

# Capítulo 05 · Resiliência: erros, timeout e rate limit

## Para quem é este capítulo

Para times de integração que precisam aumentar estabilidade e reduzir falhas intermitentes em produção.

## Pré-requisitos

- Conhecimento básico de HTTP status codes.
- Cliente HTTP com suporte a timeout e retries.

Para integração estável, trate erros transitórios (`429`, `5xx`, timeout) com retry e backoff.

## Erros comuns na prática

- `401`: token inválido/expirado.
- `403`: permissão insuficiente ou recurso não autorizado.
- `404`: recurso inexistente.
- `409`: conflito de atualização concorrente.
- `429`: excesso de chamadas; aguarde e tente novamente.
- `5xx`: falhas temporárias da API.

## Estratégia recomendada

1. Aplicar timeout em todas as requisições.
2. Retry apenas para erros transitórios (`429`, `5xx`, timeout/conexão).
3. Se vier `Retry-After`, respeitar esse valor.
4. Usar backoff exponencial com jitter.
5. Logar tentativa, status e motivo da falha.

## Exemplo executável (cliente reutilizável)

Use [meli_http_client.py](https://github.com/imparcialista/api-mercado-livre/blob/main/examples/meli_http_client.py).

Exemplo rápido:

```bash
python examples/meli_http_client.py
```

Variável opcional:
- `ML_ACCESS_TOKEN` (se definido, o exemplo chama `/users/me`; sem token, chama endpoint público `/sites`).

## Referências oficiais

- [Authentication and Authorization (EN)](https://developers.mercadolivre.com.br/en_us/authentication-and-authorization)


