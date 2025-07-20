import logging
from telethon import events, Button
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.menu import (
    with_stack_and_cleanup,
    MENU_KEY,
    DELETE_KEY
)
from plugins.helpers.buttons import get_menu_buttons
from eadconnect.client import EducationAPI

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.CallbackQuery(pattern='^default_menu$'))
@with_stack_and_cleanup()
async def handle_menu(event: Any):
    """
    Handles the `📚 Menu Principal` command by sending a greeting message.

    :param event: The event is triggered by the `📚 Menu Principal` command.
    """
    sender = await event.get_sender()
    sender_id = sender.id

    await event.delete()

    logging.info(f"[Menu Handler] by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    help_msg = await event.respond(
        "__**Em que posso te ajudar???**__",
        buttons=Button.clear()
    )

    event.client.drivers[sender_id][MENU_KEY].clear()
    instance_api = event.client.get_user_data(sender_id, 'education_api')
    access_token = event.client.get_user_data(sender_id, 'access_token')
    if not instance_api:
        event.client.set_user_data(sender_id, 'education_api', EducationAPI())

    event.client.drivers[sender_id][DELETE_KEY].append(help_msg.id)

    menu_buttons = get_menu_buttons(no_login=access_token)
    menu_title = "📚 **Menu Principal**"
    return await event.respond(menu_title, buttons=menu_buttons)
