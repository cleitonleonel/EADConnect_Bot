import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import with_stack_and_cleanup
from eadconnect.services.academic_service import AcademicService

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


async def fetch_course_periods(ead_client) -> list:
    """
    Fetches the course periods from the API.
    This function should be replaced with the actual implementation to fetch periods.
    """
    service = AcademicService(ead_client)
    periods = service.get_active_periods()
    return periods[::-1]


@client.on(events.CallbackQuery(pattern='^select_periods$'))
@with_stack_and_cleanup()
async def handle_select_periods(event: Any):
    """
    Handler to list course periods dynamically from the API and show them as inline buttons.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"[Period Handler] Triggered by User ID: {sender_id}")

    try:
        ead_client = event.client.get_user_data(sender_id, 'education_api')
        access_token = event.client.get_user_data(sender_id, 'access_token')
        if not ead_client or not access_token:
            return await event.client.just_answer(event, "❌ Cliente EAD não encontrado.", alert=True)

        ead_client.access_token = access_token
        periods = await fetch_course_periods(ead_client)

        if not periods:
            return await event.client.just_answer(event, "❌ Nenhum período encontrado.", alert=True)

        buttons_data = [
            (period["name"], f"period_{period['id']}".encode())
            for period in periods
        ]

        utility_buttons = [("🔙 Voltar", b"back_menu")]

        period_buttons = (
            build_inline_buttons(buttons_data, cols=1) +
            [[]] +
            build_inline_buttons(utility_buttons, cols=1)
        )

        await event.delete()
        await event.respond(
            "📆 **Selecione o período desejado:**",
            buttons=period_buttons
        )

    except Exception as e:
        logging.error(f"Erro ao carregar períodos: {e}")
        await event.client.just_answer(event, "❌ Erro ao carregar os períodos.", alert=True)
