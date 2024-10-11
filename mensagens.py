from termcolor import colored


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
