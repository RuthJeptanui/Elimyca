-- Database updates to support AI-enhanced matching features
-- Run these SQL commands to add new columns for AI functionality

-- Add AI-related columns to students table
ALTER TABLE students ADD COLUMN subject_tags TEXT ;
ALTER TABLE students ADD COLUMN compatibility_score DECIMAL(5,2) DEFAULT 0.00;

-- Create index for better performance on subject-based queries
CREATE INDEX idx_tutors_subject_tags ON tutors(subject_tags(100));
CREATE INDEX idx_students_subject_tags ON students(subject_tags(100));
CREATE INDEX idx_students_compatibility_score ON students(compatibility_score);

-- Update existing records to have empty subject_tags (optional, for safety)
UPDATE tutors SET subject_tags = '' WHERE subject_tags IS NULL;
UPDATE students SET subject_tags = '' WHERE subject_tags IS NULL;
UPDATE students SET compatibility_score = 0.00 WHERE compatibility_score IS NULL;


SELECT * FROM students;

