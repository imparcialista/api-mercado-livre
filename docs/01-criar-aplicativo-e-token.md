---
title: Capítulo 01 · Autenticação OAuth e geração de tokens
description: Como registrar o app no DevCenter e executar o fluxo OAuth para obter access token e refresh token.
tags:
  - auth
  - oauth
  - tokens
---

# Capítulo 01 · Autenticação OAuth e geração de tokens

## Para quem é este capítulo

Para desenvolvedores que estão iniciando uma integração e ainda não têm credenciais válidas para chamar endpoints privados.

## Pré-requisitos

- Conta no Mercado Livre com acesso ao DevCenter.
- URL de callback (`redirect_uri`) HTTPS estável.
- Python 3.11+ (opcional para rodar scripts do repositório).

Este capítulo cobre o fluxo OAuth 2.0 para obter credenciais da API Mercado Livre.

## Etapa 1 · Criar o aplicativo no DevCenter

1. Acesse o DevCenter do Mercado Livre.
2. Crie um novo aplicativo.
3. Preencha nome, descrição e URL.
4. Configure a `Redirect URI` (URL de callback) que vai receber o `code` de autorização.
5. Salve e copie:
- `APP_ID` (client_id)
- `CLIENT_SECRET`

Sem `Redirect URI` correta, a autorização falha no retorno.

## Etapa 2 · Montar a URL de autorização

Abra no navegador uma URL como esta (ajuste domínio e parâmetros):

```text
https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=SEU_APP_ID&redirect_uri=SUA_REDIRECT_URI
```

Observações:
- Use a mesma `redirect_uri` cadastrada no app.
- Após login e consentimento, você será redirecionado para algo como:

```text
https://seu-dominio/callback?code=TG-xxxxxxxx
```

Copie o valor de `code`.

## Etapa 3 · Trocar `code` por `access_token`

Faça um POST para:

```text
https://api.mercadolibre.com/oauth/token
```

Payload (`application/x-www-form-urlencoded`):
- `grant_type=authorization_code`
- `client_id=APP_ID`
- `client_secret=CLIENT_SECRET`
- `code=CODE_RECEBIDO`
- `redirect_uri=REDIRECT_URI`

Resposta esperada inclui:
- `access_token`
- `refresh_token`
- `expires_in`

## Etapa 4 · Renovar token com `refresh_token`

Quando o `access_token` expirar, faça novo POST em `https://api.mercadolibre.com/oauth/token` com:
- `grant_type=refresh_token`
- `client_id`
- `client_secret`
- `refresh_token`

## Etapa 5 · Validar o token

```bash
curl -H "Authorization: Bearer SEU_ACCESS_TOKEN" https://api.mercadolibre.com/users/me
```

Se estiver correto, você receberá os dados do usuário autenticado.

## Segurança

- Nunca versionar `client_secret`, `access_token` ou `refresh_token`.
- Use variáveis de ambiente ou cofre de segredos.
- Trate renovação de token automaticamente no seu cliente.

## Referências

- [Criar aplicação no Mercado Livre](https://developers.mercadolivre.com.br/pt_br/pt_br/crie-uma-aplicacao-no-mercado-livre)
- [Obtenção do Access Token](https://developers.mercadolivre.com.br/pt_br/obtencao-do-access-token)
- [Autenticação e Autorização](https://developers.mercadolivre.com.br/pt_br/mensagens-post-venda/autenticacao-e-autorizacao)


