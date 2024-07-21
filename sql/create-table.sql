CREATE TABLE IF NOT EXISTS github_events (
    id VARCHAR PRIMARY KEY,
    event_type VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    actor_id INT,
    actor_login VARCHAR,
    repo_id INT,
    repo_name VARCHAR,
    event_data JSONB
);