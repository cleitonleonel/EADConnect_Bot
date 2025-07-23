from smartbot.utils.buttons import (
    Button,
    build_inline_buttons
)
from telethon.tl.custom.message import Message


async def replace_button_text(
        message: 'Message',
        row: int,
        column: int,
        new_text: str
) -> list[list[Button]]:
    """
    Replaces the text of a specific inline button in a Telegram message.

    Args:
        message (Message): The Telethon Message object containing inline buttons.
        row (int): Row index of the button to be updated (0-based).
        column (int): Column index of the button to be updated (0-based).
        new_text (str): New text to display on the button.

    Raises:
        ValueError: If the message or its buttons are missing.
        IndexError: If the specified row/column is out of range.
    """

    if not message or not message.buttons:
        raise ValueError("Message or buttons not available.")

    buttons = message.buttons

    try:
        current_button = buttons[row][column]
    except IndexError:
        raise IndexError(f"Button not found at position [{row}][{column}].")

    new_button = Button.inline(new_text, current_button.data)

    buttons[row][column] = new_button

    return buttons


def get_login_buttons() -> list[list[Button]]:
    """
    Returns a list of inline buttons for the login process.

    The buttons are organized into sections for user input and utility actions.
    """
    login_section = [
        ("👤 Usuário", b"login_username"),
        ("🔑 Senha", b"login_password"),
    ]

    utility_section = [
        ("✅ Entrar", b"login_submit"),
        ("🔙 Voltar", b"back_menu"),
    ]

    login_buttons = (
            build_inline_buttons(login_section, cols=1)
            + [[]]
            + build_inline_buttons(utility_section, cols=2)
    )

    return login_buttons


def get_menu_buttons(no_login=False) -> list[list[Button]]:
    """
    Returns a list of inline buttons for the main menu.

    The buttons are organized into sections for login, main actions, notifications,
    """
    login_section = [
        ("👤 Login", b"login") if not no_login else ("", b""),
    ]

    main_section = [
        ("📖 Notas", b"select_periods"),
        ("📅 Datas", b"calendario"),
    ]

    notifier_section = [
        ("🔔 Notificações", b"notificacoes"),
    ]

    analise_section = [
        ("📚 Materiais", b"materiais"),
        ("📈 Análises", b"desempenho"),
    ]

    support_section = [
        ("💬 Fórum", b"forum"),
    ]

    utility_section = [
        ("❓ Ajuda", b"ajuda"),
        ("🚪 Sair", b"sair"),
    ]

    menu_buttons = (
            build_inline_buttons(login_section, cols=1)
            + build_inline_buttons(main_section, cols=2)
            + build_inline_buttons(notifier_section, cols=1)
            + build_inline_buttons(analise_section, cols=2)
            + build_inline_buttons(support_section, cols=1)
            + build_inline_buttons(utility_section, cols=2)
    )

    return menu_buttons
