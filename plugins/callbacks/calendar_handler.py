import logging
from telethon import events
from typing import Any
from datetime import date, timedelta, datetime
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import with_stack_and_cleanup
from eadconnect.services.academic_service import AcademicService

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


def fetch_calendar(ead_client, start_date=None, end_date=None):
    """
    Fetches calendar from the user's calendar.

    :return: A list of calendar.
    """
    service = AcademicService(ead_client)
    calendar = service.get_calendar(start_date, end_date)
    return calendar


def get_current_month_range():
    """Função para obter o intervalo do mês atual."""
    today = date.today()
    start_date = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(
            year=today.year + 1,
            month=1,
            day=1
        )
    else:
        next_month = today.replace(
            month=today.month + 1,
            day=1
        )
    end_date = next_month + timedelta(days=30)

    return today.strftime("%Y-%m-%d"), end_date.isoformat()


def format_calendar(calendar):
    """
    Formats the calendar for display.

    :param calendar: A list of calendar events to format.
    :return: A formatted string of calendar events.
    """
    if not calendar:
        return "Nenhum evento encontrado."

    calendar_str = ""
    for event in calendar:
        title = event.get('title') or 'Sem título'
        start_date = event.get('startAt') or 'Data não disponível'
        end_date = event.get('endAt') or 'Data não disponível'
        description = event.get('description') or 'Descrição não disponível'
        formated_start_date = (
            datetime
            .strptime(start_date, "%Y-%m-%d %H:%M:%S")
            .strftime("%Y-%m-%d")
        )
        calendar_str += f"📅 Evento: \n\n"
        calendar_str += f"📌 {title}\n"
        calendar_str += f"📖 Descrição: {description}\n"
        calendar_str += f"🕒 Inicia em: {formated_start_date}\n"
        calendar_str += f"🕔 Termina em: {end_date}\n"
        calendar_str += f"{45 * '='}\n\n"

    return calendar_str or "Nenhum evento encontrado."


@client.on(events.CallbackQuery(pattern='^calendario$'))
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

    try:
        ead_client = event.client.get_user_data(sender_id, 'education_api')
        access_token = event.client.get_user_data(sender_id, 'access_token')
        if not ead_client or not access_token:
            await event.client.just_answer(event, "❌ Cliente EAD não encontrado.", alert=True)
            return event.client.set_user_state(sender_id, event.client.conversation_state.IDLE)

        ead_client.access_token = access_token
        start_date, end_date = get_current_month_range()
        calendar = fetch_calendar(ead_client, start_date, end_date)
        if not calendar:
            return await event.respond("Nenhum evento encontrado no calendário.")

        calendar_str = format_calendar(calendar)
        await event.respond(calendar_str, buttons=back_buttons)

    except Exception as e:
        logging.error(f"Erro ao buscar o calendário: {e}")
        await event.respond("❌ Erro ao buscar o calendário. Tente novamente mais tarde.")
