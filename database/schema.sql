-- =============================================================================
-- schema.sql
-- Sistema Web con IA para la Adaptación Pedagógica de Textos Científicos
-- Motor: MySQL 8.x
-- =============================================================================

CREATE DATABASE IF NOT EXISTS adaptacion_ia_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE adaptacion_ia_db;

-- -----------------------------------------------------------------------------
-- ROLES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id_rol      INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol  VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- USUARIOS  (tabla base de autenticación, usada por admin y estudiantes)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario          INT AUTO_INCREMENT PRIMARY KEY,
    cedula              VARCHAR(20) NOT NULL UNIQUE,
    password_hash       VARCHAR(255) NOT NULL,
    id_rol              INT NOT NULL,
    estado              ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
    fecha_registro      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hora_registro       TIME NOT NULL DEFAULT (CURRENT_TIME),
    fecha_ultima_conexion DATETIME NULL,
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_usuarios_cedula (cedula)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- ESTUDIANTES  (datos extendidos de registro, 1:1 con usuarios)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estudiantes (
    id_estudiante       INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario          INT NOT NULL UNIQUE,
    nombres             VARCHAR(100) NOT NULL,
    apellidos           VARCHAR(100) NOT NULL,
    edad                TINYINT UNSIGNED NOT NULL,
    especializacion     VARCHAR(100) NOT NULL,
    tiempo_lectura_diario VARCHAR(20) NOT NULL,
    CONSTRAINT fk_estudiantes_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- ASIGNATURAS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS asignaturas (
    id_asignatura   INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- TEXTOS CIENTÍFICOS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS textos (
    id_texto        INT AUTO_INCREMENT PRIMARY KEY,
    id_asignatura   INT NOT NULL,
    titulo          VARCHAR(150) NOT NULL,
    contenido       MEDIUMTEXT NOT NULL,
    tipo            ENUM('pretest','adaptado') NOT NULL DEFAULT 'pretest',
    nivel           ENUM('Básico','Medio','Avanzado') NULL,
    fecha_creacion  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_textos_asignatura FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_textos_asignatura (id_asignatura)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- CONCEPTOS CLAVE (panel lateral: concepto | definición | ejemplo | aplicación)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conceptos_clave (
    id_concepto     INT AUTO_INCREMENT PRIMARY KEY,
    id_texto        INT NOT NULL,
    concepto        VARCHAR(150) NOT NULL,
    definicion      TEXT NOT NULL,
    ejemplo         TEXT NOT NULL,
    aplicacion      TEXT NOT NULL,
    CONSTRAINT fk_conceptos_texto FOREIGN KEY (id_texto) REFERENCES textos(id_texto)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- IMÁGENES / VIDEOS / INFOGRAFÍAS (multimedia asociada a un texto)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS imagenes (
    id_imagen   INT AUTO_INCREMENT PRIMARY KEY,
    id_texto    INT NOT NULL,
    url         VARCHAR(500) NOT NULL,
    descripcion VARCHAR(255),
    CONSTRAINT fk_imagenes_texto FOREIGN KEY (id_texto) REFERENCES textos(id_texto)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS videos (
    id_video    INT AUTO_INCREMENT PRIMARY KEY,
    id_texto    INT NOT NULL,
    url_embed   VARCHAR(500) NOT NULL,
    titulo      VARCHAR(150),
    CONSTRAINT fk_videos_texto FOREIGN KEY (id_texto) REFERENCES textos(id_texto)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS infografias (
    id_infografia INT AUTO_INCREMENT PRIMARY KEY,
    id_texto      INT NOT NULL,
    url           VARCHAR(500) NOT NULL,
    descripcion   VARCHAR(255),
    CONSTRAINT fk_infografias_texto FOREIGN KEY (id_texto) REFERENCES textos(id_texto)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- PREGUNTAS Y OPCIONES  (banco de preguntas por asignatura y por fase)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS preguntas (
    id_pregunta     INT AUTO_INCREMENT PRIMARY KEY,
    id_asignatura   INT NOT NULL,
    fase            ENUM('pretest','postest') NOT NULL,
    enunciado       TEXT NOT NULL,
    tipo            ENUM('opcion_multiple','verdadero_falso') NOT NULL,
    CONSTRAINT fk_preguntas_asignatura FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_preguntas_asignatura_fase (id_asignatura, fase)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS opciones (
    id_opcion       INT AUTO_INCREMENT PRIMARY KEY,
    id_pregunta     INT NOT NULL,
    texto_opcion    VARCHAR(255) NOT NULL,
    es_correcta     BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_opciones_pregunta FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- PRETEST / POSTEST (encabezado de un intento de evaluación)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pretest (
    id_pretest      INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante   INT NOT NULL,
    id_asignatura   INT NOT NULL,
    calificacion    DECIMAL(5,2) NOT NULL,
    tiempo_segundos INT NOT NULL,
    fecha           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pretest_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_pretest_asignatura FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_pretest_estudiante (id_estudiante)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS postest (
    id_postest      INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante   INT NOT NULL,
    id_asignatura   INT NOT NULL,
    nivel_adaptacion ENUM('Básico','Medio','Avanzado') NOT NULL,
    calificacion    DECIMAL(5,2) NOT NULL,
    tiempo_segundos INT NOT NULL,
    fecha           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_postest_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_postest_asignatura FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_postest_estudiante (id_estudiante)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- RESPUESTAS  (detalle de cada pregunta respondida en pretest/postest)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS respuestas (
    id_respuesta    INT AUTO_INCREMENT PRIMARY KEY,
    fase            ENUM('pretest','postest') NOT NULL,
    id_intento      INT NOT NULL,          -- referencia a id_pretest o id_postest según 'fase'
    id_pregunta     INT NOT NULL,
    id_opcion_elegida INT NOT NULL,
    es_correcta     BOOLEAN NOT NULL,
    CONSTRAINT fk_respuestas_pregunta FOREIGN KEY (id_pregunta) REFERENCES preguntas(id_pregunta)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_respuestas_opcion FOREIGN KEY (id_opcion_elegida) REFERENCES opciones(id_opcion)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_respuestas_intento (fase, id_intento)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- RESULTADOS (tabla resumen/consolidada por estudiante-asignatura, para dashboard)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resultados (
    id_resultado        INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante        INT NOT NULL,
    id_asignatura        INT NOT NULL,
    promedio_pretest      DECIMAL(5,2) NOT NULL,
    promedio_postest      DECIMAL(5,2) NOT NULL,
    diferencia_absoluta   DECIMAL(5,2) NOT NULL,
    incremento_porcentual DECIMAL(6,2) NOT NULL,
    nivel_adaptacion      ENUM('Básico','Medio','Avanzado') NOT NULL,
    fecha_calculo         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_resultados_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_resultados_asignatura FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- ENCUESTAS (respuestas Likert + preguntas abiertas, una fila por estudiante)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS encuestas (
    id_encuesta     INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante   INT NOT NULL UNIQUE,
    -- Dimensión pedagógica y de contenido
    calidad_adaptacion      TINYINT NOT NULL,
    comprension_lectora      TINYINT NOT NULL,
    elementos_apoyo_didactico TINYINT NOT NULL,
    idoneidad_nivel          TINYINT NOT NULL,
    -- Dimensión tecnológica y UX
    facilidad_uso            TINYINT NOT NULL,
    velocidad_respuesta       TINYINT NOT NULL,
    accesibilidad_compatibilidad TINYINT NOT NULL,
    -- Dimensión de interacción con IA
    precision_alucinaciones  TINYINT NOT NULL,
    capacidad_personalizacion TINYINT NOT NULL,
    claridad_instrucciones    TINYINT NOT NULL,
    -- Dimensión afectiva
    utilidad_percibida        TINYINT NOT NULL,
    confianza_sistema          TINYINT NOT NULL,
    satisfaccion_general        TINYINT NOT NULL,
    -- Preguntas abiertas
    dificultades_tecnicas       TEXT,
    sugerencias_diseno           TEXT,
    ia_omitio_informacion         TEXT,
    ejemplo_adaptacion_ayudo       TEXT,
    situaciones_uso                 TEXT,
    funcionalidades_adicionales      TEXT,
    confusion_texto_adaptado           TEXT,
    fecha                                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_encuestas_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT chk_likert_1 CHECK (calidad_adaptacion BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_2 CHECK (comprension_lectora BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_3 CHECK (elementos_apoyo_didactico BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_4 CHECK (idoneidad_nivel BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_5 CHECK (facilidad_uso BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_6 CHECK (velocidad_respuesta BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_7 CHECK (accesibilidad_compatibilidad BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_8 CHECK (precision_alucinaciones BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_9 CHECK (capacidad_personalizacion BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_10 CHECK (claridad_instrucciones BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_11 CHECK (utilidad_percibida BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_12 CHECK (confianza_sistema BETWEEN 1 AND 5),
    CONSTRAINT chk_likert_13 CHECK (satisfaccion_general BETWEEN 1 AND 5)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- AVANCE DEL ESTUDIANTE (control de asignaturas completadas)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS avance_estudiante (
    id_avance       INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante   INT NOT NULL,
    id_asignatura   INT NOT NULL,
    pretest_completado  BOOLEAN NOT NULL DEFAULT FALSE,
    adaptacion_generada BOOLEAN NOT NULL DEFAULT FALSE,
    postest_completado  BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE KEY uq_avance (id_estudiante, id_asignatura),
    CONSTRAINT fk_avance_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_avance_asignatura FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- LOGS (auditoría general del sistema)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS logs (
    id_log          INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT NULL,
    accion          VARCHAR(150) NOT NULL,
    detalle         TEXT,
    fecha           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_logs_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;
