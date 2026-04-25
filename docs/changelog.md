---
title: Changelog
description: Histórico de mudanças da documentação e estrutura de publicação.
tags:
  - changelog
  - docs
---

# Changelog

## 2026-04-24

### Adicionado em 2026-04-24
- Capítulo 07 sobre envios, logística e rastreio.
- Capítulo 08 sobre pagamentos e conciliação.
- Capítulo 09 sobre notificações e webhooks.
- Receitas de apoio para investigar envio e processar notificações sem duplicidade.

### Alterado em 2026-04-24
- Home, navegação MkDocs e mapa de tags atualizados para incluir a trilha de pós-venda.

## 2026-04-14

### Adicionado em 2026-04-14
- Migração para fluxo MkDocs-first com `mkdocs.yml` e deploy por GitHub Actions.
- Capítulos 01 a 06 com exemplos Python.
- Seções de referência: `Tags`, `Cookbook` e `Snippets`.
- Snippets reutilizáveis por domínio em `docs/_snippets/`.
- Template de novo capítulo em `docs/template-novo-capitulo.md`.
- Dependências de docs em `requirements-docs.txt`.

### Alterado em 2026-04-14
- Navegação manual removida dos capítulos (anterior/próximo/home) em favor da navegação nativa do tema.
- Home da documentação convertida para portal de entrada.
- Workflow de deploy atualizado para instalar dependências via `requirements-docs.txt`.
