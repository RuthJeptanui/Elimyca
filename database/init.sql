-- database/init.sql

CREATE TABLE tutors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    expertise VARCHAR(255) NOT NULL,  -- Comma-separated, e.g., "math,english"
    availability INT DEFAULT 5,       -- Max students they can handle
    current_load INT DEFAULT 0,
    payment_status BOOLEAN DEFAULT FALSE  -- Simulated: True if "paid" to register
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    needs_description TEXT NOT NULL,  -- Student's input for prescreening
    sentiment_score FLOAT,            -- From Hugging Face (e.g., negative sentiment score)
    matched_tutor_id INT,             -- Foreign key to tutors.id
    FOREIGN KEY (matched_tutor_id) REFERENCES tutors(id)
);

-- Database Schema Updates for IntaSend Integration

-- Update students table to include payment status
ALTER TABLE students ADD COLUMN payment_status ENUM('PENDING', 'PAID', 'FAILED') DEFAULT 'PENDING';

-- Add email and phone to tutors and students (for IntaSend)
ALTER TABLE tutors ADD COLUMN email VARCHAR(255), ADD COLUMN phone_number VARCHAR(15);
ALTER TABLE students ADD COLUMN email VARCHAR(255), ADD COLUMN phone_number VARCHAR(15);

-- Create payments table (as provided, for student payments only)
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    tutor_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KES',
    phone_number VARCHAR(15),
    email VARCHAR(255),
    intasend_invoice_id VARCHAR(255) UNIQUE,
    status ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    api_ref VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (tutor_id) REFERENCES tutors(id) ON DELETE CASCADE,
    
    INDEX idx_student_id (student_id),
    INDEX idx_tutor_id (tutor_id),
    INDEX idx_intasend_invoice_id (intasend_invoice_id),
    INDEX idx_status (status)
);