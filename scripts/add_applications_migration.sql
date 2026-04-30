-- Migración: agregar tabla de postulaciones
-- Ejecutar en HeidiSQL o con: mysql -u root -p jeronimo < scripts/add_applications_migration.sql

USE jeronimo;

CREATE TABLE IF NOT EXISTS applications (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    job_id       INT NOT NULL,
    employee_id  INT NOT NULL,
    message      TEXT,
    status       VARCHAR(20) NOT NULL DEFAULT 'pending',
    applied_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id)      REFERENCES jobs(id)  ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uq_application (job_id, employee_id),
    INDEX idx_job      (job_id),
    INDEX idx_employee (employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT 'Tabla applications creada correctamente.' AS resultado;
