"""
modules/postest.py
---------------------
Pantalla de postest: se ejecuta después de cada adaptación pedagógica con IA.
Registra el nivel de adaptación con el que se generó el texto.
"""

import streamlit as st
from database.db import run_query
from modules.evaluacion import render_evaluacion


def pantalla_postest(nombre_asignatura, nivel_adaptacion):
    asignatura = run_query(
        "SELECT id_asignatura FROM asignaturas WHERE nombre = %s", (nombre_asignatura,), fetch_one=True
    )
    completado = render_evaluacion(
        nombre_asignatura, asignatura["id_asignatura"], fase="postest", nivel_adaptacion=nivel_adaptacion
    )
    if completado:
        if st.button("Continuar", type="primary"):
            st.session_state.pop(f"resultado_postest_{asignatura['id_asignatura']}", None)
            st.session_state.pagina_actual = "principal"
            st.rerun()
