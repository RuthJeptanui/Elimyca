-- Seed Tutors
INSERT INTO tutors (name, expertise, availability, email, phone, payment_status, subject_tags)
VALUES
('Alice Wanjiru', 'Mathematics', 'Weekdays 5-8pm', 'alice@example.com', '0712000001', 'PAID', 'Mathematics, Algebra'),
('Brian Otieno', 'Physics', 'Weekends 9am-1pm', 'brian@example.com', '0712000002', 'PAID', 'Physics, Science'),
('Catherine Njeri', 'English', 'Weekdays 2-5pm', 'catherine@example.com', '0712000003', 'PAID', 'English, Literature'),
('David Kamau', 'Biology', 'Weekdays 6-9pm', 'david@example.com', '0712000004', 'PAID', 'Biology, Science'),
('Emily Chebet', 'Chemistry', 'Weekends 2-6pm', 'emily@example.com', '0712000005', 'PAID', 'Chemistry, Science'),
('Francis Mwangi', 'Programming', 'Weekdays 7-9pm', 'francis@example.com', '0712000006', 'PAID', 'Programming, Python'),
('Grace Achieng', 'History', 'Weekdays 4-7pm', 'grace@example.com', '0712000007', 'PAID', 'History, Social Studies'),
('Henry Kiptoo', 'Geography', 'Weekends 10am-2pm', 'henry@example.com', '0712000008', 'PAID', 'Geography'),
('Irene Wairimu', 'Kiswahili', 'Weekdays 5-8pm', 'irene@example.com', '0712000009', 'PAID', 'Kiswahili, Languages'),
('John Kariuki', 'Computer Science', 'Weekdays 6-9pm', 'john@example.com', '0712000010', 'PAID', 'Computer Science, Programming');

-- Seed Students
INSERT INTO students (name, description, email, phone, sentiment, subject_tags)
VALUES
('Kevin Otieno', 'I need help with algebra homework', 'kevin@example.com', '0722000001', 'Neutral', 'Mathematics, Algebra'),
('Linda Akinyi', 'Struggling with physics concepts', 'linda@example.com', '0722000002', 'Frustrated', 'Physics, Science'),
('Mark Njoroge', 'Want to improve English writing skills', 'mark@example.com', '0722000003', 'Neutral', 'English, Writing'),
('Naomi Chebet', 'Having difficulties in biology lab work', 'naomi@example.com', '0722000004', 'Frustrated', 'Biology'),
('Oscar Kiplangat', 'Need extra chemistry revision for exams', 'oscar@example.com', '0722000005', 'Stressed', 'Chemistry'),
('Patricia Wambui', 'Beginner in Python programming', 'patricia@example.com', '0722000006', 'Excited', 'Programming, Python'),
('Quinton Mutiso', 'Need help understanding world history', 'quinton@example.com', '0722000007', 'Neutral', 'History'),
('Ruth Jepkemboi', 'Geography fieldwork preparation', 'ruth@example.com', '0722000008', 'Neutral', 'Geography'),
('Samson Mwikali', 'Need tutoring in Kiswahili literature', 'samson@example.com', '0722000009', 'Neutral', 'Kiswahili, Literature'),
('Tina Wanjiku', 'Interested in computer programming basics', 'tina@example.com', '0722000010', 'Excited', 'Computer Science, Programming');
