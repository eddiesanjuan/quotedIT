-- DISC-092: Add tasks table for Task & Reminder System
-- Run this migration on the production database

CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(36) PRIMARY KEY,
    contractor_id VARCHAR(36) NOT NULL REFERENCES contractors(id),
    customer_id VARCHAR(36) REFERENCES customers(id),
    quote_id VARCHAR(36) REFERENCES quotes(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Task details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'normal',
    task_type VARCHAR(50) DEFAULT 'other',

    -- Scheduling
    due_date TIMESTAMP,
    reminder_time TIMESTAMP,
    completed_at TIMESTAMP,

    -- Status
    status VARCHAR(50) DEFAULT 'pending',

    -- Recurrence
    recurrence VARCHAR(50),
    recurrence_end_date TIMESTAMP,

    -- Auto-generation tracking
    auto_generated BOOLEAN DEFAULT FALSE,
    trigger_type VARCHAR(100),
    trigger_entity_id VARCHAR(36),

    -- Notification tracking
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMP,

    -- Snooze tracking
    snoozed_until TIMESTAMP,
    snooze_count INTEGER DEFAULT 0
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tasks_contractor_id ON tasks(contractor_id);
CREATE INDEX IF NOT EXISTS idx_tasks_customer_id ON tasks(customer_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
