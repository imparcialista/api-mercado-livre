# API Mercado Livre - Documentacao e exemplos em Python

Este repositório agora é focado em documentação prática da API do Mercado Livre, com exemplos em Python.

## Estrutura

- `docs/01-criar-aplicativo-e-token.md`: criar aplicativo e gerar tokens OAuth.
- `docs/02-primeira-consulta-anuncios.md`: primeira consulta de anúncios e paginação.
- `examples/oauth_exchange_token.py`: troca `authorization_code` por `access_token` + `refresh_token`.
- `examples/oauth_refresh_token.py`: renova `access_token` via `refresh_token`.
- `examples/get_user_items.py`: consulta anúncios (`offset` ou `scan`) e salva IDs.

## Começando

1. Leia os guias em `docs/` na ordem.
2. Instale dependências para os exemplos:

```bash
python -m pip install requests
```

3. Execute os exemplos em `examples/` após preencher as variáveis de ambiente.

## Fontes oficiais

- [Register your application](https://developers.mercadolivre.com.br/en_us/products-authentication-authorization/register-your-application)
- [Items & Searches (EN)](https://developers.mercadolivre.com.br/en_us/api-docs/items-and-searches)
- [Itens e Buscas (PT-BR)](https://developers.mercadolivre.com.br/pt_br/itens-e-buscas)
- [Obtenção do Access Token](https://developers.mercadolivre.com.br/pt_br/obtencao-do-access-token)
