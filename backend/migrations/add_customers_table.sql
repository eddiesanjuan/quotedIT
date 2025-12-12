-- DISC-086: Add customers table for CRM
-- Run this migration on the production database BEFORE add_tasks_table.sql

CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(36) PRIMARY KEY,
    contractor_id VARCHAR(36) NOT NULL REFERENCES contractors(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Contact info
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    address TEXT,

    -- Normalized fields for deduplication
    normalized_name VARCHAR(255),
    normalized_phone VARCHAR(20),

    -- CRM metadata
    status VARCHAR(50) DEFAULT 'active',
    source VARCHAR(100),
    notes TEXT,
    tags JSON DEFAULT '[]',

    -- Aggregated stats (updated by triggers/service)
    total_quoted DECIMAL(10,2) DEFAULT 0,
    total_won DECIMAL(10,2) DEFAULT 0,
    quote_count INTEGER DEFAULT 0,
    first_quote_at TIMESTAMP,
    last_quote_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_customers_contractor_id ON customers(contractor_id);
CREATE INDEX IF NOT EXISTS idx_customers_normalized_name ON customers(normalized_name);
CREATE INDEX IF NOT EXISTS idx_customers_normalized_phone ON customers(normalized_phone);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status);
CREATE INDEX IF NOT EXISTS idx_customers_last_quote_at ON customers(last_quote_at);

-- Add customer_id column to quotes table
ALTER TABLE quotes ADD COLUMN IF NOT EXISTS customer_id VARCHAR(36) REFERENCES customers(id);
CREATE INDEX IF NOT EXISTS idx_quotes_customer_id ON quotes(customer_id);
