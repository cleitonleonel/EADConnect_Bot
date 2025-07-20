import re
import logging
from telethon import events
from typing import Any
from bs4 import BeautifulSoup
from datetime import datetime
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import with_stack_and_cleanup
from eadconnect.services.academic_service import AcademicService

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


def fetch_messages(ead_client):
    """
    Fetches messages from the user's messages.

    :return: A list of messages.
    """
    service = AcademicService(ead_client)
    messages = service.get_messages(items_per_page=5)
    return messages


def format_messages(messages):
    """
    Formats the messages for display.

    :param messages: A list of messages to format.
    :return: A formatted string of messages.
    """
    if not messages:
        return "Nenhuma notificação encontrada."

    message_str = ""
    for message in messages:
        content = message.get('content', '')
        content_text = BeautifulSoup(content, 'html.parser').get_text()
        match = re.search(r'https?://[^\s<>"]+', content_text)
        if match:
            link = match.group(0)
            content_text = content_text.replace(link, f'[Link]({link})').strip()

        created_at = message.get('createdAt', '')
        date_obj = datetime.fromisoformat(created_at)
        date_str = (
            date_obj.strftime('%d/%m/%Y %H:%M:%S') if date_obj else 'Data não disponível'
        )
        message_str += f"📬 Mensagem: {content_text}\n"
        message_str += f"📅 Enviada em: {date_str}\n"
        message_str += f"👤 De: {message.get('sender', {}).get('name', 'Desconhecido')}"
        message_str += "\n\n"
        message_str += f"{45 * '='}\n\n"

    return message_str or "Nenhuma notificação encontrada."


@client.on(events.CallbackQuery(pattern='^notificacoes$'))
@with_stack_and_cleanup()
async def handle_notices(event: Any):
    """
    Handles callback queries triggered by inline button interactions.

    :param event: The event is triggered by an inline button interaction.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"[Notices Handler] by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    utility_section = [
        ("🔙 Voltar", b"back_menu"),
    ]

    try:
        ead_client = event.client.get_user_data(sender_id, 'education_api')
        access_token = event.client.get_user_data(sender_id, 'access_token')
        if not ead_client or not access_token:
            event.client.set_user_state(sender_id, event.client.conversation_state.IDLE)
            return await event.client.just_answer(event, "❌ Cliente EAD não encontrado.", alert=True)

        ead_client.access_token = access_token
        back_buttons = build_inline_buttons(utility_section, cols=1)
        messages = fetch_messages(ead_client)
        notices_message = format_messages(messages)
        if not notices_message:
            return await event.client.just_answer(event, "Nenhuma notificação encontrada.", alert=True)

        await event.delete()
        await event.respond(notices_message, buttons=back_buttons)

    except Exception as e:
        logging.error(f"Erro ao buscar mensagens na plataforma: {e}")
        await event.client.just_answer(event, "❌ Erro ao carregar mensagens. Tente novamente.", alert=True)