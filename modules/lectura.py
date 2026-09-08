"""
modules/lectura.py
--------------------
Módulo de lectura científica: presenta el texto oficial de pretest de la
asignatura seleccionada junto con un panel lateral de conceptos clave y
la sección multimedia (video + infografía), tal como definido en el
esquema PRETEST -> ADAPTACIÓN IA -> POSTEST -> ENCUESTA.
"""

import streamlit as st
from database.db import run_query
from modules.utils import iniciar_cronometro


def obtener_texto_pretest(nombre_asignatura):
    return run_query(
        """SELECT t.id_texto, t.titulo, t.contenido
           FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura
           WHERE a.nombre = %s AND t.tipo = 'pretest' LIMIT 1""",
        (nombre_asignatura,),
        fetch_one=True,
    )


def _panel_conceptos(id_texto):
    conceptos = run_query(
        "SELECT concepto, definicion, ejemplo, aplicacion FROM conceptos_clave WHERE id_texto = %s",
        (id_texto,),
        fetch=True,
    )
    st.markdown("#### 🧠 Conceptos clave")
    if not conceptos:
        st.info("Sin conceptos registrados para este texto.")
        return
    for c in conceptos:
        with st.expander(f"📌 {c['concepto']}"):
            st.markdown(f"**Definición:** {c['definicion']}")
            st.markdown(f"**Ejemplo:** {c['ejemplo']}")
            st.markdown(f"**Aplicación:** {c['aplicacion']}")


def _seccion_multimedia(id_texto):
    st.markdown("#### 🎬 Recursos multimedia")
    video = run_query(
        "SELECT url_embed, titulo FROM videos WHERE id_texto = %s LIMIT 1", (id_texto,), fetch_one=True
    )
    infografia = run_query(
        "SELECT url, descripcion FROM infografias WHERE id_texto = %s LIMIT 1", (id_texto,), fetch_one=True
    )
    col_v, col_i = st.columns(2)
    with col_v:
        if video:
            st.caption(video["titulo"])
            st.video(video["url_embed"])
    with col_i:
        if infografia:
            st.caption(infografia["descripcion"])
            #st.image(infografia["url"], use_container_width=True)
            st.image(infografia["url"], use_column_width=True)


def pantalla_lectura(nombre_asignatura):
    st.title(f"📖 Lectura científica: {nombre_asignatura}")
    texto = obtener_texto_pretest(nombre_asignatura)
    if not texto:
        st.error("No hay un texto de pretest configurado para esta asignatura.")
        return None

    col_texto, col_panel = st.columns([2.2, 1])
    with col_texto:
        st.subheader(texto["titulo"])
        st.write(texto["contenido"])
        _seccion_multimedia(texto["id_texto"])
    with col_panel:
        _panel_conceptos(texto["id_texto"])

    st.divider()
    if st.button("📝 Realizar evaluación", type="primary", use_container_width=True):
        iniciar_cronometro()
        st.session_state.pagina_actual = "pretest"
        st.rerun()
    return texto
