import logging
from typing import Any
from telethon import events
from smartbot.utils.handler import ClientHandler

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.NewMessage(pattern='/avisos'))
async def handle_notices(event: Any):
    """
    Handles the `/avisos` command by sending a greeting message.

    :param event: The event triggered by the `/avisos` command.
    """

    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"Notices Handler Triggered by User ID: {sender_id}")
    logging.info(f"Event Client Instance: {event.client}")

    await event.client.send_message(
        sender_id,
        message=f'Mensagem enviada pelo client: {event.client}',
        buttons=None
    )
    await event.respond(
        message='Resposta enviada por evento.',
        buttons=None
    )
    await event.reply(
        f"Olá, {sender.first_name}! Este é o notices handler."
    )
