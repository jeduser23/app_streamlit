# Sistema Web con IA para la Adaptación Pedagógica de Textos Científicos

MVP funcional para la investigación académica *"Sistema Web con Inteligencia
Artificial para la Adaptación Pedagógica de Textos Científicos en Estudiantes
de Tercer Año de Bachillerato"*.

Flujo implementado: **Login/Registro → Selección de asignatura → Lectura
científica → Pretest → Adaptación Pedagógica con IA (Gemini) → Postest →
Resultados comparativos → Encuesta final**, con Dashboard y CRUD para el
administrador.

Stack: **Streamlit (frontend) + Python (backend) + MySQL (persistencia) +
Google AI Studio / Gemini API (IA)**. No se usa React, Angular, Vue, PHP,
Node.js, Laravel ni Django.

---

## 1. Requisitos previos

- Python 3.10 o superior
- MySQL 8.x (o MariaDB 10.6+) en ejecución
- Una clave de API de Google AI Studio: https://aistudio.google.com/app/apikey

## 2. Instalación

```bash
# 1. Clonar / descomprimir el proyecto y ubicarse en la carpeta
cd adaptacion_ia

# 2. Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## 3. Configurar variables de entorno

Copie `.env.example` a `.env` y complete sus credenciales reales:

```bash
cp .env.example .env
```

Edite `.env`:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=su_password_mysql
DB_NAME=adaptacion_ia_db

GEMINI_API_KEY=su_clave_de_google_ai_studio
GEMINI_MODEL=gemini-1.5-flash

APP_SECRET=una_clave_secreta_propia
```

## 4. Crear la base de datos

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

Esto crea la base `adaptacion_ia_db`, todas las tablas con integridad
referencial, el usuario administrador (`admin` / `Admin123!`), las tres
asignaturas, los textos científicos oficiales de pretest, los conceptos
clave, multimedia de ejemplo y el banco de 30 preguntas (5 pretest + 5
postest por asignatura).

> **Nota:** los datos de `videos`/`infografias` insertados por `seed.sql`
> son URLs de ejemplo. Reemplácelas desde el módulo de administración
> (CRUD → Multimedia) por los recursos reales de la institución.

## 5. Ejecutar la aplicación

```bash
streamlit run app.py
```

Abra el navegador en `http://localhost:8501`.

## 6. Credenciales de acceso

| Rol | Usuario (cédula) | Contraseña |
|---|---|---|
| Administrador | `admin` | `Admin123!` |
| Estudiante | (cédula registrada) | (definida en el registro) |

## 7. Estructura del proyecto

```
adaptacion_ia/
├── app.py                     # Punto de entrada (streamlit run app.py)
├── config.py                  # Configuración central (.env, prompt IA, constantes)
├── requirements.txt
├── .env.example
├── database/
│   ├── schema.sql              # DDL: tablas, PK/FK, índices, checks
│   ├── seed.sql                # Datos iniciales (admin, textos, preguntas)
│   └── db.py                   # Pool de conexiones y helper de queries
└── modules/
    ├── utils.py                 # Hash de contraseñas, sesión, cronómetro
    ├── auth.py                  # Registro y login
    ├── principal.py             # Selección de asignatura / control de avance
    ├── lectura.py                # Texto + conceptos clave + multimedia
    ├── evaluacion.py              # Motor genérico de evaluación (5 preguntas)
    ├── pretest.py / postest.py     # Wrappers del motor de evaluación
    ├── adaptacion_ia.py             # Integración con Gemini API (google-genai)
    ├── resultados.py                 # Gráficos comparativos (Plotly)
    ├── encuesta.py                    # Encuesta final Likert + abiertas
    ├── dashboard.py                    # Dashboard administrativo + exportación
    └── admin_crud.py                    # CRUD de estudiantes/textos/preguntas/multimedia
```

## 8. Notas técnicas

- Las contraseñas se almacenan cifradas con **bcrypt** (nunca en texto plano).
- La integración de IA usa el SDK vigente **`google-genai`** (el paquete
  anterior `google-generativeai` está deprecado por Google).
- El prompt enviado a Gemini es exactamente el definido por el investigador
  (218-220 palabras, conceptos clave / ejemplo práctico / resumen final,
  ajustado según el nivel Básico/Medio/Avanzado). La respuesta se solicita
  en JSON estricto para garantizar un parseo confiable.
- El control de avance (`avance_estudiante`) impide repetir una asignatura
  ya completada y solo permite continuar con las pendientes, tal como
  especifica el esquema PRETEST → ADAPTACIÓN IA → POSTEST.
- Los resultados comparativos (promedio, diferencia absoluta, incremento
  porcentual) se calculan y persisten en la tabla `resultados` antes de
  pasar a la encuesta final.
- El dashboard exporta a **CSV** y **Excel** (openpyxl) directamente desde
  Streamlit.

## 9. Despliegue en Streamlit Community Cloud

La app también puede subirse a https://share.streamlit.io sin modificar el
código. Solo hay dos cosas que cambian respecto a correrla en local:

1. **MySQL debe ser accesible desde internet.** Streamlit Cloud no aloja
   bases de datos, así que se necesita un MySQL externo alcanzable por
   host/puerto (por ejemplo PlanetScale, Railway, un RDS de AWS, Aiven, o
   cualquier hosting MySQL con acceso remoto). Localhost no sirve aquí.
2. **Las credenciales van en `st.secrets`, no en `.env`.** El repositorio
   NUNCA debe incluir el `.env` real con contraseñas. En su lugar:
   - Suba el proyecto a un repositorio de GitHub (puede excluir `.env`
     con un `.gitignore`, dejando solo `.env.example` como referencia).
   - En share.streamlit.io, cree la app apuntando a `app.py` como archivo
     principal.
   - En **Settings → Secrets** de la app, pegue algo como:
     ```toml
     DB_HOST = "su-host-mysql-remoto.com"
     DB_PORT = "3306"
     DB_USER = "usuario"
     DB_PASSWORD = "password"
     DB_NAME = "adaptacion_ia_db"
     GEMINI_API_KEY = "su_clave_de_google_ai_studio"
     GEMINI_MODEL = "gemini-1.5-flash"
     APP_SECRET = "una_clave_secreta_propia"
     ```
   `config.py` ya está preparado para leer primero de `st.secrets` y,
   si no encuentra la clave allí (por ejemplo en su máquina local sin
   `secrets.toml`), recurre automáticamente a `.env` — no requiere tocar
   nada más.
3. Ejecute `schema.sql` y `seed.sql` una sola vez contra ese MySQL remoto
   (desde su máquina local, con un cliente MySQL apuntando al host
   remoto) antes de abrir la app en la nube.

**Limitaciones a tener en cuenta en el plan gratuito de Streamlit Cloud:**
la app "duerme" tras un período de inactividad (se reactiva al primer
acceso), y hay límites de recursos (CPU/RAM) que normalmente son
suficientes para un piloto de 15-30 estudiantes, pero conviene probarlo
con antelación a la aplicación real.

## 10. Piloto de investigación

El sistema está listo para la prueba piloto con 15 estudiantes y la
evaluación ampliada con 30 estudiantes: cada estudiante se registra con su
cédula, completa el ciclo para las tres asignaturas y su información queda
disponible para el análisis estadístico en el Dashboard administrativo
(exportable a CSV/Excel para su procesamiento en SPSS, Excel u otra
herramienta estadística).
