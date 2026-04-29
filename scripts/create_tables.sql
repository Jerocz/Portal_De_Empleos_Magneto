-- Portal de Empleos Magneto — Schema de Base de Datos
-- Ejecutar con: mysql -u root -p magneto_db < scripts/create_tables.sql
-- O pegar directamente en MySQL Workbench / phpMyAdmin

CREATE DATABASE IF NOT EXISTS magneto_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE magneto_db;

-- ──────────────────────────────────────────
-- Tabla: users
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    full_name     VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active     TINYINT(1)   NOT NULL DEFAULT 1,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────
-- Tabla: profiles
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    user_id        INT          PRIMARY KEY,
    location_city  VARCHAR(100),
    modality       VARCHAR(20),          -- remote | hybrid | on-site
    salary_min_cop INT,
    salary_max_cop INT,
    years_exp      INT,
    skills         JSON,                 -- ["python", "react", ...]
    updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────
-- Tabla: jobs
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    title          VARCHAR(255) NOT NULL,
    company        VARCHAR(255) NOT NULL,
    city           VARCHAR(100),
    modality       VARCHAR(20),          -- remote | hybrid | on-site
    description    TEXT,
    salary_min_cop INT,
    salary_max_cop INT,
    skills_required JSON,               -- ["python", "docker", ...]
    posted_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────
-- Tabla: job_matches
-- ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_matches (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT            NOT NULL,
    job_id      INT            NOT NULL,
    score       DECIMAL(5,2)   NOT NULL,
    explanation TEXT,
    run_date    DATE           NOT NULL,
    created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id)  REFERENCES jobs(id)  ON DELETE CASCADE,
    INDEX idx_user_date (user_id, run_date),
    INDEX idx_score     (user_id, score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT 'Tablas creadas correctamente.' AS resultado;
