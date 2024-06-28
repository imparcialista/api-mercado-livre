import json
import os
import time
import pandas as pd
from tkinter import filedialog as dlg
import requests
from termcolor import colored
from datetime import datetime, timezone, timedelta


os.system('color')
apenas_itens_ativos = False
base = 'https://api.mercadolibre.com'

mensagem_base = (
    '\n[*] Escolha uma opção'
    '\n[1] Trocar de conta'
    '\n[2] Atualizar desconto por planilha'
    '\n')


def pegar_datas():
    datas = []

    data_e_hora_atuais = datetime.now()
    dif = timedelta(hours=-3)
    fuso = timezone(dif)
    data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso)

    data_e_hora_atuais = data_e_hora_sao_paulo
    pegar_dia = data_e_hora_atuais.day

    if pegar_dia == 1:
        dia = pegar_dia
    else:
        dia = pegar_dia - 1

    mes = data_e_hora_atuais.month + 1
    data_futuro = data_e_hora_atuais.replace(month=mes, day=dia)

    data_alterada_texto = data_e_hora_atuais.strftime('%Y-%m-%dT%H:%M:%S')
    data_futuro_texto = data_futuro.strftime('%Y-%m-%dT%H:%M:%S')

    datas.append(data_alterada_texto)
    datas.append(data_futuro_texto)

    return datas


def msg_dif(cor, lugar, mensagem):
    linha = f'{"-" * (len(mensagem))}\n'

    texto = f'{mensagem}'

    if lugar == 'cima':
        print(colored(f'{linha}{texto}', cor))

    elif lugar == 'baixo':
        print(colored(f'{texto}{linha}', cor))

    elif lugar == 'ambos':
        print(colored(f'{linha}{texto}\n{linha}', cor))

    else:
        print(colored(f'{texto}', cor))


def msg(mensagem):
    msg_dif('white', '', f'{mensagem}')


def msg_cima(mensagem):
    msg_dif('white', 'cima', f'{mensagem}')


def msg_aviso(mensagem):
    msg_dif('yellow', '', f'{mensagem}')


def msg_alerta(mensagem):
    msg_dif('yellow', '', f'{mensagem}')


def msg_destaque(mensagem):
    msg_dif('green', 'ambos', f'{mensagem}')


def fazer_reqs(url, tv):
    headers = {'Authorization': f'Bearer {tv}'}
    resposta = requests.get(f'{url}', headers=headers)

    tentativa = 1
    while tentativa < 12:
        if resposta.status_code != 200:
            if tentativa == 11:
                msg_alerta('Número máximo de tentativas excedido')
                quit()

            else:
                msg_aviso(f'Tentativa {tentativa} | Falha na requisição')
                tentativa += 1
                time.sleep(1)

        else:
            resposta = resposta.json()
            # print(resposta)
            return resposta


def configurar_conta():
    conta_configurada = False
    while not conta_configurada:
        msg_cima('Insira o Access Token')
        tv = input(str('> '))

        headers = {'Authorization': f'Bearer {tv}'}
        resposta = requests.get(f'{base}/users/me', headers=headers)

        if resposta.status_code == 200:
            os.system('CLS')
            msg_destaque('Programa feito por @imparcialista  v1.2.5')
            msg(f'Conta conectada: {nome_conta(tv)}')
            return tv

        else:
            msg_aviso('Access Token inválido ou expirado')


def nome_conta(tv):
    nome_retorno = fazer_reqs(f'{base}/users/me', tv)
    conta = nome_retorno['nickname']
    return conta


def id_conta(tv):
    id_retorno = fazer_reqs(f'{base}/users/me', tv)
    id_seller = id_retorno['id']
    return id_seller


def preco_imprimir(preco):
    try:
        preco = float(preco)
    except:
        pass

    preco = str(preco)
    preco = preco.replace('.', ',')

    return preco


def atualizar(produto, valor_atualizar, tv, tipo, modo):
    url = f'{base}/items/{produto}'
    info_prd = fazer_reqs(url, tv)
    vendedor = nome_conta(tv)
    tit_prd = info_prd['title']

    aviso = 'yellow'
    sucesso = 'green'
    erro = 'red'
    normal = 'white'

    # SKU
    atributos = info_prd['attributes']
    sku_prd = ''

    for atributo in atributos:
        if atributo['id'] == 'SELLER_SKU':
            sku_prd = atributo['values'][0]['name']
            break

    # Envio
    tipo_envio = info_prd['shipping']['logistic_type']
    frete = info_prd['shipping']['free_shipping']

    if frete:
        frete = 'Grátis'
    else:
        frete = 'Pago'

    if tipo_envio == 'cross_docking':
        envio = 'Normal'

    elif tipo_envio == 'fulfillment':
        envio = 'Full'

    elif tipo_envio == 'not_specified':
        envio = 'Não especificado'

    else:
        envio = 'Não especificado'

    # Status
    if info_prd['status'] == 'active':
        status = 'Ativo'

    elif info_prd['status'] == 'paused':
        status = 'Pausado'

    elif info_prd['status'] == 'closed':
        status = 'Fechado'

    elif info_prd['status'] == 'under_review':
        status = 'Sob revisão'
    else:
        status = 'Outro'

    # Canal de venda
    if len(info_prd['channels']) == 2:
        canal = 'Ambos'

    elif info_prd['channels'][0] == 'marketplace':
        canal = 'Mercado Livre'

    elif info_prd['channels'][0] == 'mshops':
        canal = 'Mercado Shops'

    else:
        canal = 'Não especificado'

    msg_base = f'{status} | {produto} | {envio} | {frete} | {canal}'
    linha_ret = [vendedor, status, sku_prd, produto, envio, frete, canal, tit_prd]


    def retorno_linha(msg_ret, cor, lista_linha):
        msg_imprimir = f'{msg_base} | {msg_ret} | {tit_prd}'
        msg_dif(cor, '', msg_imprimir)
        lista_linha.append(msg_ret)
        return lista_linha


    preco_produto = info_prd['price']
    prc_org_prd = info_prd['original_price']
    prc_org_prd = str(prc_org_prd)
    possui_desconto = False

    if prc_org_prd != 'None' and prc_org_prd != 'Null':
        possui_desconto = True

    supermercado = False
    if type(valor_atualizar) is list:
        valor_mercado_livre = valor_atualizar[0]
        valor_supermercado = valor_atualizar[1]

        if 'supermarket_eligible' in info_prd['tags']:
            novo_valor = valor_supermercado
            supermercado = True
        else:
            supermercado = False
            novo_valor = valor_mercado_livre
    else:
        novo_valor = valor_atualizar


    def remover_desconto():
        url_desc = (f'{base}/seller-promotions/items'
                    f'/{produto}?promotion_type=PRICE_DISCOUNT&app_version=v2')
        headers_desc = {'Authorization': f'Bearer {tv}'}
        requests.request('DELETE', url=url_desc, headers=headers_desc)


    def dar_desconto():
        datas_desconto = pegar_datas()
        dt_desconto = datas_desconto[0]
        dt_futuro = datas_desconto[1]

        payload_desc = json.dumps(
                {
                    'deal_price'    : float(novo_valor), 'start_date': dt_desconto, 'finish_date': dt_futuro,
                    'promotion_type': 'PRICE_DISCOUNT'
                    }
                )

        url_desc = f'{base}/seller-promotions/items/{produto}?app_version=v2'
        headers_desc = {'Authorization': f'Bearer {tv}'}
        resposta_desc = requests.request('POST', url=url_desc, headers=headers_desc, data=payload_desc)

        if resposta_desc.status_code == 201:
            mensagem_desc = f'Desconto criado: De R$ {preco_produto} por R$ {novo_valor}'
            linha_retorno_desc = retorno_linha(mensagem_desc, sucesso, linha_ret)
            return linha_retorno_desc

        else:
            mensagem_desc = f'Não pôde ser alterado'
            linha_retorno_desc = retorno_linha(mensagem_desc, erro, linha_ret)
            return linha_retorno_desc


    def arrumar_preco(novo_preco):
        if preco_produto == novo_preco:
            mensagem_prc = f'Preço correto'
            linha_retorno_prc = retorno_linha(mensagem_prc, normal, linha_ret)
            return linha_retorno_prc

        if not supermercado:
            if preco_produto < 79 and frete == 'Grátis':
                input('Produto com frete grátis abaixo de 79, por favor altere.\nAperte ENTER para continuar')

            if preco_produto >= 79:
                if novo_valor < 79:
                    mensagem_prc = f'Não alterar: Novo valor abaixo do valor de frete grátis'
                    linha_retorno_prc = retorno_linha(mensagem_prc, normal, linha_ret)
                    return linha_retorno_prc

        remover_desconto()
        time.sleep(0.5)

        payload_prc = json.dumps({'price': novo_preco})

        headers_prc = {'Authorization': f'Bearer {tv}'}
        resposta_prc = requests.put(url=url, headers=headers_prc, data=payload_prc)

        # print(resposta_prc.json())

        if resposta_prc.status_code == 200:
            mensagem_prc = f'Preço alterado de R$ {preco_produto} para R$ {novo_preco}'
            linha_retorno_prc = retorno_linha(mensagem_prc, sucesso, linha_ret)
            return linha_retorno_prc

        else:
            mensagem_prc = f'Não pôde ser alterado'
            linha_retorno_prc = retorno_linha(mensagem_prc, erro, linha_ret)
            return linha_retorno_prc


    preco_min = novo_valor / 0.95
    preco_max = novo_valor / 0.41

    print(f'Primeira parada: {preco_min} min | {preco_max} max')

    preco_min = f'{preco_min:.2f}'
    preco_max = f'{preco_max:.2f}'

    print(f'Segunda parada: {preco_min} min | {preco_max} max')

    preco_min = float(preco_min)
    preco_max = float(preco_max)

    print(f'Terceira parada: {preco_min} min | {preco_max} max')

    if possui_desconto:
        preco_atual = float(prc_org_prd)
    else:
        preco_atual = float(preco_produto)

    if preco_atual < preco_min or preco_atual > preco_max:
        mensagem = f'Preço ({preco_atual}) Fora do intervalo permitido ({preco_min}) até ({preco_max})'
        retorno_linha(mensagem, aviso, linha_ret)
        arrumar_preco(preco_min)
        time.sleep(1)

    else:
        pass

    if tipo == 'estoque':
        est_prd = info_prd['available_quantity']

        mini_espera = False
        if valor_atualizar <= 0:
            valor_atualizar = 0
            if est_prd > 0:
                mini_espera = True
        else:
            if est_prd <= 0:
                mini_espera = True

        # Produtos do full não podem ser alterados
        if info_prd['shipping'] == 'Full':
            mensagem = f'Estoque no Full'
            linha_retorno = retorno_linha(mensagem, aviso, linha_ret)
            return linha_retorno

        # Não vamos trocar um valor pelo mesmo valor, nós apenas deixamos como está
        if valor_atualizar == est_prd:
            mensagem = f'Estoque correto'
            linha_retorno = retorno_linha(mensagem, normal, linha_ret)
            return linha_retorno

        # Podemos ter produtos com estoque, mas que estejam inativos, nesse caso, vamos tentar atualizar para ativo
        if valor_atualizar > 0:
            payload = json.dumps({'available_quantity': valor_atualizar, 'status': 'active'})
        else:
            payload = json.dumps({'available_quantity': valor_atualizar})

        headers = {'Authorization': f'Bearer {tv}'}
        resposta = requests.put(url=url, headers=headers, data=payload)

        if resposta.status_code == 200:
            mensagem = f'Estoque alterado de {est_prd} para {valor_atualizar}'
            if mini_espera:
                time.sleep(3)

            linha_retorno = retorno_linha(mensagem, sucesso, linha_ret)
            return linha_retorno

        else:
            mensagem = f'Não pôde ser alterado {resposta.status_code}'
            linha_retorno = retorno_linha(mensagem, erro, linha_ret)
            return linha_retorno

    elif tipo == 'desconto':
        if status != 'Ativo':
            mensagem = f'Anúncio inativo'
            linha_retorno = retorno_linha(mensagem, normal, linha_ret)
            return linha_retorno

        # Produto possui desconto
        if possui_desconto:
            prc_comparar = preco_produto

            if float(novo_valor) < prc_comparar:
                if not supermercado:
                    if prc_comparar < 79 and frete == 'Grátis':
                        input('Produto com frete grátis abaixo de 79, por favor altere.\nAperte ENTER para continuar')

                    if prc_comparar >= 79:
                        if novo_valor < 79:
                            mensagem = f'Não alterar: Desconto abaixo do valor de frete grátis'
                            linha_retorno = retorno_linha(mensagem, normal, linha_ret)
                            return linha_retorno

                mensagem = (f'Pode ser vendido por: R$ {preco_imprimir(novo_valor)}. Desconto atual: R$ '
                            f'{preco_imprimir(preco_produto)}')
                msg(mensagem)

                if modo == 'manual':
                    deseja_atualizar = input(str('Envie 1 se deseja alterar\n> '))
                else:
                    if modo == 'auto_modificar':
                        deseja_atualizar = '1'
                    else:
                        deseja_atualizar = '2'

                if deseja_atualizar == '1':
                    remover_desconto()
                    msg_dif('yellow', '', 'Recriando promoção, por favor aguarde...')
                    time.sleep(15)

                    linha_retorno = dar_desconto()
                    return linha_retorno

                else:
                    linha_retorno = retorno_linha(mensagem, normal, linha_ret)
                    return linha_retorno

            else:
                mensagem = f'Promoção ativa: De R$ {preco_imprimir(prc_org_prd)} por R$ {preco_imprimir(preco_produto)}'
                linha_retorno = retorno_linha(mensagem, normal, linha_ret)
                return linha_retorno

        else:
            if not supermercado:
                if preco_produto < 79 and frete == 'Grátis':
                    input('Produto com frete grátis abaixo de 79, por favor altere.\nAperte ENTER para continuar')

                if preco_produto >= 79:
                    if novo_valor < 79:
                        mensagem = f'Não alterar: Desconto abaixo do valor de frete grátis'
                        linha_retorno = retorno_linha(mensagem, normal, linha_ret)
                        return linha_retorno

            linha_retorno = dar_desconto()
            return linha_retorno

    elif tipo == 'preço':

        # Produto possui desconto
        if possui_desconto:
            prc_comparar = preco_produto

            if float(novo_valor) < prc_comparar:
                if not supermercado:
                    if prc_comparar < 79 and frete == 'Grátis':
                        input('Produto com frete grátis abaixo de 79, por favor altere.\nAperte ENTER para continuar')

                    if prc_comparar >= 79:
                        if novo_valor < 79:
                            mensagem = f'Não alterar: Desconto abaixo do valor de frete grátis'
                            linha_retorno = retorno_linha(mensagem, normal, linha_ret)
                            return linha_retorno

                mensagem = (f'Pode ser vendido por: R$ {preco_imprimir(novo_valor)}. Desconto atual: R$ '
                            f'{preco_imprimir(preco_produto)}')
                msg(mensagem)

                linha_retorno = retorno_linha(mensagem, normal, linha_ret)
                return linha_retorno
            else:
                mensagem = f'Promoção ativa: De R$ {preco_imprimir(prc_org_prd)} por R$ {preco_imprimir(preco_produto)}'
                linha_retorno = retorno_linha(mensagem, normal, linha_ret)
                return linha_retorno

        elif preco_produto == valor_atualizar:
            mensagem = f'Preço correto'
            linha_retorno = retorno_linha(mensagem, normal, linha_ret)
            return linha_retorno

        else:
            arrumar_preco(novo_valor)


def pegar_produtos(sku, valor_atualizar, tv, tipo, modo):
    lista_feitos = []
    paginas = 0
    url = f'{base}/users/{id_conta(tv)}/items/search?seller_sku={sku}&offset={paginas}'

    resposta = fazer_reqs(url, tv)
    quantidade_de_an = resposta['paging']['total']

    if quantidade_de_an == 0:
        mensagem = 'Nenhum anúncio encontrado'
        msg_dif('red', '', mensagem)
        lista_qtd_zero = [mensagem]
        lista_feitos.append(lista_qtd_zero)
        return lista_feitos

    else:
        if quantidade_de_an <= 50:
            for produto in resposta['results']:
                feito = atualizar(produto, valor_atualizar, tv, tipo, modo)
                lista_feitos.append(feito)

        else:

            while quantidade_de_an > 0:
                quantidade_de_an -= 50
                paginas += 1

            for pagina in range(paginas):
                url = f'{base}/users/{id_conta(tv)}/items/search?seller_sku={sku}&offset={(pagina * 50)}'

                resposta = fazer_reqs(url, tv)

                for produto in resposta['results']:
                    feito = atualizar(produto, valor_atualizar, tv, tipo, modo)
                    lista_feitos.append(feito)

        return lista_feitos


def get_input():
    input_user = input(str('> '))
    input_user = input_user.lower()
    input_user = input_user.strip()
    return input_user


def pegar_sku():
    print()
    msg('[Digite VOLTAR para retornar ao menu anterior]')
    msg_cima('Qual SKU você deseja atualizar?')
    sku_escolhido_input = input('> ')
    sku_escolhido_input = sku_escolhido_input.strip()
    return sku_escolhido_input


def main():
    os.system('CLS')
    sair = False
    token = configurar_conta()

    msg_cima('Na recriação promoções, você deseja')
    msg(
            '[1] Modificar todos anúncios automaticamente\n'
            '[2] Prefiro escolher para cada anúncio\n'
            '[3] Não modificar nenhum anúncio'
            )
    escolha_modo = get_input()

    if escolha_modo == '1':
        modo_esc = 'auto_modificar'
    elif escolha_modo == '2':
        modo_esc = 'manual'
    else:
        msg_aviso('Nenhuma promoção vai ser recriada')
        modo_esc = 'nao_modificar'

    msg(mensagem_base)

    while not sair:
        escolha = get_input()

        if escolha == 'sair':
            msg_cima('Encerrando...')
            break

        elif escolha == '?' or escolha == 'ajuda':
            msg('Digite SAIR para encerrar')

        elif escolha == '1' or escolha == 'trocar de conta':
            token = configurar_conta()

        elif escolha == '2':
            if token == '':
                token = configurar_conta()

            planilha_atualizar = dlg.askopenfilename(filetypes=[('Arquivos excel', '.xlsx')])

            if planilha_atualizar != '':
                print()
                msg(f'Caminho do arquivo: {planilha_atualizar}')
                df_atualizar = pd.read_excel(planilha_atualizar)

                lista_sku = []
                valor_trocar = []
                desconto_sm = []
                estoque_mlb = []

                # planilha_geral = False

                if df_atualizar.columns[0] == 'SKU':
                    for sku_df in df_atualizar['SKU']:
                        lista_sku.append(sku_df)

                    planilha_geral = True
                    tipo_esc_plan = 'desconto'
                    msg_cima('Modo atualizar desconto por planilha selecionado')
                    msg_alerta('ATENÇÃO: Produtos com promoção ativa não serão alterados')

                    print('\nMODELO DE PLANILHA')
                    msg_cima(
                            '| SKU | PRC-MAX-ML | PRC-MIN-ML | DESC-ML | PRC-MAX-SM | PRC-MIN-SM | DESC-SM | '
                            'Estoque |'
                            )

                    for prc_df in df_atualizar['Desconto ML']:
                        valor_trocar.append(prc_df)
                        print(
                                f'Preço com desconto ML {prc_df} | Preço mínimo {prc_df / 0.95} | Preço máximo'
                                f' {prc_df / 0.41}'
                                )

                    for dsc_df in df_atualizar['Desconto SM']:
                        desconto_sm.append(dsc_df)
                        print(
                                f'Preço com desconto SM {dsc_df} | Preço mínimo {dsc_df / 0.95} | Preço máximo {
                                dsc_df / 0.41}'
                                )

                    for est_df in df_atualizar['Estoque']:
                        estoque_mlb.append(est_df)

                else:
                    msg_alerta('A planilha não segue um padrão para que seja atualizado')
                    continue

                msg(f'\n{len(df_atualizar["SKU"])} SKUs para atualizar\nDeseja continuar?\n[1] Sim | [2] Não')
                continuar = input(str('> '))

                if continuar == '1':
                    sku_disp = []
                    sku_nao_disp = []
                    registros = []

                    for inx_sku, lista_sku_value in enumerate(lista_sku):

                        sku_mlb = str(lista_sku[inx_sku])
                        valor_mlb = valor_trocar[inx_sku]

                        valor_desconto = desconto_sm[inx_sku]
                        est_mlb = estoque_mlb[inx_sku]
                        est_mlb = int(est_mlb)
                        valor_mlb = int(valor_mlb)

                        url_df = f'{base}/users/{id_conta(token)}/items/search?seller_sku={sku_mlb}&offset={0}'

                        resposta_df = fazer_reqs(url_df, token)
                        qtd_de_an = resposta_df['paging']['total']
                        print()

                        if qtd_de_an > 0:
                            base_imp = f'SKU: {sku_mlb} | {qtd_de_an} Anúncio'

                            valor_imp_novo = str(valor_mlb)

                            if planilha_geral:
                                valor_desconto_imp = str(valor_desconto)
                                valor_imp_novo.replace('.', ',')

                                complemento = (f'Estoque: {est_mlb} | '
                                               f'Preço Mercado Livre R$ {preco_imprimir(valor_imp_novo)} | '
                                               f'Preço Supermercado R$ {preco_imprimir(valor_desconto_imp)}')
                            else:
                                complemento = f'Estoque: {valor_mlb}'

                            if qtd_de_an == 1:
                                msg_dif('white', '', f'{base_imp} | {complemento}')

                            else:
                                msg_dif('white', '', f'{base_imp}s | {complemento}')

                            sku_disp.append(sku_mlb)

                            if planilha_geral:
                                valor_mlb = [valor_mlb, valor_desconto]
                                # registro_est = pegar_produtos(sku_mlb, est_mlb, token, 'estoque', modo_esc)
                                # registros.append(registro_est)

                            registro_sku = pegar_produtos(sku_mlb, valor_mlb, token, tipo_esc_plan, modo_esc)
                            registros.append(registro_sku)

                        else:
                            registro_nenhum_an = f'SKU: {sku_mlb} | Nenhum anúncio encontrado'
                            msg_alerta(registro_nenhum_an)
                            sku_nao_disp.append(sku_mlb)

                    msg(f'\nSKUs encontrados: {sku_disp}')
                    msg(f'\nSKUs não encontrados: {sku_nao_disp}\n')

                    nova_lista = []

                    for registro in registros:
                        for registro_in in registro:
                            nova_lista.append(registro_in)

                    nova_planilha = pd.DataFrame(
                            nova_lista,
                            columns=['Vendedor', 'Status', 'SKU', 'Código', 'Envio', 'Frete',
                                     'Canal', 'Título', 'Descrição']
                            )

                    data_registro = pegar_datas()
                    data_registro = data_registro[0]
                    data_registro = data_registro[:10]

                    nova_planilha.to_excel(f'{data_registro}-{nome_conta(token)}.xlsx', index=False)
                    print(f'Arquivo gerado Registros.xlsx')

                elif continuar == '2':
                    msg_alerta('Você escolheu não continuar')

                else:
                    msg_alerta('Opção inválida')

            else:
                msg_alerta('Você não selecionou nenhum arquivo')

        else:
            print()
            msg_alerta('Opção inválida | Escolha uma das opções')

            if token != '':
                msg_destaque(f'Conta conectada: {nome_conta(token)}')

        msg(mensagem_base)


if __name__ == '__main__':
    main()
