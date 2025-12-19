CREATE TABLE ai_agent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT DEFAULT NULL,
    capability TEXT DEFAULT NULL,
    description TEXT DEFAULT NULL,
    is_public INTEGER NOT NULL DEFAULT 1,
    online INTEGER NOT NULL,
    agent_type TEXT DEFAULT NULL, -- Removed COMMENT as SQLite does not support it
);