---
title: Início
description: Portal da documentação da API Mercado Livre para integradores em Python.
tags:
  - home
  - docs
---

# API Mercado Livre para Integradores

<div class="home-hero" markdown>
Guia técnico para desenvolvedores que precisam integrar sistemas à API do Mercado Livre com segurança operacional.

[Repositório no GitHub](https://github.com/imparcialista/api-mercado-livre){ .md-button .md-button--primary }
[Começar pela autenticação](./01-criar-aplicativo-e-token.md){ .md-button }
</div>

## Trilhas de integração

<div class="home-grid" markdown>
<div class="home-card" markdown>
### Autenticação
- [Capítulo 01 · Autenticação OAuth e geração de tokens](./01-criar-aplicativo-e-token.md)
</div>
<div class="home-card" markdown>
### Catálogo e anúncios
- [Capítulo 02 · Consultar anúncios](./02-primeira-consulta-anuncios.md)
- [Capítulo 03 · Detalhes em lote](./03-detalhes-itens-lote-exportacao.md)
- [Capítulo 04 · Atualizar preço e estoque](./04-atualizar-preco-estoque.md)
</div>
<div class="home-card" markdown>
### Resiliência
- [Capítulo 05 · Erros, timeout e rate limit](./05-tratamento-erros-rate-limit.md)
- [Capítulo 09 · Notificações e webhooks](./09-notificacoes-webhooks.md)
</div>
<div class="home-card" markdown>
### Pós-venda
- [Capítulo 06 · Consultar pedidos e exportar](./06-consultar-pedidos.md)
- [Capítulo 07 · Envios, logística e rastreio](./07-envios-rastreio.md)
- [Capítulo 08 · Pagamentos e conciliação](./08-pagamentos-conciliacao.md)
</div>
</div>

## Leitura recomendada

1. Implemente autenticação (capítulo 01).
2. Colete e modele catálogo (capítulos 02 e 03).
3. Aplique atualizações com segurança (capítulo 04).
4. Endureça resiliência de produção (capítulo 05).
5. Integre rotinas de pedidos (capítulo 06).
6. Feche o pós-venda com envios, pagamentos e notificações (capítulos 07 a 09).

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
