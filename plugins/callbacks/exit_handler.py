import logging
from telethon import events, Button
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.menu import (
    with_stack_and_cleanup,
    DELETE_KEY
)

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.CallbackQuery(pattern='^sair$'))
@with_stack_and_cleanup()
async def handle_exit(event: Any):
    """
    Handles callback queries triggered by inline button interactions.

    :param event: The event is triggered by an inline button interaction.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"[Exit Handler] by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    await event.delete()

    event.client.reset_user_session(sender_id)

    exit_message = (
        "👋 **Você saiu da aplicação!**\n\n"
        "💡 **Dica:** Para voltar, basta clicar no botão 'Menu Principal' abaixo.\n\n"
        "🗑️ **Aviso:** Seus dados foram limpos - não guardamos cache para proteger sua privacidade."
    )

    main_button = Button.text("📚 Menu Principal", resize=True)
    exit_msg = await event.respond(exit_message, buttons=main_button)
    event.client.drivers[sender_id][DELETE_KEY].append(exit_msg.id)
