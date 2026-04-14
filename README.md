# API Mercado Livre - Documentacao e exemplos em Python

Este repositório agora é focado em documentação prática da API do Mercado Livre, com exemplos em Python.

## Estrutura

- `docs/01-criar-aplicativo-e-token.md`: passo a passo para criar aplicativo e gerar access token.
- `examples/oauth_exchange_token.py`: troca `authorization_code` por `access_token` + `refresh_token`.
- `examples/oauth_refresh_token.py`: gera novo `access_token` usando `refresh_token`.

## Começando

1. Leia o guia: `docs/01-criar-aplicativo-e-token.md`.
2. Instale dependências para os exemplos:

```bash
python -m pip install requests
```

3. Execute os exemplos em `examples/` após preencher as variáveis de ambiente.

## Fontes oficiais

- [Criar aplicação no Mercado Livre](https://developers.mercadolivre.com.br/pt_br/pt_br/crie-uma-aplicacao-no-mercado-livre)
- [Obtenção do Access Token](https://developers.mercadolivre.com.br/pt_br/obtencao-do-access-token)
- [Autenticação e Autorização](https://developers.mercadolivre.com.br/pt_br/mensagens-post-venda/autenticacao-e-autorizacao)
- [Configuração ou requisitos prévios](https://developers.mercadolivre.com.br/pt_br/configuracao-ou-requisitos-previos)
