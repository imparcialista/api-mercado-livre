---
title: Início
description: Portal da documentação da API Mercado Livre para integradores em Python.
tags:
  - home
  - docs
---

# API Mercado Livre para Integradores

Guia técnico para desenvolvedores que precisam integrar sistemas à API do Mercado Livre com segurança operacional.

[Repositório no GitHub](https://github.com/imparcialista/api-mercado-livre){ .md-button .md-button--primary }

## Trilhas de integração

### Autenticação
- [Capítulo 01 · Autenticação OAuth e geração de tokens](./01-criar-aplicativo-e-token.md)

### Catálogo e anúncios
- [Capítulo 02 · Consultar anúncios (items/search)](./02-primeira-consulta-anuncios.md)
- [Capítulo 03 · Detalhes de itens em lote e exportação](./03-detalhes-itens-lote-exportacao.md)
- [Capítulo 04 · Atualizar preço e estoque com segurança](./04-atualizar-preco-estoque.md)

### Resiliência de integração
- [Capítulo 05 · Resiliência: erros, timeout e rate limit](./05-tratamento-erros-rate-limit.md)

### Vendas
- [Capítulo 06 · Consultar pedidos e exportar](./06-consultar-pedidos.md)

## Leitura recomendada

1. Implemente autenticação (capítulo 01).
2. Colete e modele catálogo (capítulos 02 e 03).
3. Aplique atualizações com segurança (capítulo 04).
4. Endureça resiliência de produção (capítulo 05).
5. Integre rotinas de pedidos (capítulo 06).

## Referência de apoio

- [Cookbook](./cookbook.md)
- [Snippets](./snippets.md)
- [Tags](./tags.md)
- [Changelog](./changelog.md)

## Rodar localmente

```bash
python -m pip install -r requirements-docs.txt
mkdocs serve
```
