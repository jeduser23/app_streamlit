"""
app.py
-------
Punto de entrada de la aplicación Streamlit.
Ejecutar con:  streamlit run app.py

Flujo del estudiante:
  Login/Registro -> Pantalla principal (elegir asignatura) -> Lectura ->
  Pretest -> (repetir hasta completar las 3 asignaturas) -> Adaptación IA ->
  Postest -> Resultados comparativos -> Encuesta final

El administrador accede directamente al Dashboard + CRUD.
"""

import streamlit as st

from modules.utils import init_session_state, cerrar_sesion
from modules.auth import pantalla_autenticacion
from modules.principal import pantalla_principal
from modules.lectura import pantalla_lectura
from modules.pretest import pantalla_pretest
from modules.adaptacion_ia import pantalla_adaptacion
from modules.postest import pantalla_postest
from modules.resultados import pantalla_resultados_comparativos
from modules.encuesta import pantalla_encuesta
from modules.dashboard import pantalla_dashboard
from modules.admin_crud import pantalla_admin_crud

st.set_page_config(
    page_title="Adaptación Pedagógica de Textos Científicos con IA",
    page_icon="🎓",
    layout="wide",
)

init_session_state()


def _barra_lateral():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.nombre_completo}")
        st.caption(f"Rol: {st.session_state.rol}")
        if st.session_state.rol == "Estudiante" and st.session_state.asignatura_seleccionada:
            st.caption(f"Asignatura activa: {st.session_state.asignatura_seleccionada}")
        st.divider()
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()


def main():
    if not st.session_state.autenticado:
        pantalla_autenticacion()
        return

    _barra_lateral()

    if st.session_state.rol == "Administrador":
        tab = st.sidebar.radio("Panel", ["Dashboard", "Administración (CRUD)"])
        if tab == "Dashboard":
            pantalla_dashboard()
        else:
            pantalla_admin_crud()
        return

    # ---- Flujo del estudiante ----
    pagina = st.session_state.pagina_actual
    asignatura = st.session_state.asignatura_seleccionada

    if pagina == "principal":
        pantalla_principal()
    elif pagina == "lectura":
        pantalla_lectura(asignatura)
    elif pagina == "pretest":
        pantalla_pretest(asignatura)
    elif pagina == "adaptacion":
        pantalla_adaptacion(asignatura)
    elif pagina == "postest":
        nivel = st.session_state.adaptacion_actual["nivel"] if st.session_state.adaptacion_actual else "Básico"
        pantalla_postest(asignatura, nivel)
    elif pagina == "resultados":
        pantalla_resultados_comparativos(st.session_state.id_estudiante)
    elif pagina == "encuesta":
        pantalla_encuesta(st.session_state.id_estudiante)
    else:
        st.session_state.pagina_actual = "principal"
        st.rerun()


if __name__ == "__main__":
    main()
