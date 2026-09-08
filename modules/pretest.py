"""
modules/pretest.py
--------------------
Pantalla de pretest: obtiene el id de la asignatura seleccionada y delega
la lógica de evaluación al motor genérico `evaluacion.render_evaluacion`.
"""

import streamlit as st
from database.db import run_query
from modules.evaluacion import render_evaluacion


def pantalla_pretest(nombre_asignatura):
    asignatura = run_query(
        "SELECT id_asignatura FROM asignaturas WHERE nombre = %s", (nombre_asignatura,), fetch_one=True
    )
    completado = render_evaluacion(nombre_asignatura, asignatura["id_asignatura"], fase="pretest")
    if completado:
        if st.button("Continuar", type="primary"):
            st.session_state.pop(f"resultado_pretest_{asignatura['id_asignatura']}", None)
            st.session_state.pagina_actual = "principal"
            st.rerun()
