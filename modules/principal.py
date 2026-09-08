"""
modules/principal.py
-----------------------
Pantalla principal del estudiante: tarjetas de Matemáticas, Física y Química.
Solo una asignatura es seleccionable a la vez. Controla el avance:
al completar el ciclo (pretest -> adaptación -> postest) de una asignatura,
esta se deshabilita y solo se muestran las pendientes hasta completar las tres.
"""

import streamlit as st
from database.db import run_query
from config import ASIGNATURAS

ICONOS = {"Matemáticas": "➗", "Física": "🧲", "Química": "🧪"}


def obtener_avance(id_estudiante):
    filas = run_query(
        """SELECT a.nombre, av.pretest_completado, av.adaptacion_generada, av.postest_completado
           FROM asignaturas a
           LEFT JOIN avance_estudiante av
             ON av.id_asignatura = a.id_asignatura AND av.id_estudiante = %s""",
        (id_estudiante,),
        fetch=True,
    )
    avance = {}
    for f in filas:
        avance[f["nombre"]] = {
            "pretest": bool(f["pretest_completado"]),
            "adaptacion": bool(f["adaptacion_generada"]),
            "postest": bool(f["postest_completado"]),
        }
    return avance


def pantalla_principal():
    st.title("🏠 Selecciona una asignatura")
    id_estudiante = st.session_state.id_estudiante
    avance = obtener_avance(id_estudiante)

    pendientes = [a for a in ASIGNATURAS if not avance.get(a, {}).get("postest")]

    if not pendientes:
        st.success("🎉 Has completado el ciclo Pretest → Adaptación → Postest en las tres asignaturas.")
        if st.button("Ver resultados comparativos y encuesta final", type="primary", use_container_width=True):
            st.session_state.pagina_actual = "resultados"
            st.rerun()
        return

    st.info("Selecciona una asignatura pendiente. Las asignaturas completadas se deshabilitan automáticamente.")
    cols = st.columns(3)

    for i, asignatura in enumerate(ASIGNATURAS):
        completada = avance.get(asignatura, {}).get("postest", False)
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"## {ICONOS.get(asignatura, '📘')} {asignatura}")
                if completada:
                    st.success("✅ Completada")
                else:
                    estado_actual = avance.get(asignatura, {})
                    if estado_actual.get("adaptacion"):
                        st.caption("Pendiente: Postest")
                    elif estado_actual.get("pretest"):
                        st.caption("Pendiente: Adaptación IA")
                    else:
                        st.caption("Pendiente: Pretest")

    # Un único control de selección (solo una asignatura seleccionable a la vez),
    # limitado a las asignaturas aún no completadas.
    seleccion = st.radio(
        "Asignatura a trabajar:",
        pendientes,
        index=None,
        horizontal=True,
        key="seleccion_asignatura_principal",
    )

    st.divider()
    if st.button("Continuar", type="primary", use_container_width=True, disabled=seleccion is None):
        st.session_state.asignatura_seleccionada = seleccion
        estado_actual = avance.get(seleccion, {})
        if estado_actual.get("adaptacion") and not estado_actual.get("postest"):
            st.session_state.pagina_actual = "adaptacion"
        elif estado_actual.get("pretest"):
            st.session_state.pagina_actual = "adaptacion"
        else:
            st.session_state.pagina_actual = "lectura"
        st.rerun()
