# API Mercado Livre - Documentacao e exemplos em Python

Este repositório é focado em documentação prática da API do Mercado Livre, com exemplos em Python.

## Site de documentação

- Produção: [https://imparcialista.github.io/api-mercado-livre/](https://imparcialista.github.io/api-mercado-livre/)
- Navegação local em Markdown: [docs/index.md](./docs/index.md)

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

## Execução local da documentação (opcional)

```bash
python -m pip install mkdocs mkdocs-material
mkdocs serve
```

## Configuração do GitHub Pages (uma vez)

1. Repositório > `Settings` > `Pages`.
2. Em `Source`, selecione `GitHub Actions`.
3. Faça push na `main`.
4. Aguarde o workflow `Deploy Docs` concluir.

## Exemplos Python

Dependências mínimas:

```bash
python -m pip install requests
```

Dependências opcionais para XLSX:

```bash
python -m pip install pandas openpyxl
```
