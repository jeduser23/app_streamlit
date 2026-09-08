"""
modules/encuesta.py
----------------------
Encuesta final: escala Likert (1-5) organizada en cuatro dimensiones, más
preguntas abiertas de usabilidad, calidad pedagógica, utilidad y confianza
en la IA.
"""

import streamlit as st
from database.db import run_query, log_action

DIMENSIONES = {
    "Dimensión pedagógica y de contenido": [
        ("calidad_adaptacion", "Calidad de la adaptación"),
        ("comprension_lectora", "Comprensión lectora"),
        ("elementos_apoyo_didactico", "Elementos de apoyo didáctico"),
        ("idoneidad_nivel", "Idoneidad del nivel"),
    ],
    "Dimensión tecnológica y UX": [
        ("facilidad_uso", "Facilidad de uso"),
        ("velocidad_respuesta", "Velocidad de respuesta"),
        ("accesibilidad_compatibilidad", "Accesibilidad y compatibilidad"),
    ],
    "Dimensión de interacción con IA": [
        ("precision_alucinaciones", "Precisión y alucinaciones"),
        ("capacidad_personalizacion", "Capacidad de personalización"),
        ("claridad_instrucciones", "Claridad de instrucciones"),
    ],
    "Dimensión afectiva": [
        ("utilidad_percibida", "Utilidad percibida"),
        ("confianza_sistema", "Confianza en el sistema"),
        ("satisfaccion_general", "Satisfacción general"),
    ],
}

PREGUNTAS_ABIERTAS = {
    "Usabilidad": [
        ("dificultades_tecnicas", "¿Qué dificultades técnicas o problemas de navegación encontraste al usar la plataforma?"),
        ("sugerencias_diseno", "¿Qué sugerencias tienes para mejorar el diseño o las funciones del sitio web?"),
    ],
    "Calidad pedagógica": [
        ("ia_omitio_informacion", "¿Consideras que la IA omitió información científica importante? Explica por qué."),
        ("ejemplo_adaptacion_ayudo", "Describe un ejemplo específico de cómo la adaptación te ayudó a comprender un concepto difícil."),
    ],
    "Utilidad": [
        ("situaciones_uso", "¿En qué situaciones académicas utilizarías esta herramienta?"),
        ("funcionalidades_adicionales", "¿Qué funcionalidades adicionales te gustaría incorporar?"),
    ],
    "Confianza en IA": [
        ("confusion_texto_adaptado", "¿Hubo alguna parte del texto adaptado que te generó confusión o pareció incorrecta?"),
    ],
}


def pantalla_encuesta(id_estudiante):
    st.title("📋 Encuesta final")
    st.caption("Escala Likert: 1 = Muy en desacuerdo · 5 = Muy de acuerdo")

    respuestas = {}
    with st.form("form_encuesta"):
        for dimension, items in DIMENSIONES.items():
            st.markdown(f"### {dimension}")
            for campo, etiqueta in items:
                respuestas[campo] = st.slider(etiqueta, 1, 5, 3, key=f"likert_{campo}")

        st.markdown("### Preguntas abiertas")
        for categoria, preguntas in PREGUNTAS_ABIERTAS.items():
            st.markdown(f"**{categoria}**")
            for campo, texto in preguntas:
                respuestas[campo] = st.text_area(texto, key=f"abierta_{campo}")

        enviado = st.form_submit_button("Enviar encuesta", type="primary", use_container_width=True)

    if enviado:
        columnas = list(respuestas.keys())
        valores = list(respuestas.values())
        placeholders = ", ".join(["%s"] * len(columnas))
        columnas_sql = ", ".join(columnas)
        actualizaciones = ", ".join([f"{c} = VALUES({c})" for c in columnas])

        run_query(
            f"""INSERT INTO encuestas (id_estudiante, {columnas_sql})
                VALUES (%s, {placeholders})
                ON DUPLICATE KEY UPDATE {actualizaciones}""",
            (id_estudiante, *valores),
            commit=True,
        )
        log_action(st.session_state.id_usuario, "encuesta_final", "Encuesta registrada")
        st.success("✅ ¡Gracias! Tu encuesta ha sido registrada. Has completado el estudio.")
        st.balloons()
