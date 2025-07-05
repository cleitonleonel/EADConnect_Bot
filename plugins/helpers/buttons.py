from smartbot.utils.buttons import (
    Button,
    build_inline_buttons
)


def get_login_buttons() -> list[list[Button]]:
    """
    Returns a list of inline buttons for the login process.
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
