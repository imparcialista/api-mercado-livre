---
title: Changelog
description: Histórico de mudanças da documentação e estrutura de publicação.
tags:
  - changelog
  - docs
---

# Changelog

## 2026-04-14

### Adicionado
- Migração para fluxo MkDocs-first com `mkdocs.yml` e deploy por GitHub Actions.
- Capítulos 01 a 06 com exemplos Python.
- Seções de referência: `Tags`, `Cookbook` e `Snippets`.
- Snippets reutilizáveis por domínio em `docs/_snippets/`.
- Template de novo capítulo em `docs/template-novo-capitulo.md`.
- Dependências de docs em `requirements-docs.txt`.

### Alterado
- Navegação manual removida dos capítulos (anterior/próximo/home) em favor da navegação nativa do tema.
- Home da documentação convertida para portal de entrada.
- Workflow de deploy atualizado para instalar dependências via `requirements-docs.txt`.
