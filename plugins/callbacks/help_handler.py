import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import with_stack_and_cleanup

logging.basicConfig(level=logging.INFO)

client = ClientHandler()


@client.on(events.CallbackQuery(pattern='^ajuda$'))
@with_stack_and_cleanup()
async def handle_help(event: Any):
    """
    Handles callback queries triggered by inline button interactions.

    :param event: The event is triggered by an inline button interaction.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"[Help Handler] by User ID: {sender_id}")
    logging.debug(f"Event Client Instance: {event.client}")

    await event.delete()
    utility_section = [
        ("🔙 Voltar", b"back_menu"),
    ]
    back_buttons = build_inline_buttons(utility_section, cols=1)

    help_message = (
        "📚 __**Bem-vindo ao Assistente Acadêmico!**__\n\n"
        "Aqui estão os comandos disponíveis para te ajudar durante o semestre:\n\n"
        "`/vincular <RA> <senha>`\n"
        "🔐 Vincule sua conta acadêmica ao bot. (Use seu RA e senha do portal)\n\n"
        "`/notas`\n"
        "📊 Mostra suas últimas *notas* lançadas por disciplina.\n\n"
        "`/boletim`\n"
        "📄 Exibe seu *boletim completo*, com média final e status.\n\n"
        "`/horario`\n"
        "🕒 Mostra o seu *horário de aulas* atualizado.\n\n"
        "`/atualizar`\n"
        "🔄 Força a atualização manual dos dados da plataforma.\n\n"
        "`/desvincular`\n"
        "🚫 Remove o vínculo da sua conta com o bot.\n\n"
        "`/ajuda`\n"
        "📘 Exibe essa mensagem de ajuda.\n\n"
        "💡 *Dica:* Você receberá notificações automáticas quando houver alteração nas suas notas!\n"
        "Se tiver dúvidas ou sugestões, fale com o suporte."
    )
    await event.respond(help_message, buttons=back_buttons)
