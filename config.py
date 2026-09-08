"""
config.py
----------
Configuración centralizada de la aplicación.
Carga variables de entorno (.env) para credenciales de MySQL y Google AI Studio.
No se deben escribir credenciales directamente en el código fuente.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------
# Lectura de configuración compatible con dos entornos:
#  - Local: variables definidas en un archivo .env (python-dotenv)
#  - Streamlit Community Cloud: st.secrets (secrets.toml configurado en el
#    panel "Settings > Secrets" de la app, nunca subido al repositorio)
# st.secrets tiene prioridad si existe la clave; de lo contrario se usa
# la variable de entorno / valor por defecto.
# --------------------------------------------------------------------------
def _get(key, default=""):
    """Busca `key` primero en st.secrets (Streamlit Community Cloud) y,
    si no existe archivo de secretos o la clave no está definida allí,
    recurre a las variables de entorno / .env (uso local)."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass  # sin secrets.toml (entorno local) o fuera de un runtime de Streamlit
    return os.getenv(key, default)


# --------------------------------------------------------------------------
# Base de datos MySQL
# --------------------------------------------------------------------------
DB_CONFIG = {
    "host": _get("DB_HOST", "localhost"),
    "port": int(_get("DB_PORT", "3306")),
    "user": _get("DB_USER", "root"),
    "password": _get("DB_PASSWORD", ""),
    "database": _get("DB_NAME", "adaptacion_ia_db"),
    "autocommit": True,
}

# --------------------------------------------------------------------------
# Google AI Studio / Gemini API MODEL_NAMES = "gemini-2.5-pro" MODEL_NAME = "gemini-3-flash-preview"
# --------------------------------------------------------------------------
GEMINI_API_KEY = _get("GEMINI_API_KEY", "")
GEMINI_MODEL = _get("GEMINI_MODEL", "gemini-3-flash-preview")

# --------------------------------------------------------------------------
# Seguridad
# --------------------------------------------------------------------------
APP_SECRET = _get("APP_SECRET", "cambiar_este_valor_en_produccion")

# --------------------------------------------------------------------------
# Reglas de negocio (constantes del proyecto de investigación)
# --------------------------------------------------------------------------
ASIGNATURAS = ["Matemáticas", "Física", "Química"]
NIVELES_ADAPTACION = ["Básico", "Medio", "Avanzado"]
TIEMPOS_LECTURA = ["5 minutos", "15 minutos", "30 minutos", "60 minutos"]
NUM_PREGUNTAS_EVALUACION = 5

# Credenciales del administrador que se crean automáticamente (ver seed.sql)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123!"  # Se almacena cifrada (bcrypt) en la base de datos

# Prompt maestro para la adaptación pedagógica con Gemini
PROMPT_ADAPTACION = """OBJETIVO:
Adaptar el texto científico para estudiantes de bachillerato.

REGLAS:
1. Mantener términos científicos esenciales.
2. No simplificar conceptos clave.
3. Generar entre 218 y 220 palabras.
4. Utilizar ejemplos contextualizados.
5. Dividir el contenido en:
   - Conceptos clave
   - Ejemplo práctico
   - Resumen final

NIVEL: {nivel}

Comportamiento esperado según el nivel:
- BÁSICO: lenguaje sencillo, explicaciones simples.
- MEDIO: lenguaje intermedio, ejemplos académicos.
- AVANZADO: lenguaje técnico, mayor profundidad conceptual.

TEXTO ORIGINAL:
\"\"\"
{texto_original}
\"\"\"

Responde ÚNICAMENTE en formato JSON válido, sin texto adicional ni marcas de
código, con esta estructura exacta:
{{
  "conceptos_clave": "string",
  "ejemplo_practico": "string",
  "resumen_final": "string"
}}
"""
