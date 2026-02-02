"""
Módulo de autenticação com Keycloak.
"""
import logging
import time
from typing import Any, Dict, Optional, Tuple, Union

from flask import session
import jwt
from dash import callback, Input, Output, State, no_update, ctx
from dash.exceptions import PreventUpdate

from keycloak import KeycloakOpenID
from config import Config

logger = logging.getLogger(__name__)


# --- Keycloak client ---------------------------------------------------------
keycloak_openid = KeycloakOpenID(
    server_url=Config.KEYCLOAK_SERVER_URL,
    client_id=Config.KEYCLOAK_CLIENT_ID,
    realm_name=Config.KEYCLOAK_REALM_NAME,
    client_secret_key=Config.KEYCLOAK_CLIENT_SECRET_KEY,
)

# Margem para renovar/avaliar expiração (segundos)
_TOKEN_SKEW = 30

# --- Helpers -----------------------------------------------------------------


def _now_ts() -> int:
    return int(time.time())


@callback(
    Output("greetings-user", "children"),
    Input("login-status", 'data'),
)
def get_info_user(login_status):

    print("PEGANDO INFO DO USUARIO")
    user_logged = session.get("name", ' ')
    return f"Welcome {user_logged.title()}"


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica um JWT sem verificar assinatura (apenas claims)."""
    try:
        print(token)
        return jwt.decode(token,
                          options={"verify_signature": False},
                          algorithms=["RS256"],)
    except jwt.exceptions.DecodeError as exc:
        logger.error("Falha ao decodificar token JWT", exc_info=exc)
        return None


def _save_tokens_to_session(token_bundle: Dict[str, Any]) -> None:
    """
    Guarda tokens e metadados na sessão Flask (servidor).
    NÃO colocar tokens no dcc.Store.
    """
    access_token = token_bundle.get("access_token")
    refresh_token = token_bundle.get("refresh_token")

    # Cálculo de expiração com base no 'expires_in' e 'refresh_expires_in'
    now = _now_ts()
    expires_in = int(token_bundle.get("expires_in", 0))  # ex.: 300
    refresh_expires_in = int(token_bundle.get(
        "refresh_expires_in", 0))  # ex.: 1800

    access_expires_at = now + max(0, expires_in - _TOKEN_SKEW)
    refresh_expires_at = now + max(0, refresh_expires_in - _TOKEN_SKEW)

    claims = decode_token(access_token) or {}
    session["kc"] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_expires_at": access_expires_at,
        "refresh_expires_at": refresh_expires_at,
        "session_state": token_bundle.get("session_state"),
        "scope": token_bundle.get("scope"),
        "token_type": token_bundle.get("token_type", "Bearer"),
        "claims": claims,
    }
    # Info útil para UI
    session["username"] = claims.get(
        "preferred_username") or claims.get("email") or ""
    session["name"] = claims.get("name") or session["username"]


def _clear_session() -> None:
    """Remove dados sensíveis da sessão Flask."""
    session.pop("kc", None)
    session.pop("username", None)
    session.pop("name", None)
    session.clear()


# --- LOGIN -------------------------------------------------------------------
@callback(
    Output("login-status", "data"),
    Output("url", "pathname"),
    Output("error-message", "children"),
    Output("error-message", "style"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True,
)
def check_credentials(
    n_clicks: int,
    username: str,
    password: str,
) -> Tuple[Dict[str, Any], Union[str, Any], str, Dict[str, str]]:
    print("to aqui")

    """Valida no Keycloak e redireciona ou mostra erro."""
    if not n_clicks:
        raise PreventUpdate

    print(username, password)

    if not username or not password:
        return (
            {"logged_in": False, "token": None},
            no_update,
            "Preencha usuário e senha.",
            {"display": "block"},
        )

    try:
        token_bundle = keycloak_openid.token(username, password)  # ROPC
        _save_tokens_to_session(token_bundle)

        home_path = f"{Config.ROOT_PATH_PREFIX.rstrip('/')}"
        # No front guardamos só o flag; token fica na sessão Flask
        return {"logged_in": True, "token": None}, home_path, "", {"display": "none"}

    except Exception as exc:
        print("falha")

        logger.warning("Falha de autenticação no Keycloak: %s", exc)
        _clear_session()
        return (
            {"logged_in": False, "token": None},
            no_update,
            "Usuário e/ou senha incorretos.",
            {"display": "block"},
        )


# --- LOGOUT ------------------------------------------------------------------
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("login-status", "data", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True,
)
def handle_logout(n_clicks: int):

    print("logoutando aq")
    """Revoga refresh_token no Keycloak, limpa sessão e manda para /login."""
    if not n_clicks:
        raise PreventUpdate

    token_state = session.get("kc") or {}
    refresh_token = token_state.get("refresh_token")
    try:
        if refresh_token:
            keycloak_openid.logout(refresh_token)
    except Exception as exc:
        logger.warning("Falha ao revogar sessão no Keycloak: %s", exc)

    _clear_session()

    login_path = f"{Config.ROOT_PATH_PREFIX.rstrip('/')}"
    return login_path, {"logged_in": False, "token": None}


# --- ENTER para enviar -------------------------------------------------------
@callback(
    Output("login-button", "n_clicks", allow_duplicate=True),
    Input("password", "n_submit"),
    Input("username", "n_submit"),
    State("login-button", "n_clicks"),
    prevent_initial_call=True,
)
def handle_enter(password_submit: int, username_submit: int, n_clicks: Optional[int]) -> int:
    """Permite submeter o login com Enter nos campos."""
    # Dispara um clique sintético
    return (n_clicks or 0) + 1


# --- REFRESH automático (opcional) ------------------------------------------
# Para ativar, inclua no seu layout base:
#   dcc.Interval(id="auth-keeper", interval=30*1000, n_intervals=0)
@callback(
    Output("login-status", "data", allow_duplicate=True),
    Input("auth-keeper", "n_intervals"),
    State("login-status", "data"),
    prevent_initial_call=True,
)
def refresh_access_token(_tick: int, login_status: Dict[str, Any]):
    """
    Renova o access_token quando perto da expiração.
    Mantém o 'login-status' como está (só atualiza sessão Flask).
    Se refresh falhar/expirar, derruba a sessão.
    """
    if not login_status or not login_status.get("logged_in"):
        raise PreventUpdate

    kc = session.get("kc") or {}
    now = _now_ts()

    # Se refresh já expirou, forçamos logout client-side
    if kc.get("refresh_expires_at", 0) <= now:
        logger.info("Refresh token expirado; limpando sessão.")
        _clear_session()
        return {"logged_in": False, "token": None}

    # Se access_token ainda está válido, nada a fazer
    if kc.get("access_expires_at", 0) > now:
        raise PreventUpdate

    # Está para expirar: tenta renovar
    try:
        new_bundle = keycloak_openid.refresh_token(kc.get("refresh_token"))
        _save_tokens_to_session(new_bundle)
        # Mantém o login-status como True, sem expor token ao front
        return no_update  # ou {"logged_in": True, "token": None}
    except Exception as exc:
        logger.warning("Falha ao renovar token; limpando sessão: %s", exc)
        _clear_session()
        return {"logged_in": False, "token": None}
