-- vitalhelp_schema.sql
-- Table users : utilisateurs de l'application avec contraintes

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(150) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    nom             VARCHAR(100) NOT NULL,
    age             INTEGER NOT NULL CHECK (age >= 0 AND age <= 150),
    taille_cm       INTEGER NOT NULL CHECK (taille_cm >= 40 AND taille_cm <= 300),
    sexe            VARCHAR(10) NOT NULL CHECK (sexe IN ('homme', 'femme')),
    avatar_url      VARCHAR(255),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index pour accélérer la recherche par email
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================
-- VitalHelp - Schema PostgreSQL
-- ============================================

-- Table mesures
CREATE TABLE IF NOT EXISTS mesures (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    poids_kg        NUMERIC(5, 2),
    tension_sys     INTEGER,
    tension_dia     INTEGER,
    glycemie_gl     NUMERIC(4, 2),
    freq_cardiaque  INTEGER,
    imc             NUMERIC(4, 1),
    note            TEXT,
    date_mesure     TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT check_poids        CHECK (poids_kg IS NULL OR (poids_kg >= 1 AND poids_kg <= 500)),
    CONSTRAINT check_tension_sys  CHECK (tension_sys IS NULL OR (tension_sys >= 50 AND tension_sys <= 300)),
    CONSTRAINT check_tension_dia  CHECK (tension_dia IS NULL OR (tension_dia >= 30 AND tension_dia <= 200)),
    CONSTRAINT check_glycemie     CHECK (glycemie_gl IS NULL OR (glycemie_gl >= 0 AND glycemie_gl <= 10)),
    CONSTRAINT check_freq         CHECK (freq_cardiaque IS NULL OR (freq_cardiaque >= 20 AND freq_cardiaque <= 300))
);

-- Index pour accélérer les requêtes "toutes les mesures de l'utilisateur X"
CREATE INDEX IF NOT EXISTS idx_mesures_user_date ON mesures(utilisateur_id, date_mesure DESC);

-- Table objectifs
CREATE TABLE IF NOT EXISTS objectifs (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    titre           VARCHAR(150) NOT NULL,
    type_indicateur VARCHAR(20)  NOT NULL,
    valeur_depart   NUMERIC(6,2) NOT NULL,
    valeur_cible    NUMERIC(6,2) NOT NULL,
    deadline        DATE,
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT check_type_indicateur CHECK (type_indicateur IN ('poids','tension_sys','tension_dia','glycemie','freq_cardiaque','imc')),
    CONSTRAINT check_depart CHECK (valeur_depart >= 0 AND valeur_depart <= 500),
    CONSTRAINT check_cible  CHECK (valeur_cible  >= 0 AND valeur_cible  <= 500)
);

CREATE INDEX IF NOT EXISTS idx_objectifs_user ON objectifs(utilisateur_id);

-- Table analyses_ia
CREATE TABLE IF NOT EXISTS analyses_ia (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score_global    INTEGER NOT NULL,
    resume          TEXT NOT NULL,
    interpretation  TEXT NOT NULL,
    risques         JSONB NOT NULL,
    recommandations JSONB NOT NULL,
    nb_mesures_analysees INTEGER NOT NULL DEFAULT 0,
    modele_utilise  VARCHAR(50) NOT NULL DEFAULT 'llama-3.3-70b',
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT check_score_ia CHECK (score_global >= 0 AND score_global <= 100)
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_date ON analyses_ia(utilisateur_id, created_at DESC);

-- Table liens_partage
CREATE TABLE IF NOT EXISTS liens_partage (
    id              SERIAL PRIMARY KEY,
    utilisateur_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token           VARCHAR(64) UNIQUE NOT NULL,
    expires_at      TIMESTAMP,
    revoked         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_liens_token ON liens_partage(token);
CREATE INDEX IF NOT EXISTS idx_liens_user  ON liens_partage(utilisateur_id);