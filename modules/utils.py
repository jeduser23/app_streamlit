"""
modules/utils.py
------------------
Funciones transversales usadas por varios módulos: cifrado de contraseñas,
manejo de estado de sesión de Streamlit y control de tiempo empleado en
las evaluaciones.
"""

import time
import bcrypt
import streamlit as st


# --------------------------------------------------------------------------
# Seguridad de contraseñas
# --------------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    """Genera un hash bcrypt seguro para almacenar en MySQL."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash bcrypt."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# --------------------------------------------------------------------------
# Sesión de usuario
# --------------------------------------------------------------------------
def init_session_state():
    """Inicializa las claves de `st.session_state` usadas en toda la app."""
    defaults = {
        "autenticado": False,
        "id_usuario": None,
        "id_estudiante": None,
        "rol": None,
        "cedula": None,
        "nombre_completo": None,
        "pagina_actual": "login",
        "asignatura_seleccionada": None,
        "avance": {},          # {asignatura: {'pretest':bool, 'adaptacion':bool, 'postest':bool}}
        "timer_inicio": None,
        "adaptacion_actual": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def cerrar_sesion():
    """Limpia el estado de sesión y regresa al login."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()
    st.session_state.pagina_actual = "login"


# --------------------------------------------------------------------------
# Cronómetro de evaluaciones
# --------------------------------------------------------------------------
def iniciar_cronometro():
    st.session_state.timer_inicio = time.time()


def obtener_tiempo_transcurrido() -> int:
    """Retorna los segundos transcurridos desde `iniciar_cronometro()`."""
    if st.session_state.get("timer_inicio") is None:
        return 0
    return int(time.time() - st.session_state.timer_inicio)
