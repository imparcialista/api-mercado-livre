import flet as ft
import requests
import json

# Obs: o scroll não está funcionando

def main(page: ft.Page):
    # Título
    page.title = 'Aplicativo Luarco'

    # Tamanho da janela
    #page.window_width = 650
    #page.window_height = 600

    # Configuração do tema
    page.theme_mode = ft.ThemeMode.DARK


    def theme_changed(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        icone.icon = (
            'LIGHT_MODE_SHARP' if page.theme_mode == ft.ThemeMode.LIGHT else 'DARK_MODE'
        )
        page.update()


    icone = ft.IconButton(
            icon=ft.icons.DARK_MODE,
            icon_color='blue',
            icon_size=20,
            tooltip='Mudar tema',
            on_click=theme_changed
            )


    # Funções

    def token_invalido():
        access_token_label.error_text = 'Insira um Access Token válido'
        access_token_label.disabled = False
        btn_salvar.disabled = False
        btn_voltar_home.disabled = False
        imagem.opacity = 0
        nome_da_conta.value = ''
        access_token_label.value = ''
        id_vendedor.value = ''
        btn_salvar.text = 'Salvar'
        page.update()


    def salvar(e):
        access_token_label.error_text = ''
        imagem.opacity = 0
        if btn_salvar.text == 'Salvar':
            if len(access_token_label.value) == 74:
                access_token_label.disabled = True
                btn_salvar.text = 'Salvando'
                btn_salvar.disabled = True
                btn_voltar_home.disabled = True
                page.update()
                headers = {
                    "Access-Control-Allow-Origin"
                    "Access-Control-Allow-Origin": "*",
                    "Authorization"              : f"Bearer {access_token_label.value}"
                    }
                resposta = requests.get('https://api.mercadolibre.com/users/me', headers=headers)

                if resposta.status_code == 200:
                    resposta = requests.get('https://api.mercadolibre.com/users/me', headers=headers)
                    resposta = resposta.json()

                    id_vendedor.value = resposta['id']
                    nome_da_conta.value = resposta['nickname']
                    page.update()
                    '''
                    positivo = resposta['seller_reputation']['transactions']['ratings']['positive']
                    neutro = resposta['seller_reputation']['transactions']['ratings']['neutral']
                    negativo = resposta['seller_reputation']['transactions']['ratings']['negative']
                    
                    positivo.title = f'{positivo * 100}%'
                    neutro.title = f'{neutro * 100}%'
                    negativo.title = f'{negativo * 100}%'
                    '''
                    imagem.src = (resposta['thumbnail']['picture_url'])
                    imagem.border_radius = 50
                    imagem.opacity = 100
                    btn_salvar.text = 'Editar'
                    btn_salvar.disabled = False
                    btn_voltar_home.disabled = False
                    msg_erro.value = ''

                    page.update()
                else:
                    token_invalido()

            else:
                token_invalido()
        else:
            nome_da_conta.value = ''
            access_token_label.value = ''
            id_vendedor.value = ''
            access_token_label.disabled = False
            btn_salvar.text = 'Salvar'
            page.update()


    def fazer_reqs(pagina, seller_sku, access_token_var):
        id_do_vendedor = access_token_var[-9:]

        url = F"https://api.mercadolibre.com/users/{id_do_vendedor}/items/search?seller_sku={seller_sku}&offset={pagina}"

        payload = { }
        headers = {
            "Access-Control-Allow-Origin": "https://luarco.com.br",
            "Authorization"              : f"Bearer {access_token_var}"
            }

        resposta = requests.request("GET", url, headers=headers, data=payload)

        print(resposta.text)
        print(resposta.json())

        if resposta.status_code == 200:
            resposta = resposta.json()
            return resposta
        else:
            msg_erro.value = 'Falha na requisição, altere os valores'
            qtd_mlb.value = ''
            prc_mlb.value = ''
            page.update()
            erro = 400
            return erro


    def atualizar(produto, valor_atualizar, access_token_var):
        url = f'https://api.mercadolibre.com/items/{produto}'

        if type(valor_atualizar) == int:
            if valor_atualizar > 0:
                payload = json.dumps({ "available_quantity": valor_atualizar, "status": "active" })

            else:
                payload = json.dumps({ "available_quantity": valor_atualizar })

        else:
            payload = json.dumps({ "price": valor_atualizar })

        headers = {
            "Access-Control-Allow-Origin": 'https://luarco.com.br',
            "Authorization"              : f"Bearer {access_token_var}",
            "Content-Type"               : "application/json"
            }

        resposta = requests.request("PUT", url, headers=headers, data=payload)

        #resposta = requests.request('PUT', url=url, data=payload, headers=headers)

        msg_erro.value = f'{resposta.json()}'
        page.update()

        if resposta.status_code != 200:
            #msg_erro.value = f'{resposta.json()}'
            retorno = f'{produto} | Não pôde ser alterado'
            txt_resposta = ft.Text(f'{retorno}', size=14, color='red')
            page.update()

        else:
            if type(valor_atualizar) == int:
                retorno = f'{produto} | Estoque alterado para {valor_atualizar}'
            else:
                valor_imprimir = valor_atualizar.replace('.', ',')
                retorno = f'{produto} | Preço alterado para R$ {valor_imprimir}'

            txt_resposta = ft.Text(f'{retorno}', size=14, color='green')

        return txt_resposta


    def pegar_produtos(sku, valor_atualizar, access_token_var):
        lista_resultado = ft.ListView(expand=False, spacing=10)
        paginas = 0
        resposta = fazer_reqs(0, sku, access_token_var)

        if resposta != 400:
            quantidade_de_an = resposta['paging']['total']

            if quantidade_de_an != 0:

                if quantidade_de_an <= 50:
                    for produto in resposta['results']:
                        escrever = atualizar(produto, valor_atualizar, access_token_var)
                        lista_resultado.controls.append(escrever)
                else:

                    while quantidade_de_an > 0:
                        quantidade_de_an -= 50
                        paginas += 1

                    for pagina in range(paginas):
                        resposta = fazer_reqs(pagina * 50, sku, access_token_var)

                        for produto in resposta['results']:
                            msg_erro.value = 'Carregando...'
                            page.update()
                            escrever = atualizar(produto, valor_atualizar, access_token_var)
                            lista_resultado.controls.append(escrever)

                return lista_resultado

            else:
                msg_erro.value = 'Nenhum anúncio encontrado'
                lista_resultado.controls.append(ft.Text(''))
                page.update()
                return lista_resultado
        else:
            msg_erro.value = 'Erro na requisição'
            lista_resultado.controls.append(ft.Text(''))
            page.update()
            return lista_resultado


    def limpar():
        msg_erro.value = ''
        sku_mlb.value = ''
        qtd_mlb.value = ''
        prc_mlb.value = ''
        page.update()
        lista.controls.clear()
        page.update()


    def btn_limpar(e):
        limpar()


    def desabilitar_botoes(booleano):

        if booleano == 'sim':
            alterar_conta.disabled = True
            botoes.disabled = True
            icone.disabled = True
            carregando.opacity = 100
        else:
            alterar_conta.disabled = False
            botoes.disabled = False
            icone.disabled = False
            carregando.opacity = 0

        page.update()


    def btn_click(e):
        desabilitar_botoes('sim')
        page.update()

        access_token = access_token_label.value
        sku = sku_mlb.value
        qtd = qtd_mlb.value
        prc = prc_mlb.value

        if not nome_da_conta.value:
            msg_erro.value = 'Por favor configure uma conta'
            desabilitar_botoes('não')
            page.update()

        elif not sku_mlb.value:
            msg_erro.value = 'Por favor insira um SKU'
            desabilitar_botoes('não')
            page.update()

        elif not qtd_mlb.value and not prc_mlb.value:
            desabilitar_botoes('não')
            msg_erro.value = 'Por favor insira a quantidade ou o preço para ser alterado'
            qtd_mlb.value = ''
            prc_mlb.value = ''
            page.update()

        elif qtd_mlb.value and prc_mlb.value:
            desabilitar_botoes('não')
            msg_erro.value = 'Por favor insira apenas a quantidade ou o preço'
            qtd_mlb.value = ''
            prc_mlb.value = ''
            page.update()

        else:
            if qtd_mlb.value and not prc_mlb.value:
                valor = int(qtd)
                texto_solicitacao = f'SOLICITAÇÃO DE ALTERAÇÃO\nSKU: {sku} | Estoque: {valor}'

            else:
                valor = str(prc)
                valor = valor.replace('.', '')

                texto_solicitacao = f'SOLICITAÇÃO DE ALTERAÇÃO\nSKU: {sku} | Preço: R$ {valor}'
                valor = valor.replace(',', '.')

            retorno = fazer_reqs(0, sku, access_token)

            if retorno == 400:
                desabilitar_botoes('não')
                msg_erro.value = 'Falha na requisição, altere os valores'
                qtd_mlb.value = ''
                prc_mlb.value = ''
                page.update()

            else:
                page.update()
                btn_limpar(e)
                txt_resposta = ft.Text(f'{texto_solicitacao}', size=16, color='blue', weight='bold')
                lista.controls.append(txt_resposta)

                lista_nova = pegar_produtos(sku, valor, access_token)

                lista.controls.append(ft.Text(''))
                lista.controls.append(lista_nova)
                lista.controls.append(ft.Text(''))
                desabilitar_botoes('não')
                msg_erro.value = ''
                page.scroll = 'always'
                page.update()


    def route_change(route):
        page.views.clear()

        page.views.append(
                ft.View(
                        '/',
                        [
                            ft.AppBar(title=ft.Text('Aplicativo Luarco'), bgcolor=ft.colors.SURFACE_VARIANT),
                            inicio,
                            info_conta,
                            valores,
                            botoes,
                            msg_erro,
                            lista
                            ],
                        )
                )

        if page.route == '/trocarconta':
            page.views.append(
                    ft.View(
                            '/trocarconta',
                            [

                                ft.AppBar(title=ft.Text('Alterar conta'), bgcolor=ft.colors.SURFACE_VARIANT),
                                access,
                                nome_da_conta,
                                id_vendedor,
                                botoes_nav

                                ],
                            ),

                    )
        page.update()


    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)


    # Elementos

    # ElevatedButton
    btn_voltar_home = ft.ElevatedButton('Voltar', on_click=lambda _: page.go('/'), width=150, height=50)
    btn_salvar = ft.ElevatedButton('Salvar', on_click=salvar, width=150, height=50)
    alterar_conta = ft.ElevatedButton('Alterar conta', on_click=lambda _: page.go('/trocarconta'), width=150, height=50)
    btn_atualizar = ft.ElevatedButton('Atualizar', on_click=btn_click, width=150, height=50)
    btn_limpar_label = ft.ElevatedButton('Limpar', on_click=btn_limpar, width=150, height=50)

    # Image
    imagem = ft.Image(src='aplicativo.png', opacity=0, width=50, height=50)

    # Text
    texto_do_inicio = ft.Text(f'Atualizar estoque ou preço dos produtos no Mercado Livre ', size=14, color='blue',
                              weight='bold')
    msg_erro = ft.Text(f'', size=14, color='red', weight='bold')

    # ProgressRing
    carregando = ft.ProgressRing(width=16, height=16, stroke_width=2, opacity=0, color='blue')

    # TextField
    sku_mlb = ft.TextField(label='SKU', width=150, autofocus=True)
    qtd_mlb = ft.TextField(label='Estoque', input_filter=ft.NumbersOnlyInputFilter(), width=150)
    prc_mlb = ft.TextField(label='Preço', width=150)
    access_token_label = ft.TextField(label='Access Token', width=410, value='', password=True)
    id_vendedor = ft.TextField(label='ID do vendedor', read_only=True, value='', width=410)
    nome_da_conta = ft.TextField(label='Conta', read_only=True, value='', width=410)

    # ListView
    lista = ft.ListView(expand=False, spacing=10)

    # Row
    botoes_nav = ft.Row([btn_salvar, btn_voltar_home])
    info_conta = ft.Row([nome_da_conta, imagem])
    access = ft.Row([access_token_label, imagem])
    inicio = ft.Row([texto_do_inicio, carregando, icone])
    valores = ft.Row([sku_mlb, qtd_mlb, prc_mlb])
    botoes = ft.Row([btn_atualizar, alterar_conta, btn_limpar_label ])

    # Rotas
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

    page.scroll = 'always'


ft.app(target=main)