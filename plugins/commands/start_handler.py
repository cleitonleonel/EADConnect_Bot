import logging
from typing import Any
from telethon import events, Button
from smartbot.utils.handler import ClientHandler
from smartbot.utils.menu import (
    with_stack_and_cleanup,
    MENU_KEY,
    DELETE_KEY
)

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.NewMessage(pattern='/start'))
@with_stack_and_cleanup()
async def handle_start(event: Any):
    """
    Handles the `/start` command by sending a greeting message.

    :param event: The event triggered by the `/start` command.
    """

    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Start Handler Triggered by User ID: {sender_id}")
    logging.info(f"Event Client Instance: {event.client}")
    event.client.drivers[sender_id][MENU_KEY].clear()

    welcome_message = (
        "🎓 **Bem-vindo ao Portal Acadêmico!**\n\n"
        "Olá! Eu sou seu assistente virtual para consulta de notas e informações acadêmicas.\n\n"
        "Através deste bot você pode:\n"
        "• Consultar suas notas por disciplina\n"
        "• Ver prazos de trabalhos e provas\n"
        "• Acompanhar seu desempenho acadêmico\n\n"
        "Para começar, clique no botão abaixo para acessar o menu principal."
    )

    main_button = Button.text("📚 Menu Principal", resize=True)
    welcome_msg = await event.respond(welcome_message, buttons=main_button)
    event.client.drivers[sender_id][DELETE_KEY].append(welcome_msg.id)
