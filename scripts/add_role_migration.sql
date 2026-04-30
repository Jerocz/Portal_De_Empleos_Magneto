-- Migración: agregar rol a usuarios y posted_by a empleos
-- Ejecutar si ya tienes la base de datos creada (sin borrar datos)
-- Uso: mysql -u root -p jeronimo < scripts/add_role_migration.sql

USE jeronimo;

ALTER TABLE users
  ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'employee';

ALTER TABLE jobs
  ADD COLUMN posted_by INT NULL,
  ADD CONSTRAINT fk_jobs_posted_by
    FOREIGN KEY (posted_by) REFERENCES users(id) ON DELETE SET NULL;

SELECT 'Migración aplicada correctamente.' AS resultado;
