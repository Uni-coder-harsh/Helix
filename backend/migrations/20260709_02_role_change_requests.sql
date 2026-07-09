CREATE TABLE IF NOT EXISTS role_change_requests (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    requested_role VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
