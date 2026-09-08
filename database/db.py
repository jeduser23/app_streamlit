"""
database/db.py
----------------
Capa de acceso a datos (DAO) para MySQL. Centraliza la conexión y expone
funciones reutilizables para cada módulo de la aplicación. Se usa
mysql-connector-python con cursores de tipo diccionario para simplificar
el consumo de resultados en Streamlit / pandas.
"""

import mysql.connector
from mysql.connector import pooling
import streamlit as st
from config import DB_CONFIG

_POOL = None


def get_pool():
    """Crea (una sola vez) y retorna el pool de conexiones a MySQL."""
    global _POOL
    if _POOL is None:
        _POOL = pooling.MySQLConnectionPool(
            pool_name="adaptacion_ia_pool",
            pool_size=5,
            **DB_CONFIG,
        )
    return _POOL


def get_connection():
    """Obtiene una conexión activa del pool. Manejar con context manager."""
    try:
        return get_pool().get_connection()
    except mysql.connector.Error as err:
        st.error(
            "No fue posible conectar a la base de datos MySQL. "
            "Verifique las credenciales en el archivo .env. "
            f"Detalle técnico: {err}"
        )
        st.stop()


def run_query(query, params=None, fetch=False, fetch_one=False, commit=False):
    """
    Ejecuta una consulta SQL genérica.
    - fetch=True       -> retorna lista de dicts
    - fetch_one=True   -> retorna un único dict o None
    - commit=True      -> confirma la transacción (INSERT/UPDATE/DELETE)
    Retorna el lastrowid cuando corresponde (INSERT).
    """
    conn = get_connection()
    result = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        elif fetch_one:
            result = cursor.fetchone()
        if commit:
            conn.commit()
            result = cursor.lastrowid
        cursor.close()
    except mysql.connector.Error as err:
        conn.rollback()
        st.error(f"Error en la base de datos: {err}")
    finally:
        conn.close()
    return result


def log_action(id_usuario, accion, detalle=""):
    """Registra una acción de auditoría en la tabla `logs`."""
    run_query(
        "INSERT INTO logs (id_usuario, accion, detalle) VALUES (%s, %s, %s)",
        (id_usuario, accion, detalle),
        commit=True,
    )
