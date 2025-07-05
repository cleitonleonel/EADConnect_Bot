import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import with_stack_and_cleanup

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.CallbackQuery(pattern='^notificacoes$'))
@with_stack_and_cleanup()
async def handle_notices(event: Any):
    """
    Handles callback queries triggered by inline button interactions.

    :param event: The event is triggered by an inline button interaction.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Callback Triggered by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    await event.delete()
    utility_section = [
        ("🔙 Voltar", b"back_menu"),
    ]
    back_buttons = build_inline_buttons(utility_section, cols=1)

    notices_message = (
        "__**Notificações**__\n\n"
        "Aqui você pode gerenciar suas notificações.\n\n"
        "Use os botões abaixo para configurar suas preferências."
    )
    await event.respond(notices_message, buttons=back_buttons)
