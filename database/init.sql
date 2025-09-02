-- Create database

USE elimyca_db;



-- Tutors table
CREATE TABLE IF NOT EXISTS tutors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    expertise VARCHAR(255) NOT NULL,      -- Comma-separated subjects
    availability INT DEFAULT 5,           -- Changed to string (e.g. "Weekdays 5-8pm")
    email VARCHAR(255),
    phone_number VARCHAR(20),
    current_load INT DEFAULT 0,
    payment_status BOOLEAN DEFAULT FALSE,
    subject_tags TEXT
);


-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    needs_description TEXT NOT NULL,      -- Clearer than 'description'
    email VARCHAR(255),
    phone_number VARCHAR(20),
    sentiment VARCHAR(50),                -- From Hugging Face
    matched_tutor_id INT,
    payment_status BOOLEAN DEFAULT FALSE,
    subject_tags TEXT,
    compatibility_score DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (matched_tutor_id) REFERENCES tutors(id) ON DELETE SET NULL
);




-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    tutor_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KES',
    phone_number VARCHAR(15),
    email VARCHAR(255),
    intasend_invoice_id VARCHAR(255) UNIQUE,
    status ENUM('PENDING','COMPLETED','FAILED','CANCELLED') DEFAULT 'PENDING',
    api_ref VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (tutor_id) REFERENCES tutors(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_tutor_id (tutor_id),
    INDEX idx_intasend_invoice_id (intasend_invoice_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);



-- Indexes for AI matching
CREATE INDEX idx_tutors_subject_tags ON tutors(subject_tags(100));
CREATE INDEX idx_students_subject_tags ON students(subject_tags(100));
CREATE INDEX idx_students_compatibility_score ON students(compatibility_score);





SELECT * FROM tutors;