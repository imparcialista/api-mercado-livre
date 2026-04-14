# API Mercado Livre - Documentacao e exemplos em Python

Este repositório agora é focado em documentação prática da API do Mercado Livre, com exemplos em Python.

## Navegação da documentação

- [Trilha de docs](./docs/index.md)
- [GitHub Pages](https://imparcialista.github.io/api-mercado-livre/)

## Estrutura

- `docs/01-criar-aplicativo-e-token.md`: criar aplicativo e gerar tokens OAuth.
- `docs/02-primeira-consulta-anuncios.md`: primeira consulta de anúncios e paginação.
- `docs/03-detalhes-itens-lote-exportacao.md`: detalhes de itens em lote e exportação CSV/XLSX.
- `docs/04-atualizar-preco-estoque.md`: atualização de preço/estoque com dry-run.
- `docs/05-tratamento-erros-rate-limit.md`: tratamento de 429/5xx e retries.
- `examples/oauth_exchange_token.py`: troca `authorization_code` por `access_token` + `refresh_token`.
- `examples/oauth_refresh_token.py`: renova `access_token` via `refresh_token`.
- `examples/get_user_items.py`: consulta anúncios (`offset` ou `scan`) e salva IDs.
- `examples/get_items_details.py`: busca detalhes em lote e exporta arquivos.
- `examples/update_items.py`: atualiza itens com dry-run por padrão.
- `examples/meli_http_client.py`: cliente HTTP reutilizável com retry/backoff.
- `input/item_updates.example.json`: exemplo de payload para atualização.

## Começando

1. Leia os guias em `docs/` na ordem.
2. Instale dependências mínimas:

```bash
python -m pip install requests
```

3. Dependências opcionais para XLSX:

```bash
python -m pip install pandas openpyxl
```

4. Execute os exemplos em `examples/` após preencher as variáveis de ambiente.

## Fontes oficiais

- [Register your application](https://developers.mercadolivre.com.br/en_us/products-authentication-authorization/register-your-application)
- [Items & Searches (EN)](https://developers.mercadolivre.com.br/en_us/api-docs/items-and-searches)
- [Itens e Buscas (PT-BR)](https://developers.mercadolivre.com.br/pt_br/itens-e-buscas)
- [Obtenção do Access Token](https://developers.mercadolivre.com.br/pt_br/obtencao-do-access-token)
- [Sincronização de publicações (PT-BR)](https://developers.mercadolivre.com.br/pt_br/produto-sincronizacao-de-publicacoes)
