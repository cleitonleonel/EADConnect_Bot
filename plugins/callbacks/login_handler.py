import logging
from telethon import events
from typing import Any
from smartbot.utils.handler import ClientHandler
from smartbot.utils.menu import (
    with_stack_and_cleanup,
    DELETE_KEY
)
from plugins.helpers.buttons import (
    get_login_buttons,
    get_menu_buttons,
    replace_button_text
)
from eadconnect.utils.auth import authenticate

logging.basicConfig(level=logging.INFO)
client = ClientHandler()


@client.on(events.CallbackQuery(pattern=b'^login$'))
@with_stack_and_cleanup()
async def handle_login_command(event: Any):
    """
    Handle the main login command callback.

    This function displays the login menu with options to enter username,
    password, and submit login credentials.

    Args:
        event: Telegram callback query event
    """
    sender_id = event.sender_id
    await event.delete()
    login_buttons = get_login_buttons()

    login_msg = await event.respond("🔐 **Configurações de Acesso**", buttons=login_buttons)
    event.client.set_user_data(sender_id, 'login_message', login_msg)
    event.client.set_user_state(sender_id, event.client.conversation_state.IN_MENU)


@client.on(events.CallbackQuery(pattern=b'^login_username$'))
@with_stack_and_cleanup(False)
async def handle_username_request(event: Any):
    """
    Handle username input request callback.

    Prompts the user to send their username and sets the conversation
    state to wait for username input.

    Args:
        event: Telegram callback query event
    """
    sender_id = event.sender_id

    user_msg = await event.client.ask_user(
        sender_id,
        "✏️ Entre com seu **usuário**:",
        event.client.conversation_state.WAITING_USERNAME
    )
    event.client.drivers[sender_id][DELETE_KEY].append(user_msg.id)


@client.on(events.CallbackQuery(pattern=b'^login_password$'))
@with_stack_and_cleanup(False)
async def handle_password_request(event: Any):
    """
    Handle password input request callback.

    Prompts the user to send their password and sets the conversation
    state to wait for password input.

    Args:
        event: Telegram callback query event
    """
    sender_id = event.sender_id

    password_msg = await event.client.ask_user(
        sender_id,
        "✏️ Entre com sua **senha**:",
        event.client.conversation_state.WAITING_PASSWORD
    )
    event.client.drivers[sender_id][DELETE_KEY].append(password_msg.id)


@client.on(events.NewMessage)
async def handle_user_input(event: Any):
    """
    Handle user text input based on their current conversation state.

    This function processes user messages when they are in specific
    waiting states (username or password input).

    Args:
        event: Telegram new message event
    """
    sender_id = event.sender_id
    current_state = event.client.get_user_state(sender_id)
    login_msg = event.client.get_user_data(sender_id, 'login_message')

    if login_msg:
        delete_msg = event.client.drivers[sender_id][DELETE_KEY]
        await event.client.remove_messages(sender_id, [delete_msg[0]] if delete_msg else [])

    await event.delete()

    if current_state == event.client.conversation_state.WAITING_USERNAME:
        event.client.set_user_data(sender_id, 'username', event.text.strip())
        login_buttons = await replace_button_text(
            message=login_msg,
            row=0,
            column=0,
            new_text=f"👤 Usuário: {event.text.strip()}",
        )
        login_msg = await login_msg.edit("✅ Usuário salvo com sucesso!", buttons=login_buttons)
        event.client.set_user_data(sender_id, 'login_message', login_msg)
        event.client.set_user_state(sender_id, event.client.conversation_state.IN_MENU)

    elif current_state == event.client.conversation_state.WAITING_PASSWORD:
        event.client.set_user_data(sender_id, 'password', event.text.strip())
        login_buttons = await replace_button_text(
            message=login_msg,
            row=1,
            column=0,
            new_text=f"🔑 Senha = {'*' * len(event.text.strip())}",
        )
        login_msg = await login_msg.edit("✅ Senha salva com sucesso!.", buttons=login_buttons)
        event.client.set_user_data(sender_id, 'login_message', login_msg)
        event.client.set_user_state(sender_id, event.client.conversation_state.IN_MENU)

    elif current_state == event.client.conversation_state.IDLE:
        pass


@client.on(events.CallbackQuery(pattern=b'^login_submit$'))
@with_stack_and_cleanup(False)
async def handle_login_submit(event: Any):
    """
    Handle login submission callback.

    Validates that both username and password are provided, then attempts
    to authenticate the user with the education API.

    Args:
        event: Telegram callback query event
    """
    sender_id = event.sender_id

    username = event.client.get_user_data(sender_id, 'username')
    password = event.client.get_user_data(sender_id, 'password')

    if not username or not password:
        return await event.client.just_answer(
            event,
            "⚠️ Você precisa inserir o nome de usuário e a senha antes de fazer login.",
            alert=True
        )

    event.client.set_user_state(sender_id, event.client.conversation_state.PROCESSING)

    try:
        ead_client = event.client.get_user_data(sender_id, 'education_api')
        if not ead_client:
            event.client.set_user_state(sender_id, event.client.conversation_state.IDLE)
            return await event.client.just_answer(event, "❌ Cliente EAD não encontrado.", alert=True)

        ead_client.username = username
        ead_client.password = password

        access_token = authenticate(ead_client, attempts=1, auto_save=False)
        ead_client.access_token = access_token
        if not access_token:
            return await event.client.just_answer(
                event,
                "❌ Usuário ou Senha incorretos.\nPor favor, tente novamente.",
                alert=True
            )

        event.client.set_user_data(sender_id, 'access_token', access_token)

        success_message = await event.respond("✅ Login efetuado com sucesso!")

        login_msg = event.client.get_user_data(sender_id, 'login_message')
        if login_msg:
            await event.client.remove_messages(sender_id, [login_msg.id])

        event.client.set_user_data(sender_id, 'username', None)
        event.client.set_user_data(sender_id, 'password', None)

        menu_buttons = get_menu_buttons(no_login=access_token)

        menu_title = "📚 **Menu Principal**"
        await event.respond(menu_title, buttons=menu_buttons)
        await event.client.remove_messages(sender_id, [success_message.id])

        event.client.set_user_state(sender_id, event.client.conversation_state.IDLE)

    except Exception as e:
        await event.client.just_answer(
            event,
            "❌ Usuário ou Senha incorretos.\nPor favor, tente novamente.",
            alert=True
        )
        logging.error(f"Authentication error for user {sender_id}: {e}")
        event.client.set_user_state(sender_id, event.client.conversation_state.IN_MENU)


@client.on(events.NewMessage(pattern=r'/status'))
@with_stack_and_cleanup(False)
async def handle_status_command(event: Any):
    """
    Handle status command to show user's current conversation state.

    Args:
        event: Telegram new message event
    """
    sender_id = event.sender_id
    current_state = event.client.get_user_state(sender_id)

    if event.client.is_user_in_conversation(sender_id):
        await event.respond(f"🔄 You are in state: {current_state.value}")
    else:
        await event.respond("💤 You are idle.")


@client.on(events.NewMessage(pattern=r'/reset'))
@with_stack_and_cleanup(False)
async def handle_reset_command(event: Any):
    """
    Handle reset command to reset user's session to idle state.

    Args:
        event: Telegram new message event
    """
    sender_id = event.sender_id
    event.client.reset_user_session(sender_id)

    await event.respond("🔄 Sua sessão foi limpa.")


@client.on(events.NewMessage)
async def handle_global_conversation(event: Any):
    """
    Global conversation handler to process messages based on user state.

    This handler routes messages to appropriate conversation handlers
    based on the user's current conversation state.

    Args:
        event: Telegram new message event
    """
    await event.client.process_conversation_message(event)
