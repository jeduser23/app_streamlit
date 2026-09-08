"""
modules/evaluacion.py
------------------------
Motor genérico de evaluación (pretest y postest). Renderiza 5 preguntas
(opción múltiple / verdadero-falso), valida que todas estén respondidas,
calcula la calificación, guarda respuestas y tiempo empleado, y actualiza
el avance del estudiante.
"""

import streamlit as st
from database.db import run_query
from modules.utils import obtener_tiempo_transcurrido
from config import NUM_PREGUNTAS_EVALUACION


def obtener_preguntas(id_asignatura, fase):
    preguntas = run_query(
        """SELECT id_pregunta, enunciado, tipo FROM preguntas
           WHERE id_asignatura = %s AND fase = %s
           ORDER BY RAND() LIMIT %s""",
        (id_asignatura, fase, NUM_PREGUNTAS_EVALUACION),
        fetch=True,
    )
    for p in preguntas:
        p["opciones"] = run_query(
            "SELECT id_opcion, texto_opcion, es_correcta FROM opciones WHERE id_pregunta = %s",
            (p["id_pregunta"],),
            fetch=True,
        )
    return preguntas


_CAMPOS_AVANCE_VALIDOS = {"pretest_completado", "adaptacion_generada", "postest_completado"}


def _actualizar_avance(id_estudiante, id_asignatura, campo):
    """Actualiza una columna booleana de avance_estudiante.
    `campo` proviene únicamente de constantes internas (nunca de entrada
    del usuario), por lo que se valida contra una lista blanca antes de
    interpolarlo en el nombre de columna."""
    if campo not in _CAMPOS_AVANCE_VALIDOS:
        raise ValueError(f"Campo de avance no permitido: {campo}")
    query = (
        f"INSERT INTO avance_estudiante (id_estudiante, id_asignatura, {campo}) "
        f"VALUES (%s, %s, TRUE) "
        f"ON DUPLICATE KEY UPDATE {campo} = TRUE"
    )
    run_query(query, (id_estudiante, id_asignatura), commit=True)


def render_evaluacion(nombre_asignatura, id_asignatura, fase, nivel_adaptacion=None):
    """
    fase: 'pretest' | 'postest'
    Retorna True cuando la evaluación fue enviada y calificada con éxito.

    IMPORTANTE: una vez calificada, el resultado se guarda en
    `st.session_state[clave_resultado]`. Esto es necesario porque el botón
    "Continuar" (en pretest.py/postest.py) vive en la misma página: al hacer
    clic en él, Streamlit vuelve a ejecutar `pantalla_pretest`/`pantalla_postest`
    ANTES de procesar la navegación, lo que volvería a invocar esta función.
    Sin este resultado guardado, aquí se generaría un formulario nuevo y vacío
    (porque las preguntas cacheadas ya se habían borrado), `enviado` sería
    False, la función devolvería False, y el botón "Continuar" nunca llegaría
    a crearse en ese rerun -> el clic se perdía y volvía a verse la evaluación.
    """
    clave_preguntas = f"preguntas_{fase}_{id_asignatura}"
    clave_resultado = f"resultado_{fase}_{id_asignatura}"

    # La evaluación ya fue enviada y calificada: mostrar el resultado guardado
    # sin volver a generar el formulario ni a recalcular nada.
    if clave_resultado in st.session_state:
        resultado = st.session_state[clave_resultado]
        st.title(f"🧪 {'Pretest' if fase == 'pretest' else 'Postest'}: {nombre_asignatura}")
        st.success(
            f"✅ Puntaje: {resultado['calificacion']} / 10  |  "
            f"⏱️ Tiempo empleado: {resultado['tiempo']} segundos"
        )
        return True

    if clave_preguntas not in st.session_state:
        st.session_state[clave_preguntas] = obtener_preguntas(id_asignatura, fase)
    preguntas = st.session_state[clave_preguntas]

    if not preguntas:
        st.warning(f"No hay preguntas de {fase} configuradas para {nombre_asignatura}.")
        return False

    st.title(f"🧪 {'Pretest' if fase == 'pretest' else 'Postest'}: {nombre_asignatura}")
    st.caption("Todas las preguntas son obligatorias.")

    respuestas_usuario = {}
    with st.form(f"form_{fase}_{id_asignatura}"):
        for idx, p in enumerate(preguntas, start=1):
            st.markdown(f"**{idx}. {p['enunciado']}**")
            opciones_texto = [o["texto_opcion"] for o in p["opciones"]]
            seleccion = st.radio(
                "Seleccione una opción:",
                opciones_texto,
                index=None,
                key=f"resp_{fase}_{p['id_pregunta']}",
                label_visibility="collapsed",
            )
            respuestas_usuario[p["id_pregunta"]] = seleccion
            st.write("")
        enviado = st.form_submit_button("Enviar evaluación", type="primary", use_container_width=True)

    if not enviado:
        return False

    if any(v is None for v in respuestas_usuario.values()):
        st.error("⚠️ Debe responder todas las preguntas.")
        return False

    tiempo = obtener_tiempo_transcurrido()
    correctas = 0
    detalle_respuestas = []
    for p in preguntas:
        seleccion_texto = respuestas_usuario[p["id_pregunta"]]
        opcion_elegida = next(o for o in p["opciones"] if o["texto_opcion"] == seleccion_texto)
        if opcion_elegida["es_correcta"]:
            correctas += 1
        detalle_respuestas.append((p["id_pregunta"], opcion_elegida["id_opcion"], opcion_elegida["es_correcta"]))

    calificacion = round((correctas / len(preguntas)) * 10, 2)  # escala 0-10
    id_estudiante = st.session_state.id_estudiante

    if fase == "pretest":
        id_intento = run_query(
            """INSERT INTO pretest (id_estudiante, id_asignatura, calificacion, tiempo_segundos)
               VALUES (%s, %s, %s, %s)""",
            (id_estudiante, id_asignatura, calificacion, tiempo),
            commit=True,
        )
        _actualizar_avance(id_estudiante, id_asignatura, "pretest_completado")
    else:
        id_intento = run_query(
            """INSERT INTO postest (id_estudiante, id_asignatura, nivel_adaptacion, calificacion, tiempo_segundos)
               VALUES (%s, %s, %s, %s, %s)""",
            (id_estudiante, id_asignatura, nivel_adaptacion, calificacion, tiempo),
            commit=True,
        )
        _actualizar_avance(id_estudiante, id_asignatura, "postest_completado")

    for id_pregunta, id_opcion, es_correcta in detalle_respuestas:
        run_query(
            """INSERT INTO respuestas (fase, id_intento, id_pregunta, id_opcion_elegida, es_correcta)
               VALUES (%s, %s, %s, %s, %s)""",
            (fase, id_intento, id_pregunta, id_opcion, es_correcta),
            commit=True,
        )

    st.session_state[clave_resultado] = {"calificacion": calificacion, "tiempo": tiempo}
    del st.session_state[clave_preguntas]

    st.success(f"✅ Puntaje: {calificacion} / 10  |  ⏱️ Tiempo empleado: {tiempo} segundos")
    return True
