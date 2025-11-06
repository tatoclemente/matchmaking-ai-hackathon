-- Crear tabla de jugadores
CREATE TABLE IF NOT EXISTS players (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    elo INTEGER NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(10) NOT NULL,
    category VARCHAR(20) NOT NULL,
    positions JSONB NOT NULL,
    location JSONB NOT NULL,
    availability JSONB,
    acceptance_rate FLOAT NOT NULL DEFAULT 0.5,
    last_active_days INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar performance
CREATE INDEX idx_players_elo ON players(elo);
CREATE INDEX idx_players_category ON players(category);
CREATE INDEX idx_players_gender ON players(gender);
CREATE INDEX idx_players_acceptance_rate ON players(acceptance_rate DESC);
CREATE INDEX idx_players_last_active ON players(last_active_days);

-- Insertar un jugador de prueba
INSERT INTO players (id, name, elo, age, gender, category, positions, location, availability, acceptance_rate, last_active_days)
VALUES (
    'test-player-001',
    'Juan Test',
    1500,
    28,
    'MALE',
    'SEVENTH',
    '["FOREHAND", "BACKHAND"]'::jsonb,
    '{"lat": -31.42647, "lon": -64.18722, "zone": "Nueva Córdoba"}'::jsonb,
    '[{"min": "18:00", "max": "22:00"}]'::jsonb,
    0.85,
    2
);
