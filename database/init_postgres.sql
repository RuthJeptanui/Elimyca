-- PostgreSQL compatible schema for Elimyca -production database
-- Database: elimyca_db

-- Tutors table
CREATE TABLE IF NOT EXISTS tutors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    expertise VARCHAR(255) NOT NULL,      -- Comma-separated subjects
    availability VARCHAR(100),            -- String (e.g. "Weekdays 5-8pm")
    email VARCHAR(255),
    phone_number VARCHAR(20),
    current_load INT DEFAULT 0,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (payment_status IN ('PENDING', 'PAID', 'FAILED')),
    subject_tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    needs_description TEXT NOT NULL,      -- Clearer than 'description'
    email VARCHAR(255),
    phone_number VARCHAR(20),
    sentiment VARCHAR(50),                -- From Hugging Face
    matched_tutor_id INT,
    payment_status VARCHAR(20) DEFAULT 'PENDING' CHECK (payment_status IN ('PENDING', 'PAID', 'FAILED')),
    subject_tags TEXT,
    compatibility_score DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matched_tutor_id) REFERENCES tutors(id) ON DELETE SET NULL
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    tutor_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KES',
    phone_number VARCHAR(15),
    email VARCHAR(255),
    intasend_invoice_id VARCHAR(255) UNIQUE,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    api_ref VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (tutor_id) REFERENCES tutors(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tutors_subject_tags ON tutors USING gin (to_tsvector('english', subject_tags));
CREATE INDEX IF NOT EXISTS idx_students_subject_tags ON students USING gin (to_tsvector('english', subject_tags));
CREATE INDEX IF NOT EXISTS idx_students_compatibility_score ON students(compatibility_score);
CREATE INDEX IF NOT EXISTS idx_payments_student_id ON payments(student_id);
CREATE INDEX IF NOT EXISTS idx_payments_tutor_id ON payments(tutor_id);
CREATE INDEX IF NOT EXISTS idx_payments_intasend_invoice_id ON payments(intasend_invoice_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();