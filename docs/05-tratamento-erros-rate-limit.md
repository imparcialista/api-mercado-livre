# 05 - Tratamento de erros e limites de taxa (429)

[Docs Home](./index.md) | [Anterior: 04](./04-atualizar-preco-estoque.md)

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

## Exemplo Python (cliente reutilizável)

Use [meli_http_client.py](/C:/Users/Lucas/Documents/GitHub/api-mercado-livre/examples/meli_http_client.py).

Exemplo rápido:

```bash
python examples/meli_http_client.py
```

Variável opcional:
- `ML_ACCESS_TOKEN` (se definido, o exemplo chama `/users/me`; sem token, chama endpoint público `/sites`).

## Referência oficial usada

- [Authentication and Authorization (EN)](https://developers.mercadolivre.com.br/en_us/authentication-and-authorization)

[Docs Home](./index.md) | [Anterior: 04](./04-atualizar-preco-estoque.md)
