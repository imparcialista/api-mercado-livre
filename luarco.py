import json
import os
import time
import pandas as pd
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed


os.system('color')
apenas_itens_ativos = False
base = 'https://api.mercadolibre.com'

mensagem_base = (
    '\n[*] Escolha uma opção'
    '\n[1] Trocar de conta'
    '\n[2] Atualizar planilha'
    '\n[3] Abrir a planilha'
    '\n[4] Exportar promoções (Desconto tradicional)')


def make_request(url, tv):
    headers = {'Authorization': f'Bearer {tv}'}

    try:
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status()

        if resposta.status_code == 200:
            return resposta.json()
        elif resposta.status_code == 401:
            print('Acesso não autorizado. Verifique o Access Token.')
            tv = configure_account()
            headers['Authorization'] = f'Bearer {tv}'
            return make_request(url, tv)
        elif resposta.status_code == 404:
            print('Recurso não encontrado.')
            quit()
        elif resposta.status_code == 500:
            print('Erro interno do servidor.')
            quit()
        else:
            print(f'Status code inesperado: {resposta.status_code}')
            quit()

    except requests.exceptions.RequestException as e:
        print(f'Falha na requisição: {e}')
        quit()


def configure_account():
    conta_configurada = False
    while not conta_configurada:
        print('Insira o Access Token')
        tv = input(str('> '))

        headers = {'Authorization': f'Bearer {tv}'}
        resposta = requests.get(f'{base}/users/me', headers=headers)

        if resposta.status_code == 200:
            os.system('CLS')
            print('Programa feito por @imparcialista  v1.2.5.1')
            print(f'Conta conectada: {resposta.json()["nickname"]}')
            return tv
        else:
            print('Access Token inválido ou expirado')


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
        print('Nenhum anúncio ativo. Programa finalizado')
        return

    if quantidade_de_an > 1000:
        print(f'Quantidade de anúncios: {quantidade_de_an}')

        while quantidade_de_an > 0:
            quantidade_de_an -= 100
            paginas += 1

        paginas = paginas - 1

        lista_scroll = []
        primeiro_scroll = get_scroll_id(tv, dados_conta)
        print('Coletando IDs, por favor aguarde...')

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

        print(f'Quantidade de anúncios: {quantidade_de_an}')

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
        print(f'Pasta {dados_conta["nickname"]} criada')

    arquivo_json = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-ids_mlb.json'

    if os.path.exists(arquivo_json):
        os.remove(arquivo_json)

    with open(arquivo_json, 'w') as outfile:
        json.dump(lista, outfile)

    fim_timer = time.time()
    print(f'{dados_conta["nickname"]}: Todos os IDS foram coletados ')
    print(f'Tempo de execução: {(int(fim_timer - inicio_timer)) + 1} segundos')

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

    df = df.sort_values(by='status')
    df.to_excel(planilha, index=False)

    print(f'Planilha gerada')

    time.sleep(1)
    scn_df = pd.read_excel(planilha)


    def modify_tags(row):
        if 'supermarket_eligible' in str(row['tags']):
            return 'Supermercado'
        else:
            return row['shipping']


    scn_df['tags'] = scn_df.apply(modify_tags, axis=1)

    columns_to_keep = [
        'id', 'title', 'price', 'original_price',
        'available_quantity', 'attributes', 'status', 'tags'
        ]

    df_selected = scn_df[columns_to_keep]
    segunda_planilha = f'Arquivos/{dados_conta["nickname"]}/{dados_conta["id"]}-segunda-planilha.xlsx'
    df_selected.to_excel(segunda_planilha, index=False)

    print(f'Planilha para uso do App: {segunda_planilha}')


def get_promotions(item_id, tv):
    url = f"https://api.mercadolibre.com/seller-promotions/items/{item_id}?app_version=v2"
    headers = {
        "Authorization": f"Bearer {tv}"
        }
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 1))
            print(f"Limite de taxa excedido. Esperando {retry_after} segundos.")
            time.sleep(1)
        else:
            if response.status_code == 200:
                return item_id, response.json()
            else:
                return item_id, None


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

    promotion_info = {}

    batch_size = 100

    batches = [item_ids[i:i + batch_size] for i in range(0, len(item_ids), batch_size)]

    start_time = time.time()

    for batch in batches:
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(get_promotions, item_id, tv) for item_id in batch]
            for future in as_completed(futures):
                item_id, promotions = future.result()
                process_promotions(item_id, promotions, promotion_info)

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Tempo de execução: {execution_time:.2f} segundos")

    if not os.path.exists(f'Arquivos/{dados_conta["nickname"]}'):
        os.makedirs(f'Arquivos/{dados_conta["nickname"]}')
        print(f'Pasta {dados_conta["nickname"]} criada')

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

    print(f'Quantidade de anúncios: {quantidade_de_an}')

    while quantidade_de_an > 0:
        quantidade_de_an -= 20
        paginas += 1

    print(f'Páginas para percorrer: {paginas}')

    for pagina in range(paginas):
        inicio = gap_vinte
        fim = gap_vinte + 20
        itens = df[inicio:fim]
        lista_concatenada = ','.join(itens[0])
        lista_geral.append(lista_concatenada)
        gap_vinte += 20

    print(f'Por favor aguarde...')

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
    print(f'Informações coletadas. Tempo de execução: {(int(fim_timer - inicio_timer)) + 1} segundos')

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


def get_input():
    input_user = input(str('> '))
    input_user = input_user.lower()
    input_user = input_user.strip()
    return input_user


def main():
    os.system('CLS')
    sair = False
    token = configure_account()
    dados_conta = load_account_data(token)

    print(mensagem_base)

    while not sair:
        escolha = get_input()

        if escolha == 'sair':
            print('Encerrando...')
            break

        elif escolha == '?':
            print('Digite SAIR para encerrar')

        elif escolha == '1':
            token = ''
            main()

        elif escolha == '2':
            if token == '':
                token = configure_account()

            make_excel(token, dados_conta)

        elif escolha == '3' or escolha == 'Abrir planilha':
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
                print('Gerando a planilha...')
                make_excel(token, dados_conta)

            print('Abrindo o arquivo...')
            os.startfile(path)
            print('Arquivo aberto')

        elif escolha == '4':
            if token == '':
                token = configure_account()

            make_promotions_excel(token, dados_conta)

        else:
            print()
            print('Opção inválida | Escolha uma das opções')

            if token != '':
                print(f'Conta conectada: {dados_conta["nickname"]}')

        print(mensagem_base)


if __name__ == '__main__':
    main()
