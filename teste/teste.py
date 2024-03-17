import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Routes Example"

    def salvar(e):
        if len(access_token_label.value) == 74:
            id_vendedor.color = 'green'



            if btn_salvar.text == 'Salvar':
                access_token_label.disabled = True
                btn_salvar.text = 'Editar'
                page.update()

                headers = {'Authorization': f'Bearer {access_token_label.value}'}

                resposta = requests.request("GET", 'https://api.mercadolibre.com/users/me', headers=headers)
                resposta = resposta.json()

                id_vendedor.value = resposta['id']
                nome_da_conta.value = resposta['nickname']

                positivo = resposta['seller_reputation']['transactions']['ratings']['positive']
                neutro = resposta['seller_reputation']['transactions']['ratings']['neutral']
                negativo = resposta['seller_reputation']['transactions']['ratings']['negative']
                '''
                positivo.title = f'{positivo * 100}%'
                neutro.title = f'{neutro * 100}%'
                negativo.title = f'{negativo * 100}%'
                '''
                imagem.src = (resposta['thumbnail']['picture_url'])
                imagem.border_radius = 50
                imagem.opacity = 100

                page.update()

            else:
                id_vendedor.value = ''

                access_token_label.disabled = False
                btn_salvar.text = 'Salvar'
                page.update()
        else:
            id_vendedor.value = 'Insira um Access Token válido'
            id_vendedor.color = 'red'
            page.update()

    def route_change(route):
        page.views.clear()

        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Aplicativo Luarco"), bgcolor=ft.colors.SURFACE_VARIANT),

                    info_conta, valores, botoes, msg_erro, lista
                ],
            )
        )
        if page.route == "/accesstoken":
            page.views.append(
                ft.View(
                    "/accesstoken",
                    [

                        ft.AppBar(title=ft.Text("Alterar Access Token"), bgcolor=ft.colors.SURFACE_VARIANT),
                        access,

                        nome_da_conta,




                    ],
                ),

            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)


    texto_dica = ft.Text(f'Atualizar estoque Mercado Livre', size=14, color='blue', weight='bold')
    carregando = ft.ProgressRing(width=16, height=16, stroke_width=2, opacity=0, color='blue')
    inicio = ft.Row([texto_dica, carregando])

    alterar_conta = ft.ElevatedButton("Alterar", on_click=lambda _: page.go("/accesstoken"), width=130, height=50)

    access_token_label = ft.TextField(label='Access Token', width=380, value='', password=True)

    sku_mlb = ft.TextField(label='SKU', width=130, autofocus=True)

    qtd_mlb = ft.TextField(label='Quantidade', input_filter=ft.NumbersOnlyInputFilter(), width=130)
    prc_mlb = ft.TextField(label='Preço', width=130)
    valores = ft.Row([sku_mlb, qtd_mlb, prc_mlb])

    btn_atualizar = ft.ElevatedButton('Atualizar', width=130, height=50)
    btn_limpar_label = ft.ElevatedButton('Limpar', width=130, height=50)
    botoes = ft.Row([btn_atualizar, btn_limpar_label])

    msg_erro = ft.Text(f'', size=14, color='red', weight='bold')
    lista = ft.ListView(expand=False, spacing=10)

    btn_voltar_home = ft.ElevatedButton("Voltar", on_click=lambda _: page.go("/"), width=130, height=50)
    btn_salvar = ft.ElevatedButton("Salvar", on_click=salvar, width=130, height=50)
    botoes_nav =ft.Row([btn_salvar, btn_voltar_home])


    imagem = ft.Image(src='aplicativo.png',opacity=0, width=50, height=50)

    id_vendedor = ft.TextField(label='ID do vendedor', read_only=True, value='', width = 200)
    nome_da_conta = ft.TextField(label='Conta', read_only=True, value='', width = 300, disabled=True)
    info_conta = ft.Row([nome_da_conta, imagem, alterar_conta])
    access = ft.Row([access_token_label, btn_salvar])


    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(target=main)