import os
from smartbot.bot import Client
from smartbot.paths import SESSIONS_DIR
from telethon.network import ConnectionTcpFull
from enum import Enum
from smartbot.config import (
    BOT_TOKEN,
    APP_NAME,
    DEVICE_MODEL,
    SYSTEM_VERSION,
    APP_VERSION,
    ADMIN_IDS,
    API_ID,
    API_HASH,
)

SESSION_PATH: str = os.path.join(
    SESSIONS_DIR,
    APP_NAME
)

from constants import (
    ADMIN_COMMANDS,
    DEFAULT_COMMANDS
)


class ConversationState(Enum):
    """Enum to represent the state of the conversation with the user.
    This is used to manage the flow of the conversation and determine what
    the user is expected to do next.
    """
    IDLE = "idle"
    WAITING_USERNAME = "waiting_username"
    WAITING_PASSWORD = "waiting_password"
    WAITING_INPUT = "waiting_input"
    IN_MENU = "in_menu"
    PROCESSING = "processing"


plugins: dict[str, str | list[str]] = dict(
    root="plugins",
    include=[
        "commands.start_handler",
        "commands.help_handler",
        "commands.discipline_handler",
        "commands.grades_handler",
        "commands.notices_handler",
        "commands.notifier_handler",
        "commands.refresh_handler",
        "commands.restart_handler",
        "commands.clear_cache_handler",
        "commands.menu_handler",
        "callbacks.login_handler",
        "callbacks.menu_handler",
        "callbacks.grades_handler",
        "callbacks.periods_handler",
        "callbacks.notices_handler",
        "callbacks.materials_handler",
        "callbacks.calendar_handler",
        "callbacks.performance_handler",
        "callbacks.forum_handler",
        "callbacks.back_menu_handler",
        "callbacks.exit_handler",
        "callbacks.help_handler",
    ],
    exclude=["message"]
)
commands: dict[str, list[str]] = dict(
    admin_commands=ADMIN_COMMANDS,
    default_commands=DEFAULT_COMMANDS
)

profile: dict[str, str] = dict(
    name=APP_NAME,
    logo="src/media/logo.png",
    lang="pt",
    description=(
        "🎓 Consulte suas notas, prazos e desempenho acadêmico de forma simples e rápida, "
        "diretamente pelo Telegram."
    ),
    about="Bot não oficial de suporte acadêmico para instituições de ensino."
)

client: Client = Client(
    bot_token=BOT_TOKEN,
    session=SESSION_PATH,
    api_id=API_ID,
    api_hash=API_HASH,
    connection=ConnectionTcpFull,
    device_model=DEVICE_MODEL,
    system_version=SYSTEM_VERSION,
    app_version=APP_VERSION,
    admin_ids=ADMIN_IDS,
    commands=commands,
    plugins=plugins,
    config=profile,
    conversation_state=ConversationState,
)

if __name__ == "__main__":
    client.start_service()
