# Elimyca Connect 🎓

**Elimyca Connect** is a hackathon project aimed at advancing **SDG 4: Quality Education**.  
It connects students and parents with qualified tutors, ensuring accessible and equitable education.  

The platform leverages **AI for sentiment analysis and intelligent subject detection** to prescreen student needs and match them with suitable tutors. Matching prevents tutor overload and ensures the best possible learning experience.  

Payments are handled securely via **IntaSend**, optimized for African markets (e.g., **M-Pesa integration**).


## ✨ Features

### Core Features
- **Tutor Registration**  
  Tutors register with expertise, availability, email, and phone.  
  - Monthly fee: **KES 1000** via IntaSend.  
  - Active tutors become visible to students.  

- **Student Prescreening & Matching**  
  - Students describe their learning needs.  
  - Hugging Face Sentiment Analysis API detects urgency (e.g., frustration level).  
  - AI calculates compatibility based on tutor expertise, availability, and load.  

- **Payments Integration (via IntaSend)**  
  - Tutors: Monthly subscription.  
  - Students: Pay per session (default KES 1000).  
  - Supports **M-Pesa & card payments** with full transaction records.  

- **Dashboard & Analytics**  
  - Simple charts (via Chart.js) for tutor availability and workloads.  
  - Admin dashboard for system insights.  

- **Database Management**  
  - MySQL tables for tutors, students, and payments.  
  - Tracks payment status (`PENDING / PAID / FAILED`).  

---

### 🤖 AI-Enhanced Features
- **Smart Matching**
  - Subject detection (Math, Science, Programming, Languages, etc.)  
  - Compatibility scoring (0–100%) using multiple factors:  
    - Subject overlap (40%)  
    - Keyword/text similarity (20%)  
    - Urgency (20%)  
    - Sentiment weight (20%)  
  - Ranked results (Top 3 tutor matches).  

- **Smart Form Assistance**
  - Real-time subject suggestions while typing.  
  - Auto-completion of subjects.  
  - Sentiment-driven prioritization.  

- **Enhanced Tutor Selection**
  - Visual compatibility scores (color-coded).  
  - AI “Best Match” badges.  
  - Clear tutor expertise tags.  

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS, JavaScript, Bootstrap, Chart.js  
- **Backend:** Python (Flask framework)  
- **Database:** MySQL  
- **AI Integration:** Hugging Face Inference API  
  - `distilbert-base-uncased-finetuned-sst-2-english` for sentiment analysis  
- **Payments:** IntaSend Python SDK  
- **Other:** Requests, mysql-connector-python  

---

## 📂 Project Structure

elimyca/
├── app.py                  # Main Flask app with routes and logic
├── config.py               # Configs (DB creds, API keys, etc.)
├── config_template.py      # Template config for environment variables
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html          # Home page
│   ├── student_form.html   # Student needs form
│   ├── tutor_register.html # Tutor registration form
│   ├── tutor_selection.html# Tutor matching results
│   └── match_results.html  # Charts & match results
├── static/                 # Static assets
│   ├── css/style.css       # Custom styles
│   ├── js/app.js           # Charts & interactions
│   └── images/             # Images (e.g., SDG4 badge)
├── database/               # Database scripts
│   ├── init.sql            # Initial schema
│   └── database_updates.sql# Updates for AI features
├── AI_FEATURES_README.md   # Extended documentation for AI
└── README.md               # This file



## ⚙️ Installation & Setup

### Prerequisites
- Python **3.8+**  
- MySQL server running  
- IntaSend account with sandbox keys  
- Hugging Face token (optional for higher API limits)  

### Steps

1. **Clone the Repo**
   ```bash
   git clone <your-repo-url>
   cd elimyca_connect

## Set up virtual environment
 -  python -m venv venv
 -  # Windows
 -  venv\Scripts\activate
 -  # Unix/Mac
 -  source venv/bin/activate

 ## Istall dependancies
  - pip install -r requirements.txt

## Configure

Copy config_template.py → config.py

Update with MySQL credentials, IntaSend keys, Hugging Face token

## Set Up Database

    mysql -u root -p
    CREATE DATABASE elimyca_db;
    USE elymica_db;
    SOURCE database/init.sql;
    SOURCE database/database_updates.sql;

## Run the App

    python app.py
    Access at: http://127.0.0.1:5000/ 


  ## 🚀 Usage

## Home Page → Choose "I'm a Student/Parent" or "I'm a Tutor"

## Tutor Flow

Register with expertise & availability

Pay monthly fee via IntaSend

On success → profile visible to students

## Student Flow

Submit learning needs form

AI analyzes sentiment & subjects

Get matched with top tutors

Pay per session via IntaSend

On success → access tutor details & charts

Testing Payments → Use IntaSend Sandbox (test M-Pesa/cards).


## 📊 Database Enhancements
-- Tutors table
ALTER TABLE tutors ADD COLUMN subject_tags TEXT DEFAULT '';

-- Students table
ALTER TABLE students ADD COLUMN subject_tags TEXT DEFAULT '';
ALTER TABLE students ADD COLUMN compatibility_score DECIMAL(5,2) DEFAULT 0.00;

-- Indexes
CREATE INDEX idx_tutors_subject_tags ON tutors(subject_tags);
CREATE INDEX idx_students_subject_tags ON students(subject_tags);
CREATE INDEX idx_students_compatibility_score ON students(compatibility_score);

## 🔮 Future Enhancements

Tutor recurring payments (via IntaSend webhooks)

Authentication (login/logout)

Tutor profiles with reviews & ratings

Multi-language support

Learning style matching

Recommendation engine (suggest new subjects)

Mobile app versions

## 💡 Hackathon Notes

Built for Ruth Jeptanui, focusing on SDG 4: Quality Education

Optimized for African markets (mobile money, low fees)

Total dev time: ~1–2 days for core features

Contributors: Ruth Jeptanui

📜 License

MIT License © 2025 Ruth Jeptanui
