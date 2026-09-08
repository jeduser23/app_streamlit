"""
modules/auth.py
-----------------
Módulo de autenticación: registro de estudiantes y login (admin y estudiantes).
Login: cédula (usuario) + password.
"""

import streamlit as st
from database.db import run_query, log_action
from modules.utils import hash_password, verify_password
from config import TIEMPOS_LECTURA


def _obtener_id_rol_estudiante():
    fila = run_query("SELECT id_rol FROM roles WHERE nombre_rol = 'Estudiante'", fetch_one=True)
    return fila["id_rol"] if fila else None


def pantalla_registro():
    st.subheader("📝 Registro de estudiante")
    with st.form("form_registro", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            nombres = st.text_input("Nombres *")
            edad = st.number_input("Edad *", min_value=10, max_value=25, step=1)
            cedula = st.text_input("Cédula *")
            tiempo_lectura = st.selectbox("Tiempo diario de lectura *", TIEMPOS_LECTURA)
        with col2:
            apellidos = st.text_input("Apellidos *")
            especializacion = st.text_input("Especialización *", placeholder="Ej. Ciencias, Técnico...")
            password = st.text_input("Contraseña *", type="password")
            password2 = st.text_input("Confirmar contraseña *", type="password")

        enviado = st.form_submit_button("Registrarme", use_container_width=True)

    if enviado:
        campos = [nombres, apellidos, cedula, especializacion, password, password2]
        if any(not str(c).strip() for c in campos):
            st.error("Debe completar todos los campos obligatorios (*).")
            return
        if password != password2:
            st.error("Las contraseñas no coinciden.")
            return
        if len(password) < 6:
            st.error("La contraseña debe tener al menos 6 caracteres.")
            return

        existente = run_query(
            "SELECT id_usuario FROM usuarios WHERE cedula = %s", (cedula,), fetch_one=True
        )
        if existente:
            st.error("Ya existe un usuario registrado con esta cédula.")
            return

        id_rol = _obtener_id_rol_estudiante()
        id_usuario = run_query(
            """INSERT INTO usuarios (cedula, password_hash, id_rol, estado)
               VALUES (%s, %s, %s, 'activo')""",
            (cedula, hash_password(password), id_rol),
            commit=True,
        )
        run_query(
            """INSERT INTO estudiantes
               (id_usuario, nombres, apellidos, edad, especializacion, tiempo_lectura_diario)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (id_usuario, nombres, apellidos, int(edad), especializacion, tiempo_lectura),
            commit=True,
        )
        log_action(id_usuario, "registro_estudiante", f"Cédula {cedula}")
        st.success("✅ Registro exitoso. Ahora puede iniciar sesión.")
        st.session_state.pagina_actual = "login"


def pantalla_login():
    st.subheader("🔐 Iniciar sesión")
    with st.form("form_login"):
        cedula = st.text_input("Cédula")
        password = st.text_input("Contraseña", type="password")
        enviado = st.form_submit_button("Ingresar", use_container_width=True)

    if enviado:
        usuario = run_query(
            """SELECT u.id_usuario, u.password_hash, u.estado, r.nombre_rol
               FROM usuarios u JOIN roles r ON u.id_rol = r.id_rol
               WHERE u.cedula = %s""",
            (cedula,),
            fetch_one=True,
        )
        if not usuario or not verify_password(password, usuario["password_hash"]):
            st.error("Cédula o contraseña incorrecta.")
            return
        if usuario["estado"] != "activo":
            st.error("Su cuenta se encuentra inactiva. Contacte al administrador.")
            return

        run_query(
            "UPDATE usuarios SET fecha_ultima_conexion = NOW() WHERE id_usuario = %s",
            (usuario["id_usuario"],),
            commit=True,
        )

        st.session_state.autenticado = True
        st.session_state.id_usuario = usuario["id_usuario"]
        st.session_state.rol = usuario["nombre_rol"]
        st.session_state.cedula = cedula

        if usuario["nombre_rol"] == "Estudiante":
            estudiante = run_query(
                "SELECT id_estudiante, nombres, apellidos FROM estudiantes WHERE id_usuario = %s",
                (usuario["id_usuario"],),
                fetch_one=True,
            )
            st.session_state.id_estudiante = estudiante["id_estudiante"]
            st.session_state.nombre_completo = f'{estudiante["nombres"]} {estudiante["apellidos"]}'
            st.session_state.pagina_actual = "principal"
        else:
            st.session_state.nombre_completo = "Administrador"
            st.session_state.pagina_actual = "dashboard"

        log_action(usuario["id_usuario"], "login", f"Rol: {usuario['nombre_rol']}")
        st.rerun()


def pantalla_autenticacion():
    """Punto de entrada del módulo: alterna entre login y registro."""
    st.title("🎓 Adaptación Pedagógica de Textos Científicos con IA")
    tab_login, tab_registro = st.tabs(["Iniciar sesión", "Registrarme"])
    with tab_login:
        pantalla_login()
    with tab_registro:
        pantalla_registro()
