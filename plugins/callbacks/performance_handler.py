import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import with_stack_and_cleanup

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.CallbackQuery(pattern='^desempenho$'))
@with_stack_and_cleanup()
async def handle_performance(event: Any):
    """
    Handles callback queries triggered by inline button interactions.

    :param event: The event is triggered by an inline button interaction.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"[Performance Handler] by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    await event.delete()
    utility_section = [
        ("🔙 Voltar", b"back_menu"),
    ]
    back_buttons = build_inline_buttons(utility_section, cols=1)

    performance_message = (
        "__**Desempenho**__\n\n"
        "Aqui você pode verificar o desempenho do bot.\n\n"
        "Use os botões abaixo para visualizar as estatísticas e informações de desempenho."
    )
    await event.respond(performance_message, buttons=back_buttons)
