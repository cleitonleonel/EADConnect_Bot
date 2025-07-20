import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import with_stack_and_cleanup

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.CallbackQuery(pattern='^materiais$'))
@with_stack_and_cleanup()
async def handle_materials(event: Any):
    """
    Handles callback queries triggered by inline button interactions.

    :param event: The event is triggered by an inline button interaction.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"[Materials Handler] by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    await event.delete()
    utility_section = [
        ("🔙 Voltar", b"back_menu"),
    ]
    back_buttons = build_inline_buttons(utility_section, cols=1)

    materiais_message = (
        "__**Materiais**__\n\n"
        "Aqui você pode acessar diversos materiais de estudo e recursos úteis.\n\n"
        "Use os botões abaixo para navegar pelos diferentes tipos de materiais disponíveis."
    )
    await event.respond(materiais_message, buttons=back_buttons)
