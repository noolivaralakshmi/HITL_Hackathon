-- Users table with role-based access
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('contributor', 'contributor+reviewer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory records
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    change_type TEXT,
    confidence REAL DEFAULT 0,
    detection_reasons TEXT DEFAULT '[]',
    reasoning TEXT DEFAULT '{}',
    missing_info TEXT DEFAULT '[]',
    risk_level TEXT DEFAULT 'MEDIUM' CHECK(risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'BLOCKED')),
    guardrail_flags TEXT DEFAULT '[]',
    status TEXT DEFAULT 'DRAFT' CHECK(status IN ('DRAFT', 'PENDING_REVIEW', 'VERIFIED', 'REJECTED', 'ROLLED_BACK', 'BLOCKED', 'DISCARDED')),
    contributor_id TEXT,
    assigned_reviewer TEXT,
    approved_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,
    approved_at TIMESTAMP,
    rolled_back_at TIMESTAMP,
    rollback_reason TEXT,
    FOREIGN KEY (contributor_id) REFERENCES users(id),
    FOREIGN KEY (assigned_reviewer) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- Uploaded documents
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    memory_id TEXT,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    content TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

-- Chat messages for HITL interaction
CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,
    user_id TEXT,
    role TEXT NOT NULL CHECK(role IN ('reviewer', 'ai')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES memories(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Action log (audit trail)
CREATE TABLE IF NOT EXISTS action_log (
    id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,
    user_id TEXT,
    action TEXT NOT NULL CHECK(action IN (
        'USER_REQUEST', 'AI_DRAFT', 'HUMAN_REVIEW',
        'APPROVED', 'REJECTED', 'EDITED',
        'ROLLED_BACK', 'GUARDRAIL_FLAG', 'BLOCKED'
    )),
    risk_level TEXT,
    details TEXT DEFAULT '{}',
    ai_output TEXT,
    human_decision TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES memories(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Approval rules configuration
CREATE TABLE IF NOT EXISTS approval_rules (
    id TEXT PRIMARY KEY,
    risk_level TEXT NOT NULL,
    required_role TEXT,
    auto_approve INTEGER DEFAULT 0,
    blocked INTEGER DEFAULT 0,
    description TEXT
);

-- Memory snapshots for rollback
CREATE TABLE IF NOT EXISTS memory_snapshots (
    id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,
    snapshot TEXT NOT NULL,
    action TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

-- Full-text search index for verified memories (Mode 2)
CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    memory_id,
    change_type,
    reasoning
);

-- Insert default users for demo (2 contributors, 2 contributor+reviewers)
INSERT OR IGNORE INTO users (id, name, email, role) VALUES
    ('user-001', 'Vara Lakshmi', 'vara.lakshmi@company.com', 'contributor+reviewer'),
    ('user-002', 'Shanthi', 'shanthi@company.com', 'contributor+reviewer'),
    ('user-003', 'Archana', 'archana@company.com', 'contributor'),
    ('user-004', 'Priyanka', 'priyanka@company.com', 'contributor');

-- Insert default approval rules
INSERT OR IGNORE INTO approval_rules (id, risk_level, required_role, auto_approve, blocked, description) VALUES
    ('rule-low', 'LOW', 'reviewer', 0, 0, 'Low risk actions can be approved by reviewers'),
    ('rule-medium', 'MEDIUM', 'approver', 0, 0, 'Medium risk requires approver role'),
    ('rule-high', 'HIGH', 'admin', 0, 0, 'High risk requires admin approval'),
    ('rule-blocked', 'BLOCKED', NULL, 0, 1, 'Blocked actions cannot be approved');
