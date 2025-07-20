import logging
from telethon import events
from typing import Any, List, Dict
from datetime import datetime
from smartbot.utils.handler import ClientHandler
from smartbot.utils.buttons import build_inline_buttons
from smartbot.utils.menu import with_stack_and_cleanup
from eadconnect.services.academic_service import AcademicService

logging.basicConfig(level=logging.INFO)
client = ClientHandler()


async def fetch_disciplines_from_api(ead_client, period_id) -> List[Dict]:
    """Busca as disciplinas ativas do usuário na API de Educação."""
    service = AcademicService(ead_client)
    actual_courses = service.get_disciplines(
        period_id,
        status=[
            'isActual',
            'isSoon',
            'isPast'
        ]
    )
    return actual_courses


async def fetch_discipline_grades(ead_client, discipline_id: int) -> Dict:
    """
    Busca as notas de uma disciplina específica da API."""
    service = AcademicService(ead_client)
    actual_grades = service.get_grade_by_discipline_id(discipline_id)
    return actual_grades


def format_grades_message(grades_data: Dict) -> str:
    """
    Formata os dados das notas numa mensagem legível com emojis e Markdown para Telegram.
    """

    def format_date(date_str: str) -> str:
        try:
            if not date_str:
                return "Sem prazo"
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%Y às %H:%M")
        except Exception:
            return "Data inválida"

    def get_status_emoji(is_submited: bool, is_revised: bool, is_deadline_expired: bool) -> str:
        if is_submited and is_revised:
            return "✅ Entregue e Corrigido"
        elif is_submited:
            return "📤 Entregue"
        elif is_deadline_expired:
            return "⏰ Prazo Expirado"
        else:
            return "⏳ Pendente"

    discipline_name = grades_data.get('discipline_name', '📚 Disciplina Não Identificada')
    structure = grades_data.get('structure', [])
    final_grade = grades_data.get('finalGrade', {}).get('value', 0)
    final_grade_visible = grades_data.get('finalGrade', {}).get('isVisible', True)

    if final_grade >= 7.0:
        status = "✅ Aprovado"
        status_emoji = "🎉"
    elif final_grade >= 5.0:
        status = "⚠️ Recuperação"
        status_emoji = "📚"
    else:
        status = "❌ Reprovado"
        status_emoji = "😞"

    message = f"{status_emoji}   **{discipline_name}**\n"
    message += f"{'═' * 30}\n\n"

    for category in structure:
        category_name = category.get("name", "Categoria")
        category_value = category.get("value", 0)
        # sequence = category.get("sequence", 0)

        if "Atividade" in category_name:
            emoji = "📝"
        elif "Aulas" in category_name or "Unidades" in category_name:
            emoji = "📚"
        elif "Presencial" in category_name:
            emoji = "🏫"
        elif "SIMULADO" in category_name or "extra" in category_name:
            emoji = "🎯"
        elif "Exame" in category_name:
            emoji = "📋"
        else:
            emoji = "📊"

        message += f"{emoji} **{category_name}**\n"
        message += f"📈 Nota: {category_value}"

        formula = category.get("categoryFormula", {}).get("back", "")
        if formula and len(formula) > 0 and not 'mean' in formula.lower():
            message += f"\n🧮 Fórmula: {formula}"

        children = category.get("children", [])
        if children:
            message += "\n\n📋 **Detalhes:**\n"

            for child in children:
                child_name = child.get("name", "Item")
                child_value = child.get("value", 0)
                max_value = child.get("maxValue", 0)
                is_submited = child.get("isSubmited", False)
                is_revised = child.get("isRevised", False)
                is_deadline_expired = child.get("isDeadlineExpired", False)
                deadline = child.get("deadlineAt", "")

                status_text = get_status_emoji(is_submited, is_revised, is_deadline_expired)

                child_children = child.get("children", [])
                has_participation = any(
                    item.get("isParticipation", False) for item in child_children
                )

                if has_participation and child_children:
                    participation = child_children[0]  # Primeiro item é sempre a participação
                    # items = participation.get("items", [])
                    has_accessed_all = participation.get("hasAccessedAllItems", False)

                    message += f"\n• 🧠 **{child_name}**\n"
                    message += f"  📊 Nota: {child_value}/{max_value}\n"
                    message += f"  ⏰ Prazo: {format_date(deadline)}\n"
                    message += f"  🎯 Acesso: {'✅ Completo' if has_accessed_all else '⚠️ Incompleto'}\n"

                else:
                    message += f"\n• 📝 **{child_name}**\n"
                    message += f"  📊 Nota: {child_value}/{max_value}\n"
                    message += f"  ⏰ Prazo: {format_date(deadline)}\n"
                    message += f"  📋 Status: {status_text}\n"

        message += f"\n{'─' * 20}\n"

    message += f"\n🎯 **RESULTADO FINAL**\n"
    if final_grade_visible:
        message += f"📊 **Nota Final:** {final_grade}\n"
    else:
        message += f"📊 **Nota Final:** Oculta\n"

    message += f"🏆 **Status:** {status}\n"

    total_activities = sum(len(cat.get("children", [])) for cat in structure)
    completed_activities = sum(
        len([child for child in cat.get("children", [])
             if child.get("isSubmited", False) or
             any(item.get("hasAccessedAllItems", False)
                 for item in child.get("children", []))])
        for cat in structure
    )

    if total_activities > 0:
        completion_rate = (completed_activities / total_activities) * 100
        message += f"\n📈 **Taxa de Conclusão:** {completion_rate:.1f}%\n"

    if final_grade >= 7.0:
        message += f"\n🎉 **Parabéns! Você foi aprovado!**\n"
    elif final_grade >= 5.0:
        message += f"\n📚 **Atenção: Você está em recuperação**\n"
        message += f"💪 Estude para a prova final!\n"
    else:
        message += f"\n😔 **Você foi reprovado nesta disciplina**"
        message += f"💪 Não desista, tente novamente!\n"

    message += f"\n🤖 __Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}__"

    return message


@client.on(events.CallbackQuery(pattern=r'^period_\d+$'))
@with_stack_and_cleanup()
async def handle_grades(event: Any):
    """
    Handles callback queries triggered by inline button interactions.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    logging.info(f"[Grades Handler] by User ID: {sender_id}")
    period_id = int(event.data.decode().split("_")[1])

    try:
        ead_client = event.client.get_user_data(sender_id, 'education_api')
        access_token = event.client.get_user_data(sender_id, 'access_token')
        if not ead_client or not access_token:
            event.client.set_user_state(sender_id, event.client.conversation_state.IDLE)
            return await event.client.just_answer(event, "❌ Cliente EAD não encontrado.", alert=True)

        ead_client.access_token = access_token
        disciplines_data = await fetch_disciplines_from_api(ead_client, period_id)

        if not disciplines_data:
            return await event.client.just_answer(event, "❌ Nenhuma disciplina encontrada.", alert=True)

        disciplines = []
        for discipline in disciplines_data:
            discipline_name = discipline.get('name', 'Disciplina Desconhecida')
            formatted_name = ' '.join(discipline_name.split()[:-1])
            button_text = discipline.get('code', formatted_name)  # Use code or name for button text
            progress = discipline.get('progress', '')
            callback_data = f"grade_detail_{discipline['id']}_{'_'.join(button_text.split())}".encode()
            if progress:
                button_text += f" ({progress}%)"

            disciplines.append((button_text, callback_data))

        utility_section = [
            ("🔙 Voltar", b"back_menu"),
        ]

        disciplines_buttons = (
                build_inline_buttons(disciplines, cols=1)
                + [[]]
                + build_inline_buttons(utility_section, cols=1)
        )

        await event.delete()
        menu_title = "📚 **Selecione uma disciplina**"
        await event.respond(menu_title, buttons=disciplines_buttons)

    except Exception as e:
        logging.error(f"Erro ao buscar disciplinas: {e}")
        await event.client.just_answer(event, "❌ Erro ao carregar disciplinas. Tente novamente.", alert=True)


@client.on(events.CallbackQuery(pattern=r'^grade_detail_(\d+)_(.+)$'))
@with_stack_and_cleanup()
async def handle_grade_detail(event: Any):
    """
    Handles callback queries for specific discipline grade details.
    """
    sender = await event.get_sender()
    sender_id = sender.id

    discipline_id = int(event.pattern_match.group(1))
    discipline_name = event.pattern_match.group(2).decode('utf-8')

    logging.info(f"Grade detail requested by User ID: {sender_id} for discipline: {discipline_id}")

    try:
        ead_client = event.client.get_user_data(sender_id, 'education_api')
        access_token = event.client.get_user_data(sender_id, 'access_token')
        if not ead_client or not access_token:
            event.client.set_user_state(sender_id, event.client.conversation_state.IDLE)
            return await event.client.just_answer(event, "❌ Cliente EAD não encontrado.", alert=True)

        ead_client.access_token = access_token
        grades_data = await fetch_discipline_grades(ead_client, discipline_id)
        if not grades_data or not grades_data.get('finalGrade')['value']:
            return await event.client.just_answer(event, "❌ Nenhuma nota encontrada para esta disciplina.", alert=True)

        grades_data.update({'discipline_name': discipline_name.replace('_', ' ')})
        grades_message = format_grades_message(grades_data)

        back_buttons = build_inline_buttons([
            ("🔙 Voltar às Disciplinas", b"back_menu"),
            ("🏠 Menu Principal", b"default_menu"),
        ], cols=1)

        await event.delete()
        await event.respond(grades_message, buttons=back_buttons)
    except Exception as e:
        logging.error(f"Erro ao buscar notas da disciplina {discipline_id}: {e}")
        await event.client.just_answer(event, "❌ Erro ao carregar notas. Tente novamente.", alert=True)
