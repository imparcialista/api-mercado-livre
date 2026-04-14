# API Mercado Livre - Documentacao e exemplos em Python

Este repositório é focado em documentação prática da API do Mercado Livre, com exemplos em Python.

## Site de documentação

- Produção: [https://imparcialista.github.io/api-mercado-livre/](https://imparcialista.github.io/api-mercado-livre/)

## Stack de docs (MkDocs)

- Configuração: `mkdocs.yml`
- Conteúdo: pasta `docs/`
- Deploy: `.github/workflows/deploy-docs.yml`
- Dependências de docs: `requirements-docs.txt`

## Execução local da documentação

```bash
python -m pip install -r requirements-docs.txt
mkdocs serve
```

## Configuração do GitHub Pages (uma vez)

1. Repositório > `Settings` > `Pages`.
2. Em `Source`, selecione `GitHub Actions`.
3. Faça push na `main`.
4. Aguarde o workflow `Deploy Docs` concluir.

## Qualidade de documentação (CI)

- Workflow: `.github/workflows/docs-quality.yml`
- Checks automáticos:
  - `markdownlint` em `README.md` e `docs/**/*.md`
  - `lychee` para links quebrados

## Exemplos Python

Dependências mínimas:

```bash
python -m pip install requests
```

Dependências opcionais para XLSX:

```bash
python -m pip install pandas openpyxl
```
