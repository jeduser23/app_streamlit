"""
modules/resultados.py
------------------------
Resultados comparativos por estudiante: pretest vs postest para las tres
asignaturas, con promedio, diferencia absoluta e incremento porcentual,
visualizados con Plotly (barras y radar).
"""

import streamlit as st
import plotly.graph_objects as go
from database.db import run_query
from config import ASIGNATURAS


def _obtener_promedios(id_estudiante):
    datos = {}
    for asignatura in ASIGNATURAS:
        fila_pre = run_query(
            """SELECT AVG(p.calificacion) AS promedio FROM pretest p
               JOIN asignaturas a ON p.id_asignatura = a.id_asignatura
               WHERE p.id_estudiante = %s AND a.nombre = %s""",
            (id_estudiante, asignatura),
            fetch_one=True,
        )
        fila_post = run_query(
            """SELECT AVG(po.calificacion) AS promedio, MAX(po.nivel_adaptacion) AS nivel
               FROM postest po JOIN asignaturas a ON po.id_asignatura = a.id_asignatura
               WHERE po.id_estudiante = %s AND a.nombre = %s""",
            (id_estudiante, asignatura),
            fetch_one=True,
        )
        promedio_pre = float(fila_pre["promedio"]) if fila_pre and fila_pre["promedio"] else 0.0
        promedio_post = float(fila_post["promedio"]) if fila_post and fila_post["promedio"] else 0.0
        nivel = fila_post["nivel"] if fila_post and fila_post["nivel"] else None
        datos[asignatura] = {"pretest": promedio_pre, "postest": promedio_post, "nivel": nivel}
    return datos


def _guardar_resultados_consolidados(id_estudiante, datos):
    for asignatura, valores in datos.items():
        if valores["pretest"] == 0 and valores["postest"] == 0:
            continue
        diferencia = round(valores["postest"] - valores["pretest"], 2)
        incremento_pct = round(
            (diferencia / valores["pretest"]) * 100 if valores["pretest"] > 0 else 0, 2
        )
        asignatura_row = run_query(
            "SELECT id_asignatura FROM asignaturas WHERE nombre = %s", (asignatura,), fetch_one=True
        )
        run_query(
            """INSERT INTO resultados
               (id_estudiante, id_asignatura, promedio_pretest, promedio_postest,
                diferencia_absoluta, incremento_porcentual, nivel_adaptacion)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                id_estudiante,
                asignatura_row["id_asignatura"],
                valores["pretest"],
                valores["postest"],
                diferencia,
                incremento_pct,
                valores["nivel"] or "Básico",
            ),
            commit=True,
        )


def pantalla_resultados_comparativos(id_estudiante):
    st.title("📊 Resultados comparativos")
    datos = _obtener_promedios(id_estudiante)

    asignaturas = list(datos.keys())
    pretest_vals = [datos[a]["pretest"] for a in asignaturas]
    postest_vals = [datos[a]["postest"] for a in asignaturas]

    col1, col2, col3, col4 = st.columns(4)
    prom_pre_general = sum(pretest_vals) / len(pretest_vals) if pretest_vals else 0
    prom_post_general = sum(postest_vals) / len(postest_vals) if postest_vals else 0
    diferencia_general = prom_post_general - prom_pre_general
    incremento_general = (
        (diferencia_general / prom_pre_general) * 100 if prom_pre_general > 0 else 0
    )
    col1.metric("Promedio Pretest", f"{prom_pre_general:.2f}")
    col2.metric("Promedio Postest", f"{prom_post_general:.2f}")
    col3.metric("Diferencia absoluta", f"{diferencia_general:.2f}")
    col4.metric("Incremento %", f"{incremento_general:.1f}%")

    # ---- Gráfico de barras ----
    fig_barras = go.Figure(data=[
        go.Bar(name="Pretest", x=asignaturas, y=pretest_vals, marker_color="#6366F1"),
        go.Bar(name="Postest", x=asignaturas, y=postest_vals, marker_color="#10B981"),
    ])
    fig_barras.update_layout(
        title="Comparación Pretest vs Postest por asignatura",
        barmode="group",
        yaxis_title="Calificación (0-10)",
    )
    st.plotly_chart(fig_barras, use_container_width=True)

    # ---- Gráfico radar ----
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=pretest_vals, theta=asignaturas, fill="toself", name="Pretest"))
    fig_radar.add_trace(go.Scatterpolar(r=postest_vals, theta=asignaturas, fill="toself", name="Postest"))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title="Perfil comparativo por asignatura",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ---- Gráfico comparativo (líneas) ----
    fig_lineas = go.Figure()
    fig_lineas.add_trace(go.Scatter(x=asignaturas, y=pretest_vals, mode="lines+markers", name="Pretest"))
    fig_lineas.add_trace(go.Scatter(x=asignaturas, y=postest_vals, mode="lines+markers", name="Postest"))
    fig_lineas.update_layout(title="Evolución Pretest → Postest", yaxis_title="Calificación (0-10)")
    st.plotly_chart(fig_lineas, use_container_width=True)

    if st.button("Guardar resultados y continuar a la encuesta final", type="primary", use_container_width=True):
        _guardar_resultados_consolidados(id_estudiante, datos)
        st.session_state.pagina_actual = "encuesta"
        st.rerun()
