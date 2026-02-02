# [atual] /app.py
"""
Ponto de entrada da aplicação Flask + Dash.
"""
import callbacks
import logging
from typing import Any
from datetime import timedelta
from config import Config
import os

from flask import Flask, Response, redirect
import dash
from dash import html, dcc, Input, Output, State, no_update
import dash_mantine_components as dmc
from dash import _dash_renderer

from login_layout import create_login_layout
from home_layout import layout_main


# Configurações de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajusta a versão do React para compatibilidade
_dash_renderer._set_react_version("18.2.0")

# registra mantine_light e mantine_dark no plotly
dmc.add_figure_templates()  # requer dmc >= 0.15.1

# Instância do servidor Flask
flask_server = Flask(__name__)
flask_server.secret_key = os.urandom(15)


@flask_server.errorhandler(404)
def page_not_found(error: Exception) -> tuple[str, int]:
    """
    Handler para erros 404.

    :param error: Exceção capturada.
    :return: Tupla com mensagem e código de status.
    """
    return "Página não encontrada", 404


@flask_server.errorhandler(500)
def internal_error(error: Exception) -> tuple[str, int]:
    """
    Handler para erros 500.

    :param error: Exceção capturada.
    :return: Tupla com mensagem e código de status.
    """
    return "Erro interno do servidor", 500


# Define prefixo de rota (assegura barra única ao final)
prefix = Config.ROOT.rstrip("/") + "/"

# Instância do app Dash
app = dash.Dash(
    __name__,
    title="Keycloak Dev Application",
    server=flask_server,
    use_pages=True,
    requests_pathname_prefix=prefix,
    routes_pathname_prefix=prefix,
    external_stylesheets=[
        "https://unpkg.com/boxicons@2.1.1/css/boxicons.min.css",
        dmc.styles.ALL,
        dmc.styles.DATES,
    ],
    external_scripts=[
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0\
            /dist/js/bootstrap.bundle.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/dayjs.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/locale/pt.min.js",
    ],
    suppress_callback_exceptions=True,
)

server = app.server


def serve_layout() -> Any:
    """
    Layout base do Dash, incluindo 
    MantineProvider e placeholders para roteamento.

    :return: Componente MantineProvider contendo o layout inicial.
    """
    return dmc.MantineProvider(
        theme={
            "colorScheme": "dark",
            "primaryColor": "indigo",
            "fontFamily": "'Inter', sans-serif",
        },
        children=[
            dcc.Location(id="url", refresh=True),
            dcc.Store(id="login-status", storage_type="session",
                      data={"logged_in": False, "token": None}),
            dcc.Interval(id="auth-keeper", interval=30*1000, n_intervals=0),
            html.Div(id="page-content"),
        ],
    )


app.layout = serve_layout


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    State("login-status", "data"),
    prevent_initial_call=False,
)
def render_page(pathname: str, login_status: dict) -> Any:
    """
    Decide o que renderizar em função da rota e do estado de login.

    - Se a rota for protegida e o usuário não estiver autenticado, 
    exibe o login.
    - Caso contrário, injeta o `dash.page_container`.

    :param pathname: Caminho atual da URL.
    :param login_status: Dado armazenado em session que indica estado de login.
    :return: Layout de login ou conteúdo da página solicitada.
    """

    # Normaliza barra final
    if pathname != "/" and pathname.endswith("/"):
        pathname = pathname[:-1]

    # Rotas que exigem autenticação (sempre sem barra final)
    prefix_clean = Config.ROOT.rstrip("/")  # home
    protected_routes = {
        f"{prefix_clean}",
    }
    login = login_status or {}

    # Se rota protegida e não logado, retorna layout de login

    if pathname in protected_routes and not login_status.get("logged_in", False):
        return create_login_layout()

    # Senão, renderiza a página normalmente
    return layout_main()


@app.server.route('/')
def home():
    return redirect('/home/')


if __name__ == "__main__":
    logger.info("Iniciando servidor em modo debug")
    app.run(
        debug=False,
        port=8052,
    )
