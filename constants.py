from telethon.tl.types import BotCommand

ADMIN_COMMANDS = [
    BotCommand(
        command="restart",
        description='Limpar cache de usuários e reiniciar o bot.'
    ),
    BotCommand(
        command="notifications",
        description='Enviar mensagem ou notificação para todos os usuários.'
    )
]

DEFAULT_COMMANDS = [
    BotCommand(
        command="start",
        description='Iniciar ou reiniciar uma conversa com o bot.'
    ),
    BotCommand(
        command="mensagens",
        description='Buscar e visualizar notificações, avisos e mensagens recebidas.'
    ),
    BotCommand(
        command="disciplinas",
        description='Listar as disciplinas de determinado curso.'
    ),
    BotCommand(
        command="notas",
        description='Verificar as notas em cada disciplina ou em uma disciplina específica.'
    ),
    BotCommand(
        command="refresh",
        description='Atualizar as notas e verificar se houve alguma alteração.'
    ),
    BotCommand(
        command="clear_cache",
        description='Limpar o cache de notas.'
    )
]
