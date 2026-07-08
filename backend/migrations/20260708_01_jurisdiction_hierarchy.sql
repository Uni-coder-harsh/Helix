-- Helix Sprint A2
-- Administrative hierarchy and jurisdiction lookup schema migration.
-- This repository still bootstraps schemas via SQLAlchemy metadata at runtime;
-- this SQL file records the additive production migration steps for managed databases.

BEGIN;

ALTER TABLE countries
    ADD COLUMN IF NOT EXISTS code VARCHAR(100),
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE states
    ADD COLUMN IF NOT EXISTS code VARCHAR(100),
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE districts
    ADD COLUMN IF NOT EXISTS code VARCHAR(100),
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS parliamentary_constituencies (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100),
    state_id VARCHAR(36) NOT NULL REFERENCES states(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geojson_boundary TEXT,
    boundary_version INTEGER NOT NULL DEFAULT 1,
    area_metadata TEXT,
    population_metadata TEXT
);

CREATE TABLE IF NOT EXISTS assembly_constituencies (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100),
    district_id VARCHAR(36) NOT NULL REFERENCES districts(id),
    parliamentary_constituency_id VARCHAR(36) REFERENCES parliamentary_constituencies(id),
    mla_id VARCHAR(36),
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geojson_boundary TEXT,
    boundary_version INTEGER NOT NULL DEFAULT 1,
    area_metadata TEXT,
    population_metadata TEXT
);

CREATE TABLE IF NOT EXISTS villages (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100),
    assembly_constituency_id VARCHAR(36) NOT NULL REFERENCES assembly_constituencies(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    geojson_boundary TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE wards
    ADD COLUMN IF NOT EXISTS code VARCHAR(100),
    ADD COLUMN IF NOT EXISTS assembly_constituency_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS geojson_boundary TEXT,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS assembly_constituency_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS parliamentary_constituency_id VARCHAR(36);

ALTER TABLE issues
    ADD COLUMN IF NOT EXISTS state_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS district_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS parliamentary_constituency_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS assembly_constituency_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS ward_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS village_id VARCHAR(36);

ALTER TABLE incidents
    ADD COLUMN IF NOT EXISTS state_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS district_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS parliamentary_constituency_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS assembly_constituency_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS ward_id VARCHAR(36),
    ADD COLUMN IF NOT EXISTS village_id VARCHAR(36);

COMMIT;
