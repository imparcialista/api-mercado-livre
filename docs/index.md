---
title: Início
description: Portal da documentação da API do Mercado Livre com trilha guiada, cookbook e snippets.
tags:
  - home
  - docs
---

# API Mercado Livre Docs

Documentação prática para integração com a API do Mercado Livre, com foco em exemplos Python e fluxos reais de operação.

[Ir para o repositório no GitHub](https://github.com/imparcialista/api-mercado-livre){ .md-button .md-button--primary }

## Trilha de aprendizado

### 1) Autenticação
- [01 - Criar aplicativo e gerar Access Token](./01-criar-aplicativo-e-token.md)

### 2) Catálogo e anúncios
- [02 - Primeira consulta de anúncios](./02-primeira-consulta-anuncios.md)
- [03 - Buscar detalhes dos itens em lote](./03-detalhes-itens-lote-exportacao.md)
- [04 - Atualizar preço e estoque](./04-atualizar-preco-estoque.md)

### 3) Operação resiliente
- [05 - Tratamento de erros e limites de taxa](./05-tratamento-erros-rate-limit.md)

### 4) Vendas
- [06 - Consultar pedidos e exportar](./06-consultar-pedidos.md)

## Como usar esta documentação

!!! tip "Fluxo recomendado"
    Siga os capítulos em ordem e execute os scripts da pasta `examples/` após configurar as variáveis de ambiente.

!!! info "Ambiente"
    Os exemplos usam Python 3.11+ e a biblioteca `requests`.

## Referência rápida

- [Cookbook](./cookbook.md): receitas prontas para tarefas operacionais.
- [Snippets](./snippets.md): blocos reutilizáveis por domínio.
- [Tags](./tags.md): navegação por assunto.

## Rodando localmente

```bash
python -m pip install mkdocs mkdocs-material
mkdocs serve
```

A documentação local abrirá em `http://127.0.0.1:8000`.

