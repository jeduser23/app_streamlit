-- =============================================================================
-- seed.sql
-- Datos iniciales: roles, usuario administrador, asignaturas, textos oficiales
-- de pretest y banco de preguntas base.
-- Ejecutar DESPUÉS de schema.sql:  mysql -u root -p adaptacion_ia_db < seed.sql
-- =============================================================================
USE adaptacion_ia_db;

-- -----------------------------------------------------------------------------
-- ROLES
-- -----------------------------------------------------------------------------
INSERT INTO roles (nombre_rol) VALUES ('Administrador'), ('Estudiante')
    ON DUPLICATE KEY UPDATE nombre_rol = VALUES(nombre_rol);

-- -----------------------------------------------------------------------------
-- USUARIO ADMINISTRADOR
-- Usuario: admin  /  Contraseña: Admin123!  (hash bcrypt pre-generado)
-- -----------------------------------------------------------------------------
INSERT INTO usuarios (cedula, password_hash, id_rol, estado)
SELECT 'admin', '$2b$12$YEtLcdWrGsNwv4qfBhmsBev64oQFuqJuXtSAiOW0Lxp2Nopr2qI92',
       (SELECT id_rol FROM roles WHERE nombre_rol = 'Administrador'), 'activo'
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE cedula = 'admin');

-- -----------------------------------------------------------------------------
-- ASIGNATURAS
-- -----------------------------------------------------------------------------
INSERT INTO asignaturas (nombre) VALUES ('Matemáticas'), ('Física'), ('Química')
    ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- -----------------------------------------------------------------------------
-- TEXTOS CIENTÍFICOS OFICIALES (PRETEST) - proporcionados por el investigador
-- -----------------------------------------------------------------------------
INSERT INTO textos (id_asignatura, titulo, contenido, tipo)
SELECT id_asignatura, 'La derivada de una función en un punto', 'El cálculo diferencial representa una de las herramientas más potentes del análisis matemático moderno, esencial para el estudio de la variación en fenómenos científicos y socioeconómicos. Dentro de esta rama, el concepto de la derivada de una función en un punto específico constituye la piedra angular para comprender la dinámica del cambio instantáneo y la evolución local de las variables.\n\nCon base en el texto oficial de Matemática de tercer año de Bachillerato General Unificado, la derivada de una función f(x) en un punto de abscisa x0 se define analíticamente mediante un proceso de límite. Formalmente, corresponde al límite del cociente incremental cuando el incremento de la variable independiente tiende a cero. Desde una perspectiva puramente geométrica, este valor numérico representa la pendiente exacta de la recta tangente a la curva de la función en el punto coordenado (x0, f(x0)). Si este límite existe de manera única y finita, se afirma con rigor que la función es derivable en dicho punto. Esta noción es crucial para modelar situaciones de la vida real, permitiendo calcular magnitudes complejas como la velocidad instantánea de un móvil o la tasa de crecimiento óptimo de una población.\n\nEn conclusión, la derivada en un punto unifica la geometría analítica y el concepto de límite para cuantificar el cambio exacto. Su dominio permite a los estudiantes bachilleres desarrollar el pensamiento lógico abstracto necesario para abordar modelos científicos avanzados.', 'pretest'
FROM asignaturas WHERE nombre = 'Matemáticas';

INSERT INTO textos (id_asignatura, titulo, contenido, tipo)
SELECT id_asignatura, 'Electromagnetismo: unificación de la electricidad y el magnetismo', 'El electromagnetismo representa una de las interacciones fundamentales de la física teórica y aplicada, unificando los fenómenos eléctricos y magnéticos en un único marco conceptual. Su comprensión formal revolucionó la ciencia al demostrar que la electricidad y el magnetismo no actúan de manera aislada, sino como manifestaciones dinámicas recíprocas capaces de propagarse en el espacio.\n\nCon base en el texto oficial de Física de tercer año de Bachillerato General Unificado disponible en plataformas como Calaméo, el estudio de esta disciplina profundiza en la inducción electromagnética mediante las experiencias de Michael Faraday. Bajo este principio básico, un flujo magnético variable en el tiempo a través de un circuito es capaz de inducir una fuerza electromotriz. Adicionalmente, la ley de Lenz determina que la corriente inducida poseerá un sentido tal que sus efectos magnéticos se opondrán directamente a la variación del flujo que la genera. Esta interdependencia alcanza su máxima síntesis científica en las ecuaciones de James Clerk Maxwell, las cuales unifican vectorialmente el comportamiento de los campos y predicen matemáticamente la existencia de las ondas electromagnéticas, cuya manifestación más común es la luz.\n\nEn conclusión, el electromagnetismo clásico unifica la electricidad y el magnetismo bajo un formalismo matemático riguroso. Este conocimiento capacita a los estudiantes para analizar las tecnologías modernas y comprender las leyes físicas que gobiernan el universo.', 'pretest'
FROM asignaturas WHERE nombre = 'Física';

INSERT INTO textos (id_asignatura, titulo, contenido, tipo)
SELECT id_asignatura, 'Ácidos y bases: la teoría de Lewis', 'Los ácidos y las bases constituyen dos clases de compuestos químicos fundamentales en la naturaleza, cuyas interacciones regulan múltiples fenómenos biológicos e industriales. El entendimiento de estas sustancias ha evolucionado a través de diversas teorías científicas que explican con precisión su comportamiento molecular, su reactividad en disolución y su relevancia directa en el entorno.\n\nDe acuerdo con el texto oficial de Química de tercer año de Bachillerato General Unificado disponible en Calaméo, la conceptualización moderna de estos compuestos se extiende desde los enfoques tradicionales hasta la teoría de Gilbert Lewis. Bajo esta perspectiva formal, un ácido de Lewis se define estrictamente como aquella sustancia química capaz de aceptar un par de electrones de valencia. Por el contrario, una base de Lewis se identifica como la especie química con la capacidad de donar dicho par electrónico para formar un nuevo enlace covalente coordinado. Esta interacción es crucial, ya que la disposición espacial tridimensional de los átomos resultantes determinará la geometría molecular y las propiedades físicas y químicas de las nuevas sustancias.\n\nEn conclusión, el modelo de Lewis unifica los criterios de acidez y basicidad bajo el concepto clave del intercambio electrónico, superando las limitaciones tradicionales. Este conocimiento resulta indispensable para que los estudiantes de bachillerato comprendan la reactividad y predigan la estructura de los compuestos químicos de la vida diaria.', 'pretest'
FROM asignaturas WHERE nombre = 'Química';

-- -----------------------------------------------------------------------------
-- CONCEPTOS CLAVE (panel lateral) por texto
-- -----------------------------------------------------------------------------
INSERT INTO conceptos_clave (id_texto, concepto, definicion, ejemplo, aplicacion)
SELECT t.id_texto, 'Derivada', 'Límite del cociente incremental de una función cuando el incremento tiende a cero.', 'La pendiente de la recta tangente a f(x)=x^2 en x=2 es 4.', 'Cálculo de velocidad instantánea de un vehículo.'
FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura WHERE a.nombre='Matemáticas' AND t.tipo='pretest';

INSERT INTO conceptos_clave (id_texto, concepto, definicion, ejemplo, aplicacion)
SELECT t.id_texto, 'Recta tangente', 'Línea que toca la curva en un único punto con la misma pendiente que la función en ese punto.', 'La recta tangente a una parábola en su vértice es horizontal.', 'Diseño de trayectorias y optimización.'
FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura WHERE a.nombre='Matemáticas' AND t.tipo='pretest';

INSERT INTO conceptos_clave (id_texto, concepto, definicion, ejemplo, aplicacion)
SELECT t.id_texto, 'Inducción electromagnética', 'Generación de una fuerza electromotriz por un flujo magnético variable en el tiempo.', 'Un imán moviéndose dentro de una bobina genera corriente eléctrica.', 'Funcionamiento de generadores eléctricos.'
FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura WHERE a.nombre='Física' AND t.tipo='pretest';

INSERT INTO conceptos_clave (id_texto, concepto, definicion, ejemplo, aplicacion)
SELECT t.id_texto, 'Ley de Lenz', 'La corriente inducida se opone a la variación del flujo magnético que la genera.', 'Un imán que cae dentro de un tubo de cobre se frena por la corriente inducida.', 'Frenos electromagnéticos.'
FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura WHERE a.nombre='Física' AND t.tipo='pretest';

INSERT INTO conceptos_clave (id_texto, concepto, definicion, ejemplo, aplicacion)
SELECT t.id_texto, 'Ácido de Lewis', 'Sustancia capaz de aceptar un par de electrones de valencia.', 'El BF3 acepta un par de electrones de una base de Lewis.', 'Catálisis en reacciones orgánicas.'
FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura WHERE a.nombre='Química' AND t.tipo='pretest';

INSERT INTO conceptos_clave (id_texto, concepto, definicion, ejemplo, aplicacion)
SELECT t.id_texto, 'Base de Lewis', 'Especie química capaz de donar un par de electrones para formar un enlace covalente coordinado.', 'El NH3 dona su par de electrones libre al formar NH4+.', 'Formación de complejos de coordinación.'
FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura WHERE a.nombre='Química' AND t.tipo='pretest';

-- -----------------------------------------------------------------------------
-- MULTIMEDIA DE EJEMPLO (reemplazar por URLs institucionales reales)
-- -----------------------------------------------------------------------------
INSERT INTO videos (id_texto, url_embed, titulo)
SELECT t.id_texto, 'https://www.youtube.com/embed/dQw4w9WgXcQ', CONCAT('Video introductorio: ', a.nombre)
FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura WHERE t.tipo='pretest';

INSERT INTO infografias (id_texto, url, descripcion)
SELECT t.id_texto, CONCAT('https://via.placeholder.com/600x800.png?text=Infografia+', a.nombre), CONCAT('Infografía resumen de ', a.nombre)
FROM textos t JOIN asignaturas a ON t.id_asignatura = a.id_asignatura WHERE t.tipo='pretest';

-- -----------------------------------------------------------------------------
-- BANCO DE PREGUNTAS - MATEMÁTICAS (PRETEST)
-- -----------------------------------------------------------------------------
INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', '¿Qué representa geométricamente la derivada de una función en un punto?', 'opcion_multiple' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'La pendiente de la recta tangente a la curva en ese punto', TRUE),
(@p, 'El área bajo la curva entre dos puntos', FALSE),
(@p, 'El valor máximo absoluto de la función', FALSE),
(@p, 'La distancia entre dos puntos de la curva', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'La derivada se define formalmente como el límite del cociente incremental cuando el incremento tiende a cero.', 'verdadero_falso' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'Si el límite que define la derivada existe de manera única y finita, se dice que la función es:', 'opcion_multiple' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Derivable en ese punto', TRUE),
(@p, 'Discontinua en ese punto', FALSE),
(@p, 'No acotada', FALSE),
(@p, 'Periódica', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'La derivada permite calcular la velocidad instantánea de un móvil.', 'verdadero_falso' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', '¿Qué rama del análisis matemático estudia la derivada?', 'opcion_multiple' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Cálculo diferencial', TRUE),
(@p, 'Geometría euclidiana', FALSE),
(@p, 'Estadística descriptiva', FALSE),
(@p, 'Álgebra lineal', FALSE);

-- -----------------------------------------------------------------------------
-- BANCO DE PREGUNTAS - FÍSICA (PRETEST)
-- -----------------------------------------------------------------------------
INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', '¿Quién realizó las experiencias que fundamentan la inducción electromagnética?', 'opcion_multiple' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Michael Faraday', TRUE),
(@p, 'Isaac Newton', FALSE),
(@p, 'Albert Einstein', FALSE),
(@p, 'Nikola Tesla', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'La ley de Lenz establece que la corriente inducida se opone a la variación del flujo que la genera.', 'verdadero_falso' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', '¿Qué ecuaciones unifican vectorialmente el comportamiento de los campos eléctrico y magnético?', 'opcion_multiple' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Ecuaciones de Maxwell', TRUE),
(@p, 'Ecuaciones de Newton', FALSE),
(@p, 'Ecuaciones de Schrödinger', FALSE),
(@p, 'Ecuaciones de Bernoulli', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'La luz es una de las manifestaciones más comunes de las ondas electromagnéticas.', 'verdadero_falso' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'Un flujo magnético variable en el tiempo a través de un circuito puede inducir:', 'opcion_multiple' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Una fuerza electromotriz', TRUE),
(@p, 'Una fuerza gravitacional', FALSE),
(@p, 'Una reacción química', FALSE),
(@p, 'Un cambio de temperatura ambiental', FALSE);

-- -----------------------------------------------------------------------------
-- BANCO DE PREGUNTAS - QUÍMICA (PRETEST)
-- -----------------------------------------------------------------------------
INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'Según la teoría de Lewis, un ácido se define como una sustancia capaz de:', 'opcion_multiple' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Aceptar un par de electrones de valencia', TRUE),
(@p, 'Donar protones exclusivamente', FALSE),
(@p, 'Neutralizar bases fuertes', FALSE),
(@p, 'Formar precipitados coloreados', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'Una base de Lewis dona un par de electrones para formar un enlace covalente coordinado.', 'verdadero_falso' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', '¿Quién propuso la teoría moderna de ácidos y bases basada en el intercambio electrónico?', 'opcion_multiple' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Gilbert Lewis', TRUE),
(@p, 'Svante Arrhenius', FALSE),
(@p, 'Robert Boyle', FALSE),
(@p, 'John Dalton', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'La disposición espacial de los átomos resultantes determina la geometría molecular de la nueva sustancia.', 'verdadero_falso' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'pretest', 'Los ácidos y bases regulan múltiples fenómenos:', 'opcion_multiple' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Biológicos e industriales', TRUE),
(@p, 'Exclusivamente astronómicos', FALSE),
(@p, 'Exclusivamente geológicos', FALSE),
(@p, 'Exclusivamente climáticos', FALSE);

-- -----------------------------------------------------------------------------
-- BANCO DE PREGUNTAS - POSTEST (nuevas preguntas, mismas 3 asignaturas)
-- Estas preguntas se muestran después de cada adaptación pedagógica con IA.
-- El docente/administrador puede editarlas o ampliarlas desde el CRUD.
-- -----------------------------------------------------------------------------
INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'Tras la adaptación, ¿qué elemento del texto permite calcular la pendiente en un punto?', 'opcion_multiple' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'La derivada de la función', TRUE),
(@p, 'La integral definida', FALSE),
(@p, 'El dominio de la función', FALSE),
(@p, 'La asíntota vertical', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'El concepto de límite es indispensable para definir formalmente la derivada.', 'verdadero_falso' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', '¿Qué tipo de razonamiento desarrolla el estudio de la derivada?', 'opcion_multiple' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Pensamiento lógico abstracto', TRUE),
(@p, 'Memorización mecánica', FALSE),
(@p, 'Razonamiento verbal', FALSE),
(@p, 'Percepción espacial únicamente', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'La tasa de crecimiento de una población puede modelarse usando derivadas.', 'verdadero_falso' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'La derivada en un punto unifica la geometría analítica y el concepto de:', 'opcion_multiple' FROM asignaturas WHERE nombre='Matemáticas';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Límite', TRUE),
(@p, 'Vector', FALSE),
(@p, 'Matriz', FALSE),
(@p, 'Probabilidad', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', '¿Qué ley explica el sentido de la corriente inducida frente a la variación del flujo magnético?', 'opcion_multiple' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Ley de Lenz', TRUE),
(@p, 'Ley de Ohm', FALSE),
(@p, 'Ley de Coulomb', FALSE),
(@p, 'Ley de Hooke', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'Las ecuaciones de Maxwell predicen matemáticamente la existencia de las ondas electromagnéticas.', 'verdadero_falso' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'La electricidad y el magnetismo, según el electromagnetismo clásico, son:', 'opcion_multiple' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Manifestaciones dinámicas recíprocas unificadas', TRUE),
(@p, 'Fenómenos completamente independientes', FALSE),
(@p, 'Fuerzas nucleares fuertes', FALSE),
(@p, 'Reacciones químicas exotérmicas', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'Un flujo magnético constante (que no varía en el tiempo) induce una fuerza electromotriz.', 'verdadero_falso' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', FALSE), (@p, 'Falso', TRUE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'El electromagnetismo permite comprender tecnologías modernas y leyes físicas del universo.', 'verdadero_falso' FROM asignaturas WHERE nombre='Física';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'Según el modelo de Lewis, ¿qué determina la geometría molecular de la nueva sustancia formada?', 'opcion_multiple' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'La disposición espacial tridimensional de los átomos', TRUE),
(@p, 'El color de la disolución', FALSE),
(@p, 'La temperatura ambiental', FALSE),
(@p, 'El estado físico inicial', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'El modelo de Lewis supera las limitaciones de las teorías tradicionales de ácidos y bases.', 'verdadero_falso' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'El enlace formado entre un ácido y una base de Lewis se denomina:', 'opcion_multiple' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Enlace covalente coordinado', TRUE),
(@p, 'Enlace iónico puro', FALSE),
(@p, 'Enlace metálico', FALSE),
(@p, 'Puente de hidrógeno', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'La reactividad y estructura de los compuestos químicos de la vida diaria puede predecirse con el modelo de Lewis.', 'verdadero_falso' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'Verdadero', TRUE), (@p, 'Falso', FALSE);

INSERT INTO preguntas (id_asignatura, fase, enunciado, tipo)
SELECT id_asignatura, 'postest', 'Los ácidos y bases de Lewis se explican fundamentalmente por:', 'opcion_multiple' FROM asignaturas WHERE nombre='Química';
SET @p := LAST_INSERT_ID();
INSERT INTO opciones (id_pregunta, texto_opcion, es_correcta) VALUES
(@p, 'El intercambio de pares de electrones', TRUE),
(@p, 'El intercambio de neutrones', FALSE),
(@p, 'La emisión de fotones', FALSE),
(@p, 'La fusión nuclear', FALSE);
