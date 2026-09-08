"""
modules/dashboard.py
-----------------------
Dashboard administrativo: totales, promedios generales, resultados por
asignatura / nivel / tiempo de lectura, y exportación a CSV y Excel.
"""

import io
import pandas as pd
import streamlit as st
import plotly.express as px
from database.db import run_query


def _dataframe_resultados():
    filas = run_query(
        """SELECT e.nombres, e.apellidos, e.edad, e.especializacion,
                  e.tiempo_lectura_diario, a.nombre AS asignatura,
                  r.promedio_pretest, r.promedio_postest,
                  r.diferencia_absoluta, r.incremento_porcentual,
                  r.nivel_adaptacion, r.fecha_calculo
           FROM resultados r
           JOIN estudiantes e ON r.id_estudiante = e.id_estudiante
           JOIN asignaturas a ON r.id_asignatura = a.id_asignatura
           ORDER BY r.fecha_calculo DESC""",
        fetch=True,
    )
    return pd.DataFrame(filas)


def _exportar_botones(df, nombre_archivo):
    col1, col2 = st.columns(2)
    with col1:
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Exportar CSV", csv_bytes, file_name=f"{nombre_archivo}.csv",
            mime="text/csv", use_container_width=True,
        )
    with col2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Resultados")
        st.download_button(
            "⬇️ Exportar Excel", buffer.getvalue(), file_name=f"{nombre_archivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


def pantalla_dashboard():
    st.title("📊 Dashboard administrativo")

    total_estudiantes = run_query(
        "SELECT COUNT(*) AS total FROM estudiantes", fetch_one=True
    )["total"]
    prom_pre = run_query("SELECT AVG(promedio_pretest) AS v FROM resultados", fetch_one=True)["v"] or 0
    prom_post = run_query("SELECT AVG(promedio_postest) AS v FROM resultados", fetch_one=True)["v"] or 0
    incremento = ((prom_post - prom_pre) / prom_pre * 100) if prom_pre else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total estudiantes", total_estudiantes)
    c2.metric("Promedio general pretest", f"{float(prom_pre):.2f}")
    c3.metric("Promedio general postest", f"{float(prom_post):.2f}")
    c4.metric("Incremento porcentual", f"{incremento:.1f}%")

    df = _dataframe_resultados()
    if df.empty:
        st.info("Aún no hay resultados registrados por los estudiantes.")
        return

    st.divider()
    st.subheader("Resultados por asignatura")
    resumen_asignatura = df.groupby("asignatura")[["promedio_pretest", "promedio_postest"]].mean().reset_index()
    fig1 = px.bar(
        resumen_asignatura, x="asignatura", y=["promedio_pretest", "promedio_postest"],
        barmode="group", labels={"value": "Calificación", "variable": "Fase"},
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Resultados por nivel de adaptación")
    resumen_nivel = df.groupby("nivel_adaptacion")["incremento_porcentual"].mean().reset_index()
    fig2 = px.bar(resumen_nivel, x="nivel_adaptacion", y="incremento_porcentual",
                  labels={"incremento_porcentual": "Incremento % promedio"})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Resultados por tiempo de lectura diario")
    resumen_tiempo = df.groupby("tiempo_lectura_diario")["incremento_porcentual"].mean().reset_index()
    fig3 = px.bar(resumen_tiempo, x="tiempo_lectura_diario", y="incremento_porcentual",
                  labels={"incremento_porcentual": "Incremento % promedio"})
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.subheader("Tabla completa de resultados")
    st.dataframe(df, use_container_width=True)
    _exportar_botones(df, "resultados_investigacion")
