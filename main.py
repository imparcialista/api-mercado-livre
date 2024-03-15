import flet as ft
import requests
import json


def main(page):
    def theme_changed(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        c.icon = (
            'LIGHT_MODE_SHARP' if page.theme_mode == ft.ThemeMode.LIGHT else 'DARK_MODE'
        )
        page.update()


    page.theme_mode = ft.ThemeMode.LIGHT
    c = ft.IconButton(
            icon=ft.icons.LIGHT_MODE_SHARP,
            icon_color='blue',
            icon_size=20,
            tooltip='Mudar tema',
            on_click=theme_changed
            )

    page.scroll = 'always'
    page.title = 'Aplicativo Luarco'


    def fazer_reqs(pagina, seller_sku, access_token_var):
        id_do_vendedor = access_token_var[-9:]
        url = (f'https://api.mercadolibre.com/users/'
               f'{id_do_vendedor}/items/search?seller_sku={seller_sku}&offset='
               f'{pagina}')

        payload = { }
        headers = { 'Authorization': f'Bearer {access_token_var}' }
        resposta = requests.request('GET', url, headers=headers, data=payload, timeout=60)
        if resposta.status_code == 200:
            resposta = resposta.json()
            return resposta
        
        else:
            msg_erro.value = 'Falha na requisição, altere os valores'
            sku_mlb.value = ''
            qtd_mlb.value = ''
            page.update()
            erro = 400
            return erro


    def atualizar_estoque(produto, quantidade, access_token_var):
        url = f'https://api.mercadolibre.com/items/{produto}'
        if quantidade > 0:
            payload = json.dumps({ 'available_quantity': quantidade, 'status': 'active' })
        else:
            payload = json.dumps({ 'available_quantity': quantidade })

        headers = {
            'Authorization': f'Bearer {access_token_var}',
            'Content-Type' : 'application/json',
            'Accept'       : 'application/json'
            }

        resposta = requests.request('PUT', url, headers=headers, data=payload, timeout=60)
        if resposta.status_code != 200:
            retorno = f'{produto} | Não pode ser alterado'
            txt_resposta = ft.Text(f'{retorno}', size=14, color='red')

        else:
            retorno = f'{produto} | Estoque alterado para {quantidade}'
            txt_resposta = ft.Text(f'{retorno}', size=14, color='green')

        return txt_resposta


    def limpar():
        msg_erro.value = ''
        sku_mlb.value = ''
        qtd_mlb.value = ''
        page.update()
        lista.controls.clear()
        page.update()

    def btn_limpar(e):
        limpar()


    def btn_click(e):
        access_token = access_token_label.value
        sku = sku_mlb.value
        qtd = qtd_mlb.value

        if not access_token_label.value:
            msg_erro.value = 'Por favor insira o Access Token'
            page.update()
        elif not sku_mlb.value:
            msg_erro.value = 'Por favor insira um SKU'
            page.update()
        elif not qtd_mlb.value:
            msg_erro.value = 'Por favor insira a quantidade'
            page.update()
        else:
            botoes.disabled = True
            c.disabled = True
            pr.opacity = 100
            
            page.update()
            limpar()
            retorno = fazer_reqs(0, sku, access_token)  # pega 50 produtos
            

            if retorno == 400:
                page.update()

            else:
                lista_resultado = ft.ListView(expand=False, spacing=10)
                quantidade_de_an = retorno['paging']['total']

                btn_limpar(e)
                qtd = int(qtd)

                texto = f'Alteração solicitada para {quantidade_de_an} anúncios\nSKU: {sku} | Estoque: {qtd}'
                txt_resposta = ft.Text(f'{texto}', size=14, color='blue', weight='bold')
                lista.controls.append(txt_resposta)

                if quantidade_de_an != 0:
                    if quantidade_de_an <= 50:
                        for produto in retorno['results']:
                            escrever = atualizar_estoque(produto, qtd, access_token)
                            lista_resultado.controls.append(escrever)
                    else:
                        while quantidade_de_an > 0:
                            quantidade_de_an -= 50
                            paginas += 1

                        for pagina in range(paginas):
                            retorno = fazer_reqs(pagina * 50, sku, access_token)
                            for produto in retorno['results']:
                                escrever = atualizar_estoque(produto, qtd, access_token)
                                lista_resultado.controls.append(escrever)

                    # return lista_resultado
                
                else:
                    limpar()
                    msg_erro.value = 'Nenhum anúncio encontrado'
                    page.update()

                lista.controls.append(lista_resultado)
                lista.controls.append(ft.Text(''))
                page.update()

            botoes.disabled = False
            c.disabled = False
            pr.opacity = 0
            
            page.update()


    texto_inicial = ft.Text(f'Atualizar estoque no Mercado Livre', size=14, color='blue', weight='bold')
    pr = ft.ProgressRing(width=16, height=16, stroke_width = 2, opacity=0, color='blue')
    inicio = ft.Row([texto_inicial, pr, c])

    access_token_label = ft.TextField(label='Access Token', width=310, value='', password=True)

    sku_mlb = ft.TextField(label='SKU', width=150, autofocus=True)
    qtd_mlb = ft.TextField(label='Quantidade', input_filter=ft.NumbersOnlyInputFilter(), width=150)
    valores = ft.Row([sku_mlb, qtd_mlb])

    btn_perguntar = ft.ElevatedButton('Atualizar', on_click=btn_click, width=150)
    btn_limpar_label = ft.ElevatedButton('Limpar', on_click=btn_limpar, width=150)
    botoes = ft.Row([btn_perguntar, btn_limpar_label])

    msg_erro = ft.Text(f'', size=14, color='red', weight='bold')
    lista = ft.ListView(expand=False, spacing=10)
    page.add(inicio, access_token_label, valores, botoes, msg_erro, lista)

ft.app(target=main)
