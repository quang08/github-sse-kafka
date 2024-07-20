create table if not exists github_events (
    id varchar primary key,
    event_type varchar,
    event_data JSONB,
    created_at TIMESTAMPTZ default now()
)