-- ============================================================
-- Archivo: init.sql
-- Objetivo: Inicializar la base de datos centinela_db
--           con las tablas necesarias para el proyecto
-- ============================================================

-- Crear tabla de URLs que se van a procesar
CREATE TABLE urls (
    id SERIAL PRIMARY KEY,          -- Identificador único
    url TEXT NOT NULL,              -- Dirección web a analizar
    priority INT DEFAULT 0,         -- Prioridad de procesamiento (0 = normal)
    status VARCHAR(50) DEFAULT 'pending', -- Estado: pending, processed, error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Fecha de creación
);

-- Crear tabla de resultados de análisis
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,          -- Identificador único
    url_id INT REFERENCES urls(id) ON DELETE CASCADE, -- Relación con la URL
    sentiment VARCHAR(20),          -- Resultado del análisis de sentimiento (ej: positivo, negativo, neutral)
    keywords TEXT,                  -- Palabras clave encontradas
    score NUMERIC,                  -- Puntaje de confianza del análisis
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Fecha de análisis
);

-- Crear tabla de publicaciones realizadas
CREATE TABLE publications (
    id SERIAL PRIMARY KEY,          -- Identificador único
    url_id INT REFERENCES urls(id) ON DELETE CASCADE, -- Relación con la URL
    platform VARCHAR(50),           -- Plataforma donde se publicó (ej: Twitter, Mastodon, Reddit)
    message TEXT,                   -- Mensaje publicado
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Fecha de publicación
);

-- Crear tabla de usuarios opcional (si quieres manejar autenticación)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,          -- Identificador único
    username VARCHAR(100) UNIQUE,   -- Nombre de usuario
    password VARCHAR(255),          -- Contraseña encriptada
    role VARCHAR(50) DEFAULT 'user',-- Rol: admin, user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Fecha de creación
);

-- ============================================================
-- Datos iniciales opcionales (ejemplo de inserción)
-- ============================================================

-- Insertar una URL de prueba
INSERT INTO urls (url, priority, status)
VALUES ('https://www.reuters.com/example', 1, 'pending');

-- Insertar un usuario de prueba
INSERT INTO users (username, password, role)
VALUES ('admin', 'admin123', 'admin');

-- Índices para acelerar consultas frecuentes
CREATE INDEX idx_urls_status ON urls(status);
CREATE INDEX idx_analyses_url_id ON analyses(url_id);
CREATE INDEX idx_publications_url_id ON publications(url_id);

-- Restricciones para mantener datos consistentes
ALTER TABLE analyses
  ADD CONSTRAINT chk_score_nonnegative CHECK (score IS NULL OR score >= 0);

ALTER TABLE publications
  ADD CONSTRAINT chk_platform_nonempty CHECK (platform IS NOT NULL AND length(platform) > 0);
