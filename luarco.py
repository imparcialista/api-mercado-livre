import json
import os
import time
import pandas as pd
from tkinter import filedialog as dlg
import requests

from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


os.system('color')
apenas_itens_ativos = False
base = 'https://api.mercadolibre.com'

mensagem_base = (
    '\n[*] Escolha uma opção'
    '\n[1] Trocar de conta'
    '\n[2] update_product planilha'
    '\n[3] Abrir a planilha'
    '\n[4] update_product por SKU'
    '\n[5] update_product por planilha'
    '\n[6] Mais vendidos por categoria'
    '\n[7] Exportar produtos com promoções')


def catch_dates():
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


# Supondo que essas funções estejam definidas em outro lugar
from mensagens import msg_alerta, msg_aviso, msg_cima, msg_destaque, msg, msg_dif


def make_request(url, tv):
    headers = {'Authorization': f'Bearer {tv}'}

    try:
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status()  # Levanta uma exceção se o status não for 200

        # Tratamento de status codes específicos
        if resposta.status_code == 200:
            return resposta.json()
        elif resposta.status_code == 401:
            msg_alerta('Acesso não autorizado. Verifique o Access Token.')
            tv = configure_account()  # Solicita um novo access_token
            headers['Authorization'] = f'Bearer {tv}'
            return make_request(url, tv)  # Tenta novamente com o novo token
        elif resposta.status_code == 404:
            msg_alerta('Recurso não encontrado.')
            quit()
        elif resposta.status_code == 500:
            msg_alerta('Erro interno do servidor.')
            quit()
        else:
            msg_aviso(f'Status code inesperado: {resposta.status_code}')
            quit()

    except requests.exceptions.RequestException as e:
        msg_alerta(f'Falha na requisição: {e}')
        quit()


def configure_account():
    conta_configurada = False
    while not conta_configurada:
        msg_cima('Insira o Access Token')
        tv = input(str('> '))

        headers = {'Authorization': f'Bearer {tv}'}
        resposta = requests.get(f'{base}/users/me', headers=headers)

        if resposta.status_code == 200:
            os.system('CLS')
            msg_destaque('Programa feito por @imparcialista  v1.2.5.1')
            msg(f'Conta conectada: {resposta.json()["nickname"]}')
            return tv
        else:
            msg_aviso('Access Token inválido ou expirado')


def load_account_data(tv):
    url = f'{base}/users/me'
    resposta = make_request(url, tv)
    return {
        'id'      : resposta['id'],
        'nickname': resposta['nickname']
        }


def get_scroll_id(tv, dados_conta):
    url = f'{base}/users/{dados_conta["id"]}/items/search?search_type=scan&limit=100'
    resposta = make_request(url, tv)
    return resposta


def next_page(scroll, tv, dados_conta):
    url = f'{base}/users/{dados_conta["id"]}/items/search?search_type=scan&scroll_id={scroll}&limit=100'
    resposta = make_request(url, tv)
    return resposta


def get_all_ids(tv):
    lista = []
    inicio_timer = time.time()
    paginas = 0

    filtro = 'include_filters=true&status=active' if apenas_itens_ativos else ''

    dados_conta = load_account_data(tv)

    url = f'{base}/users/{dados_conta["id"]}/items/search?{filtro}&offset={0}'
    resposta = make_request(url, tv)

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
        primeiro_scroll = get_scroll_id(tv, dados_conta)
        msg_cima('Coletando IDs, por favor aguarde...')

        lista_scroll.append(primeiro_scroll['scroll_id'])
        for produto in primeiro_scroll['results']:
            lista.append(produto)


        def gerar_scroll(scroll_anterior):
            scroll = next_page(scroll_anterior, tv, dados_conta)

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
            url = f'{base}/users/{dados_conta["id"]}/items/search?{filtro}&offset={pagina * 50}'

            resposta = make_request(url, tv)

            for produto in resposta['results']:
                lista.append(produto)

    if not os.path.exists(f'Arquivos/{dados_conta["nickname"]}'):
        os.makedirs(f'Arquivos/{dados_conta["nickname"]}')
        msg_cima(f'Pasta {dados_conta["nickname"]} criada')

    arquivo_json = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-ids_mlb.json'

    if os.path.exists(arquivo_json):
        os.remove(arquivo_json)

    with open(arquivo_json, 'w') as outfile:
        json.dump(lista, outfile)

    fim_timer = time.time()
    msg_cima(f'{dados_conta["nickname"]}: Todos os IDS foram coletados ')
    msg_cima(f'Tempo de execução: {(int(fim_timer - inicio_timer)) + 1} segundos')

    return lista


def export_to_spreadsheet(lista_json: list, colunas_drop: list, dados_conta):
    arquivo_json = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-retorno-produtos.json'

    if os.path.exists(arquivo_json):
        os.remove(arquivo_json)

    with open(arquivo_json, 'w') as outfile:
        json.dump(lista_json, outfile)

    df = pd.read_json(arquivo_json)
    df = df.drop(colunas_drop, axis=1, errors='ignore')
    planilha = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-planilha-produtos.xlsx'

    if os.path.exists(planilha):
        os.remove(planilha)

    df['date_created'] = pd.to_datetime(df['date_created'], format='%d/%m/%Y %H:%M:%S')
    df['last_updated'] = pd.to_datetime(df['last_updated'], format='%d/%m/%Y %H:%M:%S')

    # df = df.sort_values(by='last_updated', ascending=False)
    df = df.sort_values(by='status')
    df.to_excel(planilha, index=False)

    msg(f'Planilha gerada')

    # Segunda planilha

    time.sleep(1)

    # Ler a planilha
    scn_df = pd.read_excel(planilha)


    def modify_tags(row):
        if 'supermarket_eligible' in str(row['tags']):
            return 'Supermercado'
        else:
            return row['shipping']


    # Aplicar a função à coluna 'tags'
    scn_df['tags'] = scn_df.apply(modify_tags, axis=1)

    # Selecionar as colunas desejadas
    columns_to_keep = [
        'id', 'title', 'price', 'original_price',
        'available_quantity', 'attributes', 'status', 'tags'
        ]
    df_selected = scn_df[columns_to_keep]

    # Caminho para o arquivo .xlsx de saída
    segunda_planilha = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-segunda-planilha.xlsx'

    # Exportar a nova planilha
    df_selected.to_excel(segunda_planilha, index=False)

    print(f'Planilha para uso do App: {segunda_planilha}')


# Função para obter informações de promoção de um item
def get_promotions(item_id, tv):
    url = f"https://api.mercadolibre.com/seller-promotions/items/{item_id}?app_version=v2"
    headers = {
        "Authorization": f"Bearer {tv}"
        }
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get('Retry-After', 1))
            print(f"Limite de taxa excedido. Esperando {retry_after} segundos.")
            time.sleep(1)
            # time.sleep(retry_after)
        else:
            if response.status_code == 200:
                return item_id, response.json()
            else:
                return item_id, None


# Função para processar as promoções de um item
def process_promotions(item_id, promotions, promotion_info):
    if promotions:
        for promotion in promotions:
            if "status" in promotion:
                if promotion["status"] == "started":
                    if "offers" in promotion:
                        for offer in promotion["offers"]:
                            if offer["status"] == "candidate":
                                promotion_info[item_id] = {
                                    "finish_date": offer["end_date"],
                                    "final_price": offer["new_price"]
                                    }
                    elif "price" in promotion:
                        promotion_info[item_id] = {
                            "finish_date": promotion["finish_date"],
                            "final_price": promotion["price"]
                            }
                elif promotion["status"] == "candidate":
                    promotion_info[item_id] = {
                        "status" : "candidate",
                        "message": "Produto elegível para promoção, mas não há desconto ativo no momento."
                        }


# Função para exportar os resultados para uma planilha Excel
def export_promotions_to_excel(promotion_info, filename):
    data = []
    for item_id, info in promotion_info.items():
        if "finish_date" in info:
            data.append(
                    {
                        "Item ID"    : item_id,
                        "Finish Date": info["finish_date"],
                        "Final Price": info["final_price"],
                        "Status"     : "started",
                        "Message"    : f"Promoção ativa com desconto de PRICE_DISCOUNT"
                        }
                    )
        elif "status" in info and info["status"] == "candidate":
            data.append(
                    {
                        "Item ID"    : item_id,
                        "Finish Date": "",
                        "Final Price": "",
                        "Status"     : info["status"],
                        "Message"    : info["message"]
                        }
                    )
        else:
            data.append(
                    {
                        "Item ID"    : item_id,
                        "Finish Date": "",
                        "Final Price": "",
                        "Status"     : "",
                        "Message"    : "Nenhuma promoção encontrada"
                        }
                    )

    df = pd.DataFrame(data)
    df = df.sort_values(by='Status', ascending=False)

    df.to_excel(filename, index=False)
    print(f"Resultados exportados para {filename}")


def make_promotions_excel(tv, dados_conta):
    # Carregar IDs dos itens do arquivo JSON

    ids_mlb = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-ids_mlb.json'

    if not os.path.exists(ids_mlb):
        get_all_ids(tv)

    json_file = ids_mlb

    try:
        with open(json_file, 'r') as file:
            item_ids = json.load(file)

    except FileNotFoundError:
        print(f"Arquivo JSON não encontrado: {json_file}")
        exit(1)

    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo JSON: {json_file}")
        exit(1)

    # Dicionário para armazenar os resultados
    promotion_info = {}

    # Definir o tamanho do lote com base no tamanho da lista de IDs
    total_items = len(item_ids)
    # batch_size = min(100, total_items)  # Ajuste este valor conforme necessário
    batch_size = total_items

    # Dividir os IDs dos itens em lotes
    batches = [item_ids[i:i + batch_size] for i in range(0, len(item_ids), batch_size)]

    # Iniciar a medição do tempo de execução
    start_time = time.time()

    # Processar cada lote em paralelo
    for batch in batches:
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(get_promotions, item_id, tv) for item_id in batch]
            for future in as_completed(futures):
                item_id, promotions = future.result()
                process_promotions(item_id, promotions, promotion_info)

    # Finalizar a medição do tempo de execução
    end_time = time.time()
    execution_time = end_time - start_time

    # Exibir o tempo de execução
    print(f"Tempo de execução: {execution_time:.2f} segundos")

    if not os.path.exists(f'Arquivos/{dados_conta["nickname"]}'):
        os.makedirs(f'Arquivos/{dados_conta["nickname"]}')
        msg_cima(f'Pasta {dados_conta["nickname"]} criada')

    # Exportar os resultados para uma planilha Excel
    filename = f"Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-promotion_results.xlsx"
    export_promotions_to_excel(promotion_info, filename)


def make_excel(tv, dados_conta):
    ids_mlb = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-ids_mlb.json'
    lista_retorno = []
    lista_geral = []
    gap_vinte = 0
    paginas = 0

    if not os.path.exists(ids_mlb):
        get_all_ids(tv)

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
        retorno = make_request(url, tv)

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

    export_to_spreadsheet(lista_retorno, drops, dados_conta)


def price_print(preco):
    try:
        preco = float(preco)
    except:
        pass

    preco = str(preco)
    preco = preco.replace('.', ',')

    return preco


def update_product(produto, valor_update_product, tv, tipo, modo, dados_conta):
    url = f'{base}/items/{produto}'
    info_produto = make_request(url, tv)
    vendedor = dados_conta['nickname']
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


    def line_return(msg_ret, cor, lista_linha):
        msg_imprimir = f'{msg_base} | {msg_ret} | {tit_produto}'
        msg_dif(cor, '', msg_imprimir)
        lista_linha.append(msg_ret)
        return lista_linha


    if tipo == 'estoque':
        est_produto = info_produto['available_quantity']

        mini_espera = False
        if valor_update_product <= 0:
            valor_update_product = 0
            if est_produto > 0:
                mini_espera = True
        else:
            if est_produto <= 0:
                mini_espera = True

        # Produtos do full não podem ser alterados
        if info_produto['shipping'] == 'Full':
            linha_ret = line_return('Estoque no Full', aviso, linha_ret)
            return linha_ret

        # Não vamos trocar um valor pelo mesmo valor, nós apenas deixamos como está
        if valor_update_product == est_produto:
            linha_ret = line_return('Estoque correto', normal, linha_ret)
            return linha_ret

        # Podemos ter produtos com estoque, mas que estejam inativos, nesse caso, vamos tentar update_product para ativo
        if valor_update_product > 0:
            payload = json.dumps(
                    {
                        'available_quantity': valor_update_product, 'status': 'active',
                        "channels"          : [
                            "marketplace",
                            "mshops"
                            ]
                        }
                    )
        else:
            payload = json.dumps({'available_quantity': valor_update_product})

        headers = {'Authorization': f'Bearer {tv}'}
        resposta = requests.put(url=url, headers=headers, data=payload)

        if resposta.status_code == 200:
            mensagem = f'Estoque alterado de {est_produto} para {valor_update_product}'
            if mini_espera:
                time.sleep(1)

            linha_ret = line_return(mensagem, sucesso, linha_ret)
            return linha_ret

        else:
            linha_ret = line_return('Não pôde ser alterado', erro, linha_ret)
            return linha_ret

    elif tipo == 'sku':
        payload = json.dumps({'attributes': [{'id': 'SELLER_SKU', 'value_name': f'{valor_update_product}'}]})

        headers = {'Authorization': f'Bearer {tv}'}
        resposta = requests.put(url=url, headers=headers, data=payload)

        if resposta.status_code == 200:
            linha_ret = line_return(f'SKU novo: {valor_update_product}', sucesso, linha_ret)
            return linha_ret

        else:
            linha_ret = line_return('Não pôde ser alterado', erro, linha_ret)
            return linha_ret
    else:
        supermercado = False
        if type(valor_update_product) is list:
            valor_mercado_livre = valor_update_product[0]
            valor_supermercado = valor_update_product[1]

            if 'supermarket_eligible' in info_produto['tags']:
                novo_valor = valor_supermercado
                supermercado = True
            else:
                supermercado = False
                novo_valor = valor_mercado_livre
        else:
            novo_valor = valor_update_product

        preco_produto = info_produto['price']
        preco_original_produto = info_produto['original_price']
        # preco_original_produto = str(preco_original_produto)

        # print(f'preço_produto: {preco_produto} | preco_original_produto: {preco_original_produto}')

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
                                'Produto com frete grátis abaixo de 79, por favor altere.\nAperte ENTER para continuar'
                                )

                    if preco_comparar >= 79:
                        if novo_valor < 79:
                            mensagem = f'Não alterar: Desconto abaixo do valor de frete grátis'
                            linha_ret = line_return(mensagem, normal, linha_ret)
                            return linha_ret

                mensagem = (f'Pode ser vendido por: R$ {price_print(novo_valor)}. Desconto atual: R$ '
                            f'{price_print(preco_produto)} | {sku_produto} | {produto} | {tit_produto}')
                msg(mensagem)

                if desconto:
                    if modo == 'manual':
                        deseja_update_product = input(str('Envie 1 se deseja alterar\n> '))
                    else:
                        if modo == 'auto_modificar':
                            deseja_update_product = '1'
                        else:
                            deseja_update_product = '2'

                    if deseja_update_product == '1':
                        url = f'{base}/seller-promotions/items/{produto}?promotion_type=PRICE_DISCOUNT&app_version=v2'
                        headers = {'Authorization': f'Bearer {tv}'}
                        requests.request('DELETE', url=url, headers=headers)
                        msg_dif('yellow', '', 'Recriando promoção, por favor aguarde...')
                        time.sleep(15)

                        datas_desconto = catch_dates()

                        dt_desconto = datas_desconto[0]
                        dt_futuro = datas_desconto[1]

                        payload = json.dumps(
                                {
                                    'deal_price'    : float(novo_valor),
                                    'start_date'    : dt_desconto,
                                    'finish_date'   : dt_futuro,
                                    'promotion_type': 'PRICE_DISCOUNT'
                                    }
                                )

                        url = f'{base}/seller-promotions/items/{produto}?app_version=v2'

                        headers = {'Authorization': f'Bearer {tv}'}
                        resposta = requests.request('POST', url=url, headers=headers, data=payload)

                        if resposta.status_code == 201:
                            mensagem = (f'Desconto recriado: De R$ {price_print(preco_produto)} por R$ '
                                        f'{price_print(novo_valor)}')
                            linha_ret = line_return(mensagem, sucesso, linha_ret)
                            return linha_ret

                        else:
                            linha_ret = line_return('Não pôde ser alterado', erro, linha_ret)
                            return linha_ret

                else:
                    linha_ret = line_return(mensagem, normal, linha_ret)
                    return linha_ret

            else:
                mensagem = (f'Promoção ativa: De R$ {price_print(preco_original_produto)} '
                            f'por R$ {price_print(preco_produto)}')
                linha_ret = line_return(mensagem, normal, linha_ret)
                return linha_ret

        elif preco_produto == valor_update_product:
            linha_ret = line_return('Preço correto', normal, linha_ret)
            return linha_ret

        else:
            if not supermercado:
                if preco_produto < 79 and frete == 'Grátis':
                    input('Produto com frete grátis abaixo de 79, por favor altere.\nAperte ENTER para continuar')

                if preco_produto >= 79:
                    if novo_valor < 79:
                        mensagem = f'Não alterar: Desconto abaixo do valor de frete grátis'
                        linha_ret = line_return(mensagem, normal, linha_ret)
                        return linha_ret

            if preco:
                payload = json.dumps({'price': valor_update_product})

                headers = {'Authorization': f'Bearer {tv}'}
                resposta = requests.put(url=url, headers=headers, data=payload)

                if resposta.status_code == 200:
                    mensagem = (f'Preço alterado de R$ {price_print(preco_produto)} '
                                f'para R$ {price_print(valor_update_product)}')
                    linha_ret = line_return(mensagem, sucesso, linha_ret)
                    return linha_ret

                else:
                    linha_ret = line_return('Não pôde ser alterado', erro, linha_ret)
                    return linha_ret

            else:  # desconto = True
                datas_desconto = catch_dates()

                dt_desconto = datas_desconto[0]
                dt_futuro = datas_desconto[1]

                payload = json.dumps(
                        {
                            'deal_price'    : float(novo_valor),
                            'start_date'    : dt_desconto,
                            'finish_date'   : dt_futuro,
                            'promotion_type': 'PRICE_DISCOUNT'
                            }
                        )

            url = f'{base}/seller-promotions/items/{produto}?app_version=v2'

            headers = {'Authorization': f'Bearer {tv}'}
            resposta = requests.request('POST', url=url, headers=headers, data=payload)

            if resposta.status_code == 201:
                mensagem = f'Desconto criado: De R$ {price_print(preco_produto)} por R$ {price_print(novo_valor)}'
                linha_ret = line_return(mensagem, sucesso, linha_ret)
                return linha_ret

            else:
                linha_ret = line_return('Não pôde ser alterado', erro, linha_ret)
                return linha_ret


def pegar_produtos(sku, valor_update_product, tv, tipo, modo, dados_conta):
    lista_feitos = []
    paginas = 0
    url = f'{base}/users/{dados_conta["id"]}/items/search?seller_sku={sku}&offset={paginas}'

    resposta = make_request(url, tv)
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
                feito = update_product(produto, valor_update_product, tv, tipo, modo, dados_conta)
                lista_feitos.append(feito)

        else:

            while quantidade_de_an > 0:
                quantidade_de_an -= 50
                paginas += 1

            for pagina in range(paginas):
                url = f'{base}/users/{dados_conta["id"]}/items/search?seller_sku={sku}&offset={(pagina * 50)}'

                resposta = make_request(url, tv)

                for produto in resposta['results']:
                    feito = update_product(produto, valor_update_product, tv, tipo, modo, dados_conta)
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
    msg_cima('Qual SKU você deseja update_product?')
    sku_escolhido_input = input('> ')
    sku_escolhido_input = sku_escolhido_input.strip()
    return sku_escolhido_input


def main():
    os.system('CLS')
    sair = False
    token = configure_account()
    dados_conta = load_account_data(token)

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
            token = ''
            main()

        elif escolha == '2' or escolha == 'update_product planilha':
            if token == '':
                token = configure_account()

            make_excel(token, dados_conta)

        elif escolha == '3' or escolha == 'abrir planilha':
            if token == '':
                token = configure_account()

            path = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-planilha-produtos.xlsx'

            if not os.path.exists(path):
                make_excel(token, dados_conta)

            path = os.path.realpath(path)
            df_tamanho = pd.read_excel(path)
            tamanho_planilha = len(df_tamanho['id'])

            filtro_4 = ''
            url_4 = f'{base}/users/{dados_conta["id"]}/items/search?{filtro_4}&offset={0}'
            resposta_4 = make_request(url_4, token)
            qtd_de_an_4 = resposta_4['paging']['total']

            if tamanho_planilha != qtd_de_an_4:
                msg_cima('Gerando a planilha...')
                make_excel(token, dados_conta)

            msg('Abrindo o arquivo...')
            os.startfile(path)
            msg('Arquivo aberto')

        elif escolha == '4' or escolha == 'atualizador':
            if token == '':
                token = configure_account()

            update_product_info = True
            while update_product_info:
                print()
                msg_cima('[Digite VOLTAR para retornar ao menu anterior]')
                msg_cima('O que você deseja update_product?')
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
                                            f'SKU: {sku_escolhido} | Estoque: {valor_alterar}'
                                            )

                                    pegar_produtos(sku_escolhido, valor_alterar, token, tipo_esc, modo_esc, dados_conta)
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
                                            f'Preço: R$ {price_print(valor_alterar)}'
                                            )

                                    valor_alterar = valor_alterar.replace(',', '.')

                                    pegar_produtos(sku_escolhido, valor_alterar, token, tipo_esc, modo_esc, dados_conta)
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
                                            f' {price_print(valor_alterar)}'
                                            )

                                    valor_alterar = valor_alterar.replace(',', '.')

                                    pegar_produtos(sku_escolhido, valor_alterar, token, tipo_esc, modo_esc, dados_conta)
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
                                            f'SKU antigo: {sku_escolhido} | SKU Novo: {valor_alterar}'
                                            )

                                    pegar_produtos(sku_escolhido, valor_alterar, token, tipo_esc, modo_esc, dados_conta)
                                    print()

                                else:
                                    break

                        else:
                            msg_alerta('Opção inválida, digite apenas 1, 2, 3 ou 4')
                            break

                    else:
                        break

                break

        elif escolha == '5' or escolha == 'update_product por planilha':
            if token == '':
                token = configure_account()

            planilha_update_product = dlg.askopenfilename(filetypes=[('Arquivos excel', '.xlsx')])

            if planilha_update_product != '':
                print()
                msg(f'Caminho do arquivo: {planilha_update_product}')
                df_update_product = pd.read_excel(planilha_update_product)

                lista_sku = []
                valor_trocar = []
                desconto_sm = []
                estoque_mlb = []

                planilha_est = False
                planilha_prc = False
                planilha_sku = False
                planilha_des = False
                planilha_des_e_est = False

                if df_update_product.columns[0] == 'SKU':
                    for sku_df in df_update_product['SKU']:
                        lista_sku.append(sku_df)

                    if df_update_product.columns[1] == 'Estoque':
                        msg_cima('Modo update_product estoque por planilha selecionado')
                        tipo_esc_plan = 'estoque'
                        msg_alerta('ATENÇÃO: Produtos que estão oferecendo Full não serão alterados')

                        print('\nMODELO DE PLANILHA')
                        msg_cima('| SKU | Estoque |')
                        planilha_est = True

                        for est_df in df_update_product['Estoque']:
                            valor_trocar.append(est_df)

                    elif df_update_product.columns[1] == 'Preço':
                        msg_cima('Modo update_product preço por planilha selecionado')
                        tipo_esc_plan = 'preço'
                        msg_alerta('ATENÇÃO: Produtos com promoção ativa não serão alterados')

                        print('\nMODELO DE PLANILHA')
                        msg_cima('| SKU | Preço |')
                        planilha_prc = True

                        for preco_df in df_update_product['Preço']:
                            valor_trocar.append(preco_df)

                    elif df_update_product.columns[1] == 'Desconto ML' or df_update_product.columns[1] == 'Desconto SM':
                        planilha_des_e_est = True
                        tipo_esc_plan = 'desconto'
                        msg_cima('Modo update_product desconto por planilha selecionado')
                        msg_alerta('ATENÇÃO: Produtos com promoção ativa não serão alterados')

                        print('\nMODELO DE PLANILHA')
                        msg_cima('| SKU | Desconto ML | Desconto SM | Estoque |')

                        for preco_df in df_update_product['Desconto ML']:
                            valor_trocar.append(preco_df)

                        for dsc_df in df_update_product['Desconto SM']:
                            desconto_sm.append(dsc_df)

                        for est_df in df_update_product['Estoque']:
                            estoque_mlb.append(est_df)

                    elif df_update_product.columns[1] == 'SKU Novo':
                        msg_cima('Modo update_product SKUs por planilha selecionado')
                        tipo_esc_plan = 'sku'
                        msg_alerta('ATENÇÃO: A troca de SKUs pode levar um tempo para ser refletida no Mercado Livre')

                        print('\nMODELO DE PLANILHA')
                        msg_cima('| SKU | SKU Novo |')
                        planilha_sku = True

                        for sku_df in df_update_product['SKU Novo']:
                            valor_trocar.append(sku_df)

                    else:
                        msg_alerta('A planilha não segue um padrão para que seja atualizado')
                        continue

                else:
                    msg_alerta('A planilha não segue um padrão para que seja atualizado')
                    continue

                msg(f'\n{len(df_update_product["SKU"])} SKUs para update_product\nDeseja continuar?\n[1] Sim | [2] Não')
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

                        url_df = f'{base}/users/{dados_conta["id"]}/items/search?seller_sku={sku_mlb}&offset={0}'

                        resposta_df = make_request(url_df, token)
                        qtd_de_an = resposta_df['paging']['total']
                        print()

                        if qtd_de_an > 0:
                            base_imp = f'SKU: {sku_mlb} | {qtd_de_an} Anúncio'

                            valor_imp_novo = str(valor_mlb)

                            if planilha_prc:
                                complemento = f'Preço: R$ {price_print(valor_imp_novo)}'

                            elif planilha_des_e_est:
                                valor_desconto_imp = str(valor_desconto)
                                valor_imp_novo.replace('.', ',')

                                complemento = (f'Estoque: {est_mlb} | '
                                               f'Preço Mercado Livre R$ {price_print(valor_imp_novo)} | '
                                               f'Preço Supermercado R$ {price_print(valor_desconto_imp)}')

                            elif planilha_des:
                                valor_desconto_imp = str(valor_desconto)
                                valor_imp_novo.replace('.', ',')

                                complemento = (f'Estoque: {est_mlb} | '
                                               f'Preço Mercado Livre R$ {price_print(valor_imp_novo)} | '
                                               f'Preço Supermercado R$ {price_print(valor_desconto_imp)}')

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
                                registro_est = pegar_produtos(sku_mlb, est_mlb, token, 'estoque', modo_esc, dados_conta)
                                registros.append(registro_est)

                            if planilha_des:
                                valor_mlb = [valor_mlb, valor_desconto]

                            registro_sku = pegar_produtos(
                                    sku_mlb, valor_mlb, token, tipo_esc_plan, modo_esc, dados_conta
                                    )
                            registros.append(registro_sku)

                        else:
                            registro_nenhum_an = f'SKU: {sku_mlb} | Nenhum anúncio encontrado'
                            msg_alerta(registro_nenhum_an)
                            sku_nao_disp.append(sku_mlb)

                    msg(f'\nSKUs encontrados: {sku_disp}')
                    msg(f'\nSKUs não encontrados: {sku_nao_disp}\n')

                    with open(f'registro-{dados_conta["nickname"]}.txt', 'w') as reg:
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
                                     'Canal', 'Título', 'Descrição']
                            )

                    data_registro = catch_dates()
                    data_registro = data_registro[0]
                    data_registro = data_registro[:10]

                    nova_planilha.to_excel(f'{data_registro}-{dados_conta["nickname"]}.xlsx', index=False)
                    print(f'Arquivo gerado Registros.xlsx')

                elif continuar == '2':
                    msg_alerta('Você escolheu não continuar')

                else:
                    msg_alerta('Opção inválida')

            else:
                msg_alerta('Você não selecionou nenhum arquivo')

        elif escolha == '6':
            if token == '':
                token = configure_account()

            msg_cima('Qual o código da categoria? Exemplo: MLB432825')

            categoria = input(str('> '))

            url_cat = f'{base}/highlights/MLB/category/{categoria}'
            retorno_cat = make_request(url_cat, token)

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

                prd_cat = make_request(url_cat_2, token)

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
                token = configure_account()

            make_promotions_excel(token, dados_conta)


        else:
            print()
            msg_alerta('Opção inválida | Escolha uma das opções')

            if token != '':
                msg_destaque(f'Conta conectada: {dados_conta["nickname"]}')

        msg(mensagem_base)


if __name__ == '__main__':
    main()
