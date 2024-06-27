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
    '\n[2] Atualizar planilha'
    '\n[3] Abrir a planilha'
    '\n[4] Atualizar por SKU'
    '\n[5] Atualizar por planilha'
    '\n[6] Mais vendidos por categoria'
    '\n[7] Clonar anúncios de uma conta (BETA)'
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


def fazer_post(id_mlb, tv1, tv2):
    url_id = f'{base}/items/{id_mlb}'
    corpo_produto = fazer_reqs(url_id, tv1)

    url_id = f'{base}/items'

    lista_nao_pode = [
        'original_price', 'deal_ids', 'descriptions', 'seller_contact', 'id', 'seller_id', 'thumbnail',
        'last_updated', 'inventory_id', 'permalink', 'differential_pricing', 'stop_time',
        'sold_quantity', 'user_product_id', 'item_relations', 'variations', 'base_price', 'sub_status',
        'initial_quantity', 'date_created', 'expiration_time', 'warnings', 'end_time', 'health',
        'listing_source', 'international_delivery_mode', 'thumbnail_id', 'parent_item_id', 'geolocation',
        'start_time', 'shipping', 'official_store_id', 'seller_address', 'automatic_relist',
        'tags', 'coverage_areas', 'location', 'sale_terms', 'warranty'
        ]

    lista_chave = []
    lista_valor = []

    for chave in corpo_produto:
        if chave in lista_nao_pode:
            pass

        else:
            valor = corpo_produto[f'{chave}']
            lista_chave.append(chave)
            lista_valor.append(valor)

    atributo_chave = []
    for inx, atributo in enumerate(lista_chave):
        valor_atributo = lista_valor[inx]

        atributos_nao_pode = ['PACKAGE_HEIGHT', 'PRODUCT_FEATURES', 'PACKAGE_WEIGHT', 'SHIPMENT_PACKING',
                              'PACKAGE_LENGTH', 'PACKAGE_WIDTH']

        if atributo == 'attributes':
            for item in valor_atributo:
                if item['id'] in atributos_nao_pode:
                    pass
                else:
                    atributo_chave.append(item)
                    lista_valor[inx] = [item]

    dicionario = dict(zip(lista_chave, lista_valor))

    payload = json.dumps(dicionario)
    headers = {'Authorization': f'Bearer {tv2}'}

    resposta = requests.request('POST', url=url_id, headers=headers, data=payload)

    resultado = 'NÃO CLONADO' if resposta.status_code != 201 else 'CLONADO'

    resposta = resposta.json()
    retorno = [resultado, id_mlb, resposta]
    print(retorno)
    time.sleep(1)
    return retorno


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


def pegar_scroll_id(tv):
    url = f'{base}/users/{id_conta(tv)}/items/search?search_type=scan&limit=100'
    resposta = fazer_reqs(url, tv)
    return resposta


def proxima_pagina(scroll, tv):
    url = f'{base}/users/{id_conta(tv)}/items/search?search_type=scan&scroll_id={scroll}&limit=100'
    resposta = fazer_reqs(url, tv)
    return resposta


def pegar_todos_ids(tv):
    lista = []
    inicio_timer = time.time()
    paginas = 0

    filtro = 'include_filters=true&status=active' if apenas_itens_ativos else ''

    url = f'{base}/users/{id_conta(tv)}/items/search?{filtro}&offset={0}'
    resposta = fazer_reqs(url, tv)

    quantidade_de_an = resposta['paging']['total']

    if quantidade_de_an == 0:
        msg_cima('Nenhum anúncio ativo. Programa finalizado')
        return

    if quantidade_de_an > 1000:
        msg_cima(f'Quantidade de anúncios: {quantidade_de_an}')

        while quantidade_de_an > 0:
            quantidade_de_an -= 100
            paginas += 1

        paginas = paginas - 1

        lista_scroll = []
        primeiro_scroll = pegar_scroll_id(tv)
        msg_cima('Coletando IDs, por favor aguarde...')

        lista_scroll.append(primeiro_scroll['scroll_id'])
        for produto in primeiro_scroll['results']:
            lista.append(produto)


        def gerar_scroll(scroll_anterior):
            scroll = proxima_pagina(scroll_anterior, tv)

            for id_mlb in scroll['results']:
                lista.append(id_mlb)

            lista_scroll.append(scroll['scroll_id'])


        for pagina in range(paginas):
            gerar_scroll(lista_scroll[pagina])

    else:
        quantidade_de_an = resposta['paging']['total']

        msg_cima(f'Quantidade de anúncios: {quantidade_de_an}')

        while quantidade_de_an > 0:
            quantidade_de_an -= 50
            paginas += 1

        for pagina in range(paginas):
            url = f'{base}/users/{id_conta(tv)}/items/search?{filtro}&offset={pagina * 50}'

            resposta = fazer_reqs(url, tv)

            for produto in resposta['results']:
                lista.append(produto)

    if not os.path.exists(f'Arquivos/{nome_conta(tv)}'):
        os.makedirs(f'Arquivos/{nome_conta(tv)}')
        msg_cima(f'Pasta {nome_conta(tv)} criada')

    arquivo_json = f'Arquivos/{nome_conta(tv)}/{id_conta(tv)}-ids_mlb.json'

    if os.path.exists(arquivo_json):
        os.remove(arquivo_json)

    with open(arquivo_json, 'w') as outfile:
        json.dump(lista, outfile)

    fim_timer = time.time()
    msg_cima(f'{nome_conta(tv)}: Todos os IDS foram coletados ')
    msg_cima(f'Tempo de execução: {(int(fim_timer - inicio_timer)) + 1} segundos')

    return lista


def exportar_para_planilha(lista_json: list, colunas_drop: list, tv):
    arquivo_json = f'Arquivos/{(nome_conta(tv))}/{id_conta(tv)}-retorno-produtos.json'

    if os.path.exists(arquivo_json):
        os.remove(arquivo_json)

    with open(arquivo_json, 'w') as outfile:
        json.dump(lista_json, outfile)

    df = pd.read_json(arquivo_json)
    df = df.drop(colunas_drop, axis=1, errors='ignore')
    planilha = f'Arquivos/{nome_conta(tv)}/{id_conta(tv)}-planilha-produtos.xlsx'

    if os.path.exists(planilha):
        os.remove(planilha)

    df['date_created'] = pd.to_datetime(df['date_created'], format='%d/%m/%Y %H:%M:%S')
    df['last_updated'] = pd.to_datetime(df['last_updated'], format='%d/%m/%Y %H:%M:%S')

    df = df.sort_values(by='last_updated', ascending=False)
    df.to_excel(planilha, index=False)

    msg(f'Planilha gerada')


def gerar_planilha(tv):
    ids_mlb = f'Arquivos/{nome_conta(tv)}/{id_conta(tv)}-ids_mlb.json'
    lista_retorno = []
    lista_geral = []
    gap_vinte = 0
    paginas = 0

    if not os.path.exists(ids_mlb):
        pegar_todos_ids(tv)

    inicio_timer = time.time()

    df = pd.read_json(ids_mlb)
    quantidade_de_an = len(df)

    msg_cima(f'Quantidade de anúncios: {quantidade_de_an}')

    while quantidade_de_an > 0:
        quantidade_de_an -= 20
        paginas += 1

    msg_cima(f'Páginas para percorrer: {paginas}')

    for pagina in range(paginas):
        inicio = gap_vinte
        fim = gap_vinte + 20
        itens = df[inicio:fim]
        lista_concatenada = ','.join(itens[0])
        lista_geral.append(lista_concatenada)
        gap_vinte += 20

    msg(f'Por favor aguarde...')

    for i_pack, pack in enumerate(lista_geral):

        url = f'{base}/items?ids={pack}'
        retorno = fazer_reqs(url, tv)

        for grupo_de_itens in retorno:
            body = grupo_de_itens['body']

            envio = body['shipping']['logistic_type']
            if envio == 'cross_docking':
                body['shipping'] = 'Normal'

            elif envio == 'fulfillment':
                body['shipping'] = 'Full'

            elif envio == 'not_specified':
                body['shipping'] = 'Não especificado'

            else:
                body['shipping'] = 'Não especificado'

            atributos = body['attributes']

            for atributo in atributos:
                if atributo['id'] == 'SELLER_SKU':
                    sku = atributo['values'][0]['name']
                    body['attributes'] = sku
                    break

                else:
                    body['attributes'] = ''

            if body['status'] == 'active':
                body['status'] = 'Ativo'

            elif body['status'] == 'paused':
                body['status'] = 'Pausado'

            elif body['status'] == 'closed':
                body['status'] = 'Fechado'

            elif body['status'] == 'under_review':
                body['status'] = 'Sob revisão'
            else:
                body['status'] = 'Outro'

            criado = body['date_created']
            atua = body['last_updated']

            body['date_created'] = f'{criado[8:10]}/{criado[5:7]}/{criado[0:4]} {criado[11:19]}'
            body['last_updated'] = f'{atua[8:10]}/{atua[5:7]}/{atua[0:4]} {atua[11:19]}'

            porcentagem = body['health']

            try:
                float(porcentagem)
                body['health'] = f'{(float(porcentagem)) * 100}%'

            except:
                body['health'] = ''

            if body['catalog_listing'] == 'TRUE':
                body['catalog_listing'] = 'Verdadeiro'
            else:
                body['catalog_listing'] = 'Falso'

            if len(body['item_relations']) == 0:
                body['item_relations'] = 'Sem relação'
            else:
                body['item_relations'] = body['item_relations'][0]['id']

            if len(body['channels']) == 2:
                body['channels'] = 'Vendido em ambos canais'

            elif body['channels'][0] == 'marketplace':
                body['channels'] = 'Vendido apenas no Mercado Livre'

            elif body['channels'][0] == 'mshops':
                body['channels'] = 'Vendido apenas no Mercado Shops'

            else:
                body['channels'] = 'Não especificado'

            lista_retorno.append(body)

    fim_timer = time.time()
    msg(f'Informações coletadas. Tempo de execução: {(int(fim_timer - inicio_timer)) + 1} segundos')

    drops = [
        'site_id', 'official_store_id', 'user_product_id', 'seller_id', 'category_id', 'inventory_id',
        'currency_id', 'sale_terms', 'buying_mode', 'listing_type_id', 'start_time', 'stop_time', 'end_time',
        'expiration_time', 'thumbnail_id', 'pictures', 'video_id', 'descriptions', 'accepts_mercadopago',
        'non_mercado_pago_payment_methods', 'international_delivery_mode', 'seller_address', 'seller_contact',
        'location', 'geolocation', 'coverage_areas', 'warnings', 'listing_source', 'variations', 'sub_status',
        'warranty', 'parent_item_id', 'differential_pricing', 'deal_ids', 'automatic_relist', 'start_time',
        'stop_time', 'end_time', 'expiration_time', 'condition', 'seller_custom_field'
        ]

    exportar_para_planilha(lista_retorno, drops, tv)


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
    info_produto = fazer_reqs(url, tv)
    vendedor = nome_conta(tv)
    tit_produto = info_produto['title']

    aviso = 'yellow'
    sucesso = 'green'
    erro = 'red'
    normal = 'white'

    # SKU
    atributos = info_produto['attributes']
    sku_produto = ''

    for atributo in atributos:
        if atributo['id'] == 'SELLER_SKU':
            sku_produto = atributo['values'][0]['name']
            break

    # Envio
    tipo_envio = info_produto['shipping']['logistic_type']
    frete = info_produto['shipping']['free_shipping']

    frete = 'Grátis' if frete else 'Pago'

    if tipo_envio == 'cross_docking':
        envio = 'Normal'

    elif tipo_envio == 'fulfillment':
        envio = 'Full'

    elif tipo_envio == 'not_specified':
        envio = 'Não especificado'

    else:
        envio = 'Não especificado'

    # Status
    if info_produto['status'] == 'active':
        status = 'Ativo'

    elif info_produto['status'] == 'paused':
        status = 'Pausado'

    elif info_produto['status'] == 'closed':
        status = 'Fechado'

    elif info_produto['status'] == 'under_review':
        status = 'Sob revisão'
    else:
        status = 'Outro'

    # Canal de venda
    if len(info_produto['channels']) == 2:
        canal = 'Ambos'

    elif info_produto['channels'][0] == 'marketplace':
        canal = 'Mercado Livre'

    elif info_produto['channels'][0] == 'mshops':
        canal = 'Mercado Shops'

    else:
        canal = 'Não especificado'

    msg_base = f'{status} | {produto} | {envio} | {frete} | {canal}'
    linha_ret = [vendedor, status, sku_produto, produto, envio, frete, canal, tit_produto]


    def retorno_linha(msg_ret, cor, lista_linha):
        msg_imprimir = f'{msg_base} | {msg_ret} | {tit_produto}'
        msg_dif(cor, '', msg_imprimir)
        lista_linha.append(msg_ret)
        return lista_linha


    if tipo == 'estoque':
        est_produto = info_produto['available_quantity']

        mini_espera = False
        if valor_atualizar <= 0:
            valor_atualizar = 0
            if est_produto > 0:
                mini_espera = True
        else:
            if est_produto <= 0:
                mini_espera = True

        # Produtos do full não podem ser alterados
        if info_produto['shipping'] == 'Full':
            linha_ret = retorno_linha('Estoque no Full', aviso, linha_ret)
            return linha_ret

        # Não vamos trocar um valor pelo mesmo valor, nós apenas deixamos como está
        if valor_atualizar == est_produto:
            linha_ret = retorno_linha('Estoque correto', normal, linha_ret)
            return linha_ret

        # Podemos ter produtos com estoque, mas que estejam inativos, nesse caso, vamos tentar atualizar para ativo
        if valor_atualizar > 0:
            payload = json.dumps({'available_quantity': valor_atualizar, 'status': 'active'})
        else:
            payload = json.dumps({'available_quantity': valor_atualizar})

        headers = {'Authorization': f'Bearer {tv}'}
        resposta = requests.put(url=url, headers=headers, data=payload)

        if resposta.status_code == 200:
            mensagem = f'Estoque alterado de {est_produto} para {valor_atualizar}'
            if mini_espera:
                time.sleep(1)

            linha_ret = retorno_linha(mensagem, sucesso, linha_ret)
            return linha_ret

        else:
            linha_ret = retorno_linha('Não pôde ser alterado', erro, linha_ret)
            return linha_ret

    elif tipo == 'sku':
        payload = json.dumps({'attributes': [{'id': 'SELLER_SKU', 'value_name': f'{valor_atualizar}'}]})

        headers = {'Authorization': f'Bearer {tv}'}
        resposta = requests.put(url=url, headers=headers, data=payload)

        if resposta.status_code == 200:
            linha_ret = retorno_linha(f'SKU novo: {valor_atualizar}', sucesso, linha_ret)
            return linha_ret

        else:
            linha_ret = retorno_linha('Não pôde ser alterado', erro, linha_ret)
            return linha_ret
    else:
        supermercado = False
        if type(valor_atualizar) is list:
            valor_mercado_livre = valor_atualizar[0]
            valor_supermercado = valor_atualizar[1]

            if 'supermarket_eligible' in info_produto['tags']:
                novo_valor = valor_supermercado
                supermercado = True
            else:
                supermercado = False
                novo_valor = valor_mercado_livre
        else:
            novo_valor = valor_atualizar

        preco_produto = info_produto['price']
        preco_original_produto = info_produto['original_price']
        preco_original_produto = str(preco_original_produto)

        # print(f'preco_produto: {preco_produto} | preco_original_produto: {preco_original_produto}')

        preco = False
        desconto = False

        if tipo == 'preço':
            preco = True
        elif tipo == 'desconto':
            desconto = True
        else:
            print('Você supostamente não deveria ver essa mensagem')

        # Produto possui desconto
        if preco_original_produto != 'None' and preco_original_produto != 'Null':
            preco_comparar = preco_produto

            if float(novo_valor) < preco_comparar:
                if not supermercado:
                    if preco_comparar < 79 and frete == 'Grátis':
                        input(
                            'Produto com frete grátis abaixo de 79, por favor altere.\nAperte ENTER para continuar')

                    if preco_comparar >= 79:
                        if novo_valor < 79:
                            mensagem = f'Não alterar: Desconto abaixo do valor de frete grátis'
                            linha_ret = retorno_linha(mensagem, normal, linha_ret)
                            return linha_ret

                mensagem = (f'Pode ser vendido por: R$ {preco_imprimir(novo_valor)}. Desconto atual: R$ '
                            f'{preco_imprimir(preco_produto)} | {sku_produto} | {produto} | {tit_produto}')
                msg(mensagem)

                if desconto:
                    if modo == 'manual':
                        deseja_atualizar = input(str('Envie 1 se deseja alterar\n> '))
                    else:
                        if modo == 'auto_modificar':
                            deseja_atualizar = '1'
                        else:
                            deseja_atualizar = '2'

                    if deseja_atualizar == '1':
                        url = f'{base}/seller-promotions/items/{produto}?promotion_type=PRICE_DISCOUNT&app_version=v2'
                        headers = {'Authorization': f'Bearer {tv}'}
                        requests.request('DELETE', url=url, headers=headers)
                        msg_dif('yellow', '', 'Recriando promoção, por favor aguarde...')
                        time.sleep(15)

                        datas_desconto = pegar_datas()

                        dt_desconto = datas_desconto[0]
                        dt_futuro = datas_desconto[1]

                        payload = json.dumps(
                                {
                                    'deal_price'    : float(novo_valor),
                                    'start_date'    : dt_desconto,
                                    'finish_date'   : dt_futuro,
                                    'promotion_type': 'PRICE_DISCOUNT'
                                    })

                        url = f'{base}/seller-promotions/items/{produto}?app_version=v2'

                        headers = {'Authorization': f'Bearer {tv}'}
                        resposta = requests.request('POST', url=url, headers=headers, data=payload)

                        if resposta.status_code == 201:
                            mensagem = (f'Desconto recriado: De R$ {preco_imprimir(preco_produto)} por R$ '
                                        f'{preco_imprimir(novo_valor)}')
                            linha_ret = retorno_linha(mensagem, sucesso, linha_ret)
                            return linha_ret

                        else:
                            linha_ret = retorno_linha('Não pôde ser alterado', erro, linha_ret)
                            return linha_ret

                else:
                    linha_ret = retorno_linha(mensagem, normal, linha_ret)
                    return linha_ret

            else:
                mensagem = f'Promoção ativa: De R$ {preco_imprimir(preco_original_produto)} por R$ {preco_imprimir(preco_produto)}'
                linha_ret = retorno_linha(mensagem, normal, linha_ret)
                return linha_ret

        elif preco_produto == valor_atualizar:
            linha_ret = retorno_linha('Preço correto', normal, linha_ret)
            return linha_ret

        else:
            if not supermercado:
                if preco_produto < 79 and frete == 'Grátis':
                    input('Produto com frete grátis abaixo de 79, por favor altere.\nAperte ENTER para continuar')

                if preco_produto >= 79:
                    if novo_valor < 79:
                        mensagem = f'Não alterar: Desconto abaixo do valor de frete grátis'
                        linha_ret = retorno_linha(mensagem, normal, linha_ret)
                        return linha_ret

            if preco:
                payload = json.dumps({'price': valor_atualizar})

                headers = {'Authorization': f'Bearer {tv}'}
                resposta = requests.put(url=url, headers=headers, data=payload)

                if resposta.status_code == 200:
                    mensagem = f'Preço alterado de R$ {preco_imprimir(preco_produto)} para R$ {preco_imprimir(valor_atualizar)}'
                    linha_ret = retorno_linha(mensagem, sucesso, linha_ret)
                    return linha_ret

                else:
                    linha_ret = retorno_linha('Não pôde ser alterado', erro, linha_ret)
                    return linha_ret

            else:   # desconto = True
                datas_desconto = pegar_datas()

                dt_desconto = datas_desconto[0]
                dt_futuro = datas_desconto[1]

                payload = json.dumps(
                        {
                            'deal_price'    : float(novo_valor),
                            'start_date'    : dt_desconto,
                            'finish_date'   : dt_futuro,
                            'promotion_type': 'PRICE_DISCOUNT'
                            })

            url = f'{base}/seller-promotions/items/{produto}?app_version=v2'

            headers = {'Authorization': f'Bearer {tv}'}
            resposta = requests.request('POST', url=url, headers=headers, data=payload)

            if resposta.status_code == 201:
                mensagem = f'Desconto criado: De R$ {preco_imprimir(preco_produto)} por R$ {preco_imprimir(novo_valor)}'
                linha_ret = retorno_linha(mensagem, sucesso, linha_ret)
                return linha_ret

            else:
                linha_ret = retorno_linha('Não pôde ser alterado', erro, linha_ret)
                return linha_ret


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
    token_2 = ''

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

        elif escolha == '2' or escolha == 'atualizar planilha':
            if token == '':
                token = configurar_conta()

            gerar_planilha(token)

        elif escolha == '3' or escolha == 'abrir planilha':
            if token == '':
                token = configurar_conta()

            path = f'Arquivos/{(nome_conta(token))}/{id_conta(token)}-planilha-produtos.xlsx'

            if not os.path.exists(path):
                gerar_planilha(token)

            path = os.path.realpath(path)
            df_tamanho = pd.read_excel(path)
            tamanho_planilha = len(df_tamanho['id'])

            filtro_4 = ''
            url_4 = f'{base}/users/{id_conta(token)}/items/search?{filtro_4}&offset={0}'
            resposta_4 = fazer_reqs(url_4, token)
            qtd_de_an_4 = resposta_4['paging']['total']

            if tamanho_planilha != qtd_de_an_4:
                msg_cima('Gerando a planilha...')
                gerar_planilha(token)

            msg('Abrindo o arquivo...')
            os.startfile(path)
            msg('Arquivo aberto')

        elif escolha == '4' or escolha == 'atualizador':
            if token == '':
                token = configurar_conta()

            atualizar_info = True
            while atualizar_info:
                print()
                msg_cima('[Digite VOLTAR para retornar ao menu anterior]')
                msg_cima('O que você deseja atualizar?')
                msg_cima('[1] Estoque | [2] Preço | [3] Desconto | [4] SKU')
                tipo_desejado = get_input()

                atualizador = True
                while atualizador:
                    if tipo_desejado != 'voltar':
                        tipo_escolhas = ['1', '2', '3', '4']
                        if tipo_desejado in tipo_escolhas:
                            if tipo_desejado == '1':
                                tipo_esc = 'estoque'

                            elif tipo_desejado == '2':
                                tipo_esc = 'preço'

                            elif tipo_desejado == '3':
                                tipo_esc = 'desconto'

                            else:
                                tipo_esc = 'sku'

                            if tipo_esc == 'estoque':
                                sku_escolhido = pegar_sku()
                                if sku_escolhido != 'voltar':
                                    print()
                                    valor_alterar = input('Qual o novo estoque?\n> ')

                                    try:
                                        valor_alterar = int(valor_alterar)

                                    except:
                                        print()
                                        msg_alerta('ERRO: Insira apenas números inteiros')
                                        break

                                    msg_cima(f'SOLICITAÇÃO DE ALTERAÇÃO')
                                    print()
                                    msg_dif(
                                            'white', '',
                                            f'SKU: {sku_escolhido} | Estoque: {valor_alterar}')

                                    pegar_produtos(sku_escolhido, valor_alterar, token, tipo_esc, modo_esc)
                                    print()
                                else:
                                    break

                            elif tipo_esc == 'preço':
                                sku_escolhido = pegar_sku()
                                if sku_escolhido != 'voltar':
                                    print()
                                    valor_alterar = input(str('Qual o novo preço?\n> R$ '))
                                    valor_alterar = valor_alterar.replace('.', '')

                                    msg_dif('white', '', f'SOLICITAÇÃO DE ALTERAÇÃO')
                                    msg_dif(
                                            'white', '',
                                            f'SKU: {sku_escolhido} | '
                                            f'Preço: R$ {preco_imprimir(valor_alterar)}')

                                    valor_alterar = valor_alterar.replace(',', '.')

                                    pegar_produtos(sku_escolhido, valor_alterar, token, tipo_esc, modo_esc)
                                    print()
                                else:
                                    break

                            elif tipo_esc == 'desconto':
                                sku_escolhido = pegar_sku()
                                if sku_escolhido != 'voltar':
                                    print()
                                    valor_alterar = input(str('Qual o novo preço com desconto?\n> R$ '))
                                    valor_alterar = valor_alterar.replace('.', '')

                                    msg_dif('white', '', f'SOLICITAÇÃO DE ALTERAÇÃO')

                                    msg_dif(
                                            'white', '',
                                            f'SKU: {sku_escolhido} | Preço com desconto: R$'
                                            f' {preco_imprimir(valor_alterar)}')

                                    valor_alterar = valor_alterar.replace(',', '.')

                                    pegar_produtos(sku_escolhido, valor_alterar, token, tipo_esc, modo_esc)
                                    print()
                                else:
                                    break

                            else:
                                sku_escolhido = pegar_sku()
                                if sku_escolhido != 'voltar':
                                    print()
                                    valor_alterar = input('Qual o novo SKU?\n> ')

                                    msg_cima(f'SOLICITAÇÃO DE ALTERAÇÃO')
                                    print()
                                    msg_dif(
                                            'white', '',
                                            f'SKU antigo: {sku_escolhido} | SKU Novo: {valor_alterar}')

                                    pegar_produtos(sku_escolhido, valor_alterar, token, tipo_esc, modo_esc)
                                    print()

                                else:
                                    break

                        else:
                            msg_alerta('Opção inválida, digite apenas 1, 2, 3 ou 4')
                            break

                    else:
                        break

                break

        elif escolha == '5' or escolha == 'atualizar por planilha':
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

                planilha_est = False
                planilha_prc = False
                planilha_sku = False
                planilha_des = False
                planilha_des_e_est = False

                if df_atualizar.columns[0] == 'SKU':
                    for sku_df in df_atualizar['SKU']:
                        lista_sku.append(sku_df)

                    if df_atualizar.columns[1] == 'Estoque':
                        msg_cima('Modo atualizar estoque por planilha selecionado')
                        tipo_esc_plan = 'estoque'
                        msg_alerta('ATENÇÃO: Produtos que estão oferecendo Full não serão alterados')

                        print('\nMODELO DE PLANILHA')
                        msg_cima('| SKU | Estoque |')
                        planilha_est = True

                        for est_df in df_atualizar['Estoque']:
                            valor_trocar.append(est_df)

                    elif df_atualizar.columns[1] == 'Preço':
                        msg_cima('Modo atualizar preço por planilha selecionado')
                        tipo_esc_plan = 'preço'
                        msg_alerta('ATENÇÃO: Produtos com promoção ativa não serão alterados')

                        print('\nMODELO DE PLANILHA')
                        msg_cima('| SKU | Preço |')
                        planilha_prc = True

                        for preco_df in df_atualizar['Preço']:
                            valor_trocar.append(preco_df)

                    elif df_atualizar.columns[1] == 'Desconto ML' or df_atualizar.columns[1] == 'Desconto SM':
                        planilha_des_e_est = True
                        tipo_esc_plan = 'desconto'
                        msg_cima('Modo atualizar desconto por planilha selecionado')
                        msg_alerta('ATENÇÃO: Produtos com promoção ativa não serão alterados')

                        print('\nMODELO DE PLANILHA')
                        msg_cima('| SKU | Desconto ML | Desconto SM | Estoque |')

                        for preco_df in df_atualizar['Desconto ML']:
                            valor_trocar.append(preco_df)

                        for dsc_df in df_atualizar['Desconto SM']:
                            desconto_sm.append(dsc_df)

                        for est_df in df_atualizar['Estoque']:
                            estoque_mlb.append(est_df)

                    elif df_atualizar.columns[1] == 'SKU Novo':
                        msg_cima('Modo atualizar SKUs por planilha selecionado')
                        tipo_esc_plan = 'sku'
                        msg_alerta('ATENÇÃO: A troca de SKUs pode levar um tempo para ser refletida no Mercado Livre')

                        print('\nMODELO DE PLANILHA')
                        msg_cima('| SKU | SKU Novo |')
                        planilha_sku = True

                        for sku_df in df_atualizar['SKU Novo']:
                            valor_trocar.append(sku_df)

                    else:
                        msg_alerta('A planilha não segue um padrão para que seja atualizado')
                        continue

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

                        if planilha_des_e_est:
                            valor_desconto = desconto_sm[inx_sku]
                            est_mlb = estoque_mlb[inx_sku]
                            est_mlb = int(est_mlb)

                        else:
                            valor_desconto = ''
                            est_mlb = ''

                        if planilha_est:
                            valor_mlb = int(valor_mlb)

                        url_df = f'{base}/users/{id_conta(token)}/items/search?seller_sku={sku_mlb}&offset={0}'

                        resposta_df = fazer_reqs(url_df, token)
                        qtd_de_an = resposta_df['paging']['total']
                        print()

                        if qtd_de_an > 0:
                            base_imp = f'SKU: {sku_mlb} | {qtd_de_an} Anúncio'

                            valor_imp_novo = str(valor_mlb)

                            if planilha_prc:
                                complemento = f'Preço: R$ {preco_imprimir(valor_imp_novo)}'

                            elif planilha_des_e_est:
                                valor_desconto_imp = str(valor_desconto)
                                valor_imp_novo.replace('.', ',')

                                complemento = (f'Estoque: {est_mlb} | '
                                               f'Preço Mercado Livre R$ {preco_imprimir(valor_imp_novo)} | '
                                               f'Preço Supermercado R$ {preco_imprimir(valor_desconto_imp)}')

                            elif planilha_des:
                                valor_desconto_imp = str(valor_desconto)
                                valor_imp_novo.replace('.', ',')

                                complemento = (f'Estoque: {est_mlb} | '
                                               f'Preço Mercado Livre R$ {preco_imprimir(valor_imp_novo)} | '
                                               f'Preço Supermercado R$ {preco_imprimir(valor_desconto_imp)}')

                            elif planilha_sku:
                                complemento = f'SKU: {valor_mlb}'

                            else:
                                complemento = f'Estoque: {valor_mlb}'

                            if qtd_de_an == 1:
                                msg_dif('white', '', f'{base_imp} | {complemento}')

                            else:
                                msg_dif('white', '', f'{base_imp}s | {complemento}')

                            sku_disp.append(sku_mlb)

                            if planilha_des_e_est:
                                valor_mlb = [valor_mlb, valor_desconto]
                                registro_est = pegar_produtos(sku_mlb, est_mlb, token, 'estoque', modo_esc)
                                registros.append(registro_est)

                            if planilha_des:
                                valor_mlb = [valor_mlb, valor_desconto]

                            registro_sku = pegar_produtos(sku_mlb, valor_mlb, token, tipo_esc_plan, modo_esc)
                            registros.append(registro_sku)

                        else:
                            registro_nenhum_an = f'SKU: {sku_mlb} | Nenhum anúncio encontrado'
                            msg_alerta(registro_nenhum_an)
                            sku_nao_disp.append(sku_mlb)

                    msg(f'\nSKUs encontrados: {sku_disp}')
                    msg(f'\nSKUs não encontrados: {sku_nao_disp}\n')

                    with open('registro.txt', 'w') as reg:
                        for item_reg in registros:
                            for item_reg_un in item_reg:
                                nova_linha = f'{item_reg_un}\n'
                                reg.write(nova_linha)

                    nova_lista = []

                    for registro in registros:
                        for registro_in in registro:
                            nova_lista.append(registro_in)

                    nova_planilha = pd.DataFrame(
                            nova_lista,
                            columns=['Vendedor', 'Status', 'SKU', 'Código', 'Envio', 'Frete',
                                     'Canal', 'Título', 'Descrição'])

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

        elif escolha == '6':
            if token == '':
                token = configurar_conta()

            msg_cima('Qual o código da categoria? Exemplo: MLB432825')

            categoria = input(str('> '))

            url_cat = f'{base}/highlights/MLB/category/{categoria}'
            retorno_cat = fazer_reqs(url_cat, token)

            retorno_cat = retorno_cat['content']

            lista_categoria = []
            linha_ret_cat = []

            print('Carregando, por favor aguarde...')

            for inx_cat, item in enumerate(retorno_cat):
                lista_categoria.append(item)

                produto_cat = item['id']

                tipo_produto = item['type']
                if tipo_produto == 'PRODUCT':
                    url_cat_2 = f'{base}/products/{produto_cat}'

                else:
                    url_cat_2 = f'{base}/items/{produto_cat}'

                prd_cat = fazer_reqs(url_cat_2, token)

                if tipo_produto == 'PRODUCT':
                    id_produto_cat = prd_cat['buy_box_winner']['item_id']
                    title_produto_cat = prd_cat['name']
                    seller_id_cat = prd_cat['buy_box_winner']['seller_id']

                else:
                    id_produto_cat = prd_cat['id']
                    title_produto_cat = prd_cat['title']
                    seller_id_cat = prd_cat['seller_id']

                price_cat = prd_cat['buy_box_winner']['price']
                envio_cat = prd_cat['buy_box_winner']['shipping']['logistic_type']

                if envio_cat == 'cross_docking':
                    prd_cat['buy_box_winner']['shipping'] = 'Normal'

                elif envio_cat == 'fulfillment':
                    prd_cat['buy_box_winner']['shipping'] = 'Full'

                elif envio_cat == 'not_specified':
                    prd_cat['buy_box_winner']['shipping'] = 'Não especificado'

                else:
                    prd_cat['buy_box_winner']['shipping'] = 'Não especificado'

                seller_address = prd_cat['buy_box_winner']['seller_address']

                cidade = seller_address['city']['name']
                estado = seller_address['state']['name']

                endereco_seller = f'{estado}, {cidade}'

                headers_cat = {'Authorization': f'Bearer {token}'}
                resposta_cat = requests.get(f'{base}/users/{seller_id_cat}', headers=headers_cat)
                resposta_cat = resposta_cat.json()
                conta_cat = resposta_cat['nickname']

                seller_id_cat = conta_cat

                linha_ret_cat.append([id_produto_cat, title_produto_cat, seller_id_cat, price_cat, endereco_seller])

            df_cat = pd.DataFrame(linha_ret_cat, columns=['ID MLB', 'TÍTULO', 'LOJA', 'PREÇO', 'ENDEREÇO'])

            df_cat.to_excel(f'Categoria-{categoria}.xlsx', index=True)
            print(f'Arquivo gerado Categoria-{categoria}.xlsx')

        elif escolha == '7':
            if token == '':
                print('Configure o primeiro token')
                token = configurar_conta()

            print(f'Primeiro Token configurado: {token}')

            if token_2 == '':
                print('Configure o segundo token')
                token_2 = configurar_conta()

            print(f'Segundo Token configurado: {token_2}')

            planilha_atualizar = dlg.askopenfilename(filetypes=[('Arquivos excel', '.xlsx')])

            msg(f'Caminho do arquivo: {planilha_atualizar}')
            df_atualizar = pd.read_excel(planilha_atualizar)

            lista_id = []

            if df_atualizar.columns[0] == 'id':
                for id_df in df_atualizar['id']:
                    lista_id.append(id_df)

            lista_resultado = []
            for id_mlb in lista_id:
                retorno_clone = fazer_post(id_mlb, token, token_2)
                lista_resultado.append(retorno_clone)

            nova_lista = []

            for item in lista_resultado:
                nova_lista.append(item)

            nova_planilha = pd.DataFrame(nova_lista, columns=['Status', 'Código', 'JSON'])

            nova_planilha.to_excel('clonados.xlsx', index=False)
            print(f'Arquivo gerado clonados.xlsx')

        else:
            print()
            msg_alerta('Opção inválida | Escolha uma das opções')

            if token != '':
                msg_destaque(f'Conta conectada: {nome_conta(token)}')

        msg(mensagem_base)


if __name__ == '__main__':
    main()
