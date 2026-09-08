"""
modules/admin_crud.py
------------------------
Operaciones CRUD del administrador: estudiantes, textos, preguntas/opciones,
imágenes, videos e infografías. También permite ver resultados pretest/postest.
"""

import pandas as pd
import streamlit as st
from database.db import run_query
from config import ASIGNATURAS


def _crud_estudiantes():
    st.subheader("👩‍🎓 Estudiantes")
    estudiantes = run_query(
        """SELECT e.id_estudiante, u.cedula, e.nombres, e.apellidos, e.edad,
                  e.especializacion, e.tiempo_lectura_diario, u.estado
           FROM estudiantes e JOIN usuarios u ON e.id_usuario = u.id_usuario""",
        fetch=True,
    )
    df = pd.DataFrame(estudiantes)
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.markdown("#### Cambiar estado de un estudiante")
        seleccion = st.selectbox(
            "Estudiante", df["id_estudiante"],
            format_func=lambda i: df.loc[df.id_estudiante == i, "nombres"].values[0]
            + " " + df.loc[df.id_estudiante == i, "apellidos"].values[0],
        )
        nuevo_estado = st.selectbox("Nuevo estado", ["activo", "inactivo"])
        if st.button("Actualizar estado"):
            run_query(
                """UPDATE usuarios u JOIN estudiantes e ON u.id_usuario = e.id_usuario
                   SET u.estado = %s WHERE e.id_estudiante = %s""",
                (nuevo_estado, seleccion), commit=True,
            )
            st.success("Estado actualizado.")
            st.rerun()

        st.markdown("#### Eliminar estudiante")
        eliminar_id = st.selectbox(
            "Seleccionar para eliminar", df["id_estudiante"], key="del_estudiante"
        )
        if st.button("🗑️ Eliminar estudiante definitivamente", type="secondary"):
            run_query(
                """DELETE u FROM usuarios u JOIN estudiantes e ON u.id_usuario = e.id_usuario
                   WHERE e.id_estudiante = %s""",
                (eliminar_id,), commit=True,
            )
            st.success("Estudiante eliminado.")
            st.rerun()


def _crud_textos():
    st.subheader("📚 Textos científicos")
    asignatura = st.selectbox("Asignatura", ASIGNATURAS, key="txt_asignatura")
    id_asignatura = run_query(
        "SELECT id_asignatura FROM asignaturas WHERE nombre=%s", (asignatura,), fetch_one=True
    )["id_asignatura"]

    textos = run_query(
        "SELECT id_texto, titulo, tipo, nivel FROM textos WHERE id_asignatura=%s ORDER BY id_texto DESC",
        (id_asignatura,), fetch=True,
    )
    st.dataframe(pd.DataFrame(textos), use_container_width=True)

    with st.expander("➕ Agregar nuevo texto de pretest"):
        titulo = st.text_input("Título", key="nuevo_titulo_texto")
        contenido = st.text_area("Contenido", height=200, key="nuevo_contenido_texto")
        if st.button("Guardar texto"):
            if titulo and contenido:
                run_query(
                    "INSERT INTO textos (id_asignatura, titulo, contenido, tipo) VALUES (%s,%s,%s,'pretest')",
                    (id_asignatura, titulo, contenido), commit=True,
                )
                st.success("Texto agregado.")
                st.rerun()
            else:
                st.error("Complete título y contenido.")

    if textos:
        st.markdown("#### Eliminar texto")
        id_borrar = st.selectbox(
            "Seleccionar texto", [t["id_texto"] for t in textos],
            format_func=lambda i: next(t["titulo"] for t in textos if t["id_texto"] == i),
        )
        if st.button("🗑️ Eliminar texto seleccionado"):
            run_query("DELETE FROM textos WHERE id_texto=%s", (id_borrar,), commit=True)
            st.success("Texto eliminado.")
            st.rerun()


def _crud_preguntas():
    st.subheader("❓ Preguntas y opciones")
    asignatura = st.selectbox("Asignatura", ASIGNATURAS, key="preg_asignatura")
    fase = st.selectbox("Fase", ["pretest", "postest"], key="preg_fase")
    id_asignatura = run_query(
        "SELECT id_asignatura FROM asignaturas WHERE nombre=%s", (asignatura,), fetch_one=True
    )["id_asignatura"]

    preguntas = run_query(
        "SELECT id_pregunta, enunciado, tipo FROM preguntas WHERE id_asignatura=%s AND fase=%s",
        (id_asignatura, fase), fetch=True,
    )
    for p in preguntas:
        opciones = run_query(
            "SELECT texto_opcion, es_correcta FROM opciones WHERE id_pregunta=%s", (p["id_pregunta"],), fetch=True
        )
        with st.expander(f"#{p['id_pregunta']} · {p['enunciado'][:70]}"):
            for o in opciones:
                marca = "✅" if o["es_correcta"] else "▫️"
                st.write(f"{marca} {o['texto_opcion']}")
            if st.button("🗑️ Eliminar pregunta", key=f"del_preg_{p['id_pregunta']}"):
                run_query("DELETE FROM preguntas WHERE id_pregunta=%s", (p["id_pregunta"],), commit=True)
                st.success("Pregunta eliminada.")
                st.rerun()

    with st.expander("➕ Agregar nueva pregunta (opción múltiple, 4 opciones)"):
        enunciado = st.text_input("Enunciado", key="nuevo_enunciado")
        tipo = st.selectbox("Tipo", ["opcion_multiple", "verdadero_falso"], key="nuevo_tipo")
        opciones_texto = []
        correcta_idx = None
        num_opciones = 2 if tipo == "verdadero_falso" else 4
        for i in range(num_opciones):
            opciones_texto.append(st.text_input(f"Opción {i+1}", key=f"opcion_{i}"))
        correcta_idx = st.number_input(
            "Índice de la opción correcta (empezando en 1)", min_value=1, max_value=num_opciones, step=1
        )
        if st.button("Guardar pregunta"):
            if enunciado and all(opciones_texto):
                id_pregunta = run_query(
                    "INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo) VALUES (%s,%s,%s,%s)",
                    (id_asignatura, fase, enunciado, tipo), commit=True,
                )
                for i, texto_opcion in enumerate(opciones_texto, start=1):
                    run_query(
                        "INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES (%s,%s,%s)",
                        (id_pregunta, texto_opcion, i == correcta_idx), commit=True,
                    )
                st.success("Pregunta agregada.")
                st.rerun()
            else:
                st.error("Complete el enunciado y todas las opciones.")


def _crud_multimedia():
    st.subheader("🖼️ Imágenes, videos e infografías")
    asignatura = st.selectbox("Asignatura", ASIGNATURAS, key="mm_asignatura")
    textos = run_query(
        """SELECT t.id_texto, t.titulo FROM textos t JOIN asignaturas a ON t.id_asignatura=a.id_asignatura
           WHERE a.nombre=%s""",
        (asignatura,), fetch=True,
    )
    if not textos:
        st.warning("No hay textos para esta asignatura.")
        return
    id_texto = st.selectbox(
        "Texto asociado", [t["id_texto"] for t in textos],
        format_func=lambda i: next(t["titulo"] for t in textos if t["id_texto"] == i),
    )

    tab_img, tab_video, tab_info = st.tabs(["Imágenes", "Videos", "Infografías"])
    with tab_img:
        url = st.text_input("URL de la imagen", key="img_url")
        desc = st.text_input("Descripción", key="img_desc")
        if st.button("Agregar imagen"):
            run_query("INSERT INTO imagenes (id_texto, url, descripcion) VALUES (%s,%s,%s)",
                       (id_texto, url, desc), commit=True)
            st.success("Imagen agregada.")
        imagenes = run_query("SELECT * FROM imagenes WHERE id_texto=%s", (id_texto,), fetch=True)
        st.dataframe(pd.DataFrame(imagenes), use_container_width=True)

    with tab_video:
        url = st.text_input("URL embed del video", key="video_url")
        titulo = st.text_input("Título del video", key="video_titulo")
        if st.button("Agregar video"):
            run_query("INSERT INTO videos (id_texto, url_embed, titulo) VALUES (%s,%s,%s)",
                       (id_texto, url, titulo), commit=True)
            st.success("Video agregado.")
        videos = run_query("SELECT * FROM videos WHERE id_texto=%s", (id_texto,), fetch=True)
        st.dataframe(pd.DataFrame(videos), use_container_width=True)

    with tab_info:
        url = st.text_input("URL de la infografía", key="info_url")
        desc = st.text_input("Descripción", key="info_desc")
        if st.button("Agregar infografía"):
            run_query("INSERT INTO infografias (id_texto, url, descripcion) VALUES (%s,%s,%s)",
                       (id_texto, url, desc), commit=True)
            st.success("Infografía agregada.")
        infografias = run_query("SELECT * FROM infografias WHERE id_texto=%s", (id_texto,), fetch=True)
        st.dataframe(pd.DataFrame(infografias), use_container_width=True)


def _ver_resultados():
    st.subheader("📈 Resultados pretest y postest")
    pretest = run_query(
        """SELECT e.nombres, e.apellidos, a.nombre AS asignatura, p.calificacion, p.tiempo_segundos, p.fecha
           FROM pretest p JOIN estudiantes e ON p.id_estudiante=e.id_estudiante
           JOIN asignaturas a ON p.id_asignatura=a.id_asignatura ORDER BY p.fecha DESC""",
        fetch=True,
    )
    postest = run_query(
        """SELECT e.nombres, e.apellidos, a.nombre AS asignatura, po.nivel_adaptacion,
                  po.calificacion, po.tiempo_segundos, po.fecha
           FROM postest po JOIN estudiantes e ON po.id_estudiante=e.id_estudiante
           JOIN asignaturas a ON po.id_asignatura=a.id_asignatura ORDER BY po.fecha DESC""",
        fetch=True,
    )
    st.markdown("**Pretest**")
    st.dataframe(pd.DataFrame(pretest), use_container_width=True)
    st.markdown("**Postest**")
    st.dataframe(pd.DataFrame(postest), use_container_width=True)


def pantalla_admin_crud():
    st.title("⚙️ Administración del sistema")
    tabs = st.tabs(["Estudiantes", "Textos", "Preguntas", "Multimedia", "Resultados"])
    with tabs[0]:
        _crud_estudiantes()
    with tabs[1]:
        _crud_textos()
    with tabs[2]:
        _crud_preguntas()
    with tabs[3]:
        _crud_multimedia()
    with tabs[4]:
        _ver_resultados()
