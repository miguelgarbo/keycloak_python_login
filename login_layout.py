# [atual] layouts/login_layout.py
"""Layout da página de login."""

from __future__ import annotations

from typing import Any

import dash_mantine_components as dmc
from dash import dcc, html
from dash.development.base_component import Component as DashComponent

from config import Config


def create_login_layout() -> DashComponent:
    return html.Main(
        className="login-body",
        children=[
            dmc.Center(
                style={"width": "100%", "minHeight": "100vh"},
                children=[
                    dmc.Paper(
                        withBorder=False,
                        shadow="xl",
                        radius="lg",
                        p=26,
                        style={
                            "backgroundColor": "#fff",
                            "width": "100%",
                            "maxWidth": 360,
                            "animation": "fadeIn 0.5s ease-out",
                        },
                        children=[
                            # Logo principal

                            # Inputs com ícones
                            dmc.Title("Keycloak Login", order=2, pb=20),

                            dmc.Stack(
                                gap="sm",
                                children=[
                                    dmc.TextInput(
                                        id="username",
                                        placeholder="Usuário",
                                        size="md",
                                        radius="sm",
                                        required=True,
                                        # reserva espaço p/ o ícone
                                        leftSectionWidth=36,
                                        styles={
                                            "input": {
                                                "height": 45,
                                            },
                                            # evita que o clique no ícone roube o foco
                                            "section": {"pointerEvents": "none"},
                                        },
                                    ),
                                    dmc.PasswordInput(
                                        id="password",
                                        placeholder="Senha",
                                        size="md",
                                        radius="sm",
                                        required=True,
                                        leftSectionWidth=36,
                                        styles={
                                            "input": {
                                                "height": 45,
                                            },
                                        },
                                    ),
                                    dmc.Text(
                                        id="password-error",
                                        children="Por favor, insira sua senha",
                                        size="sm",
                                        style={
                                            "display": "none",
                                            "color": "#a0a0a0",
                                            "fontWeight": 500,
                                        },
                                    ),
                                ],
                            ),
                            # Botão "Entrar"
                            dmc.Button(
                                "Entrar",
                                id="login-button",
                                size="md",
                                fullWidth=True,
                                mt=28,
                                radius="sm",
                                variant="filled",
                                color="#529ee2",
                                styles={
                                    "root": {
                                        "color": "#ffffff",
                                        "border": "none",
                                        "textTransform": "uppercase",
                                        "fontWeight": 600,
                                        "padding": "13px 36px",
                                        "borderRadius": "5px",
                                        "letterSpacing": "1px",
                                        "cursor": "pointer",
                                        "transition": "all 0.3s ease",
                                        "boxShadow": (
                                            "0 4px 6px rgba(0, 0, 0, 0.3)"
                                        ),
                                        "&:hover": {
                                            "background": (
                                                "linear-gradient(135deg, "
                                                "#707070 0%, #909090 100%)"
                                            ),
                                            "transform": "translateY(-2px)",
                                            "boxShadow": (
                                                "0 6px 8px rgba(0, 0, 0, 0.4)"
                                            ),
                                        },
                                        "&:active": {
                                            "transform": "translateY(0)",
                                        },
                                    }
                                },
                            ),
                            # Hidden submit
                            # (se você usa Enter/n_submit em algum lugar)
                            dcc.Input(
                                id="hidden-submit",
                                type="text",
                                style={"display": "none"},
                                n_submit=0,
                            ),
                            # Saída e erro
                            html.Div(id="login-output"),
                            dmc.Text(
                                id="error-message",
                                children="",
                                ta="center",
                                mt="sm",
                                style={
                                    "display": "none",
                                    "color": "#ff6b6b",
                                    "fontWeight": 600,
                                },
                            ),

                        ],
                    ),
                ],
            ),
        ],
    )


__all__ = ["create_login_layout"]
