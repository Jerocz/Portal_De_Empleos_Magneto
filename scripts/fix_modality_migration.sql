-- ================================================================
-- SOLUCIÓN DEFINITIVA: Error "Data truncated for column 'modality'"
-- Ejecutar en MySQL: mysql -u root -p magneto_db < scripts/fix_modality_migration.sql
-- ================================================================

USE magneto_db;

-- Paso 1: Ver qué tipo tiene actualmente la columna (diagnóstico)
SELECT COLUMN_NAME, COLUMN_TYPE, CHARACTER_MAXIMUM_LENGTH
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'magneto_db' AND TABLE_NAME IN ('jobs','profiles') AND COLUMN_NAME = 'modality';

-- Paso 2: Convertir a VARCHAR(30) libre (elimina cualquier ENUM o restricción)
ALTER TABLE jobs     MODIFY COLUMN modality VARCHAR(30) NULL;
ALTER TABLE profiles MODIFY COLUMN modality VARCHAR(30) NULL;

-- Paso 3: Normalizar datos existentes a los valores nuevos
UPDATE jobs     SET modality = 'remote'     WHERE modality IN ('Remote','REMOTE','remoto','Remoto');
UPDATE jobs     SET modality = 'hybrid'     WHERE modality IN ('Hybrid','HYBRID','hibrido','híbrido','Híbrido');
UPDATE jobs     SET modality = 'presencial' WHERE modality IN ('on-site','on_site','onsite','Presencial','PRESENCIAL','presencial');

UPDATE profiles SET modality = 'remote'     WHERE modality IN ('Remote','REMOTE','remoto','Remoto');
UPDATE profiles SET modality = 'hybrid'     WHERE modality IN ('Hybrid','HYBRID','hibrido','híbrido','Híbrido');
UPDATE profiles SET modality = 'presencial' WHERE modality IN ('on-site','on_site','onsite','Presencial','PRESENCIAL','presencial');

SELECT 'Migracion completada correctamente.' AS resultado;
