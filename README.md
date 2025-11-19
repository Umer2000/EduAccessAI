# **🎓 EduAccess AI**
<h2>Instantly convert classroom PDFs into accessible lessons using Gemini 2.5 Flash + Opus workflows<h2/>
<h1>🚀 Overview</h1>

<h2>EduAccess AI is an accessibility-focused platform that transforms traditional classroom materials into inclusive, student-ready learning experiences.
Teachers upload any PDF or worksheet, and the system automatically:

Extracts and simplifies the content

Adapts it for dyslexic or blind learners

Generates reading levels

Passes the lesson through an Opus agentic review workflow

Updates lesson status and audit logs via webhook

Publishes approved lessons to a student dashboard

Built for the AI Genesis Hackathon, EduAccess AI delivers a seamless accessibility pipeline powered by Gemini 2.5 Flash and Opus.<h2>

<h1>✨ Features</h1>
<h3>👩‍🏫 Teacher Dashboard</h3>

<h2>Upload PDFs / images

Run AI-powered content simplification

Trigger Opus workflows for automated review

View lesson audit reports and approval status

Manage lessons across profiles and languages<h2/>

<h3>🧑‍🎓 Student Dashboard<h3/>

<h2>Browse teacher-approved lessons

Filter by profile & language

Read simplified accessible text

Listen using built-in text-to-speech

View bullet-point summaries & reading level<h2/>

<h1>⚙️ Backend (FastAPI)<h1/>

<h2>PDF text extraction using pypdf

Gemini 2.5 Flash for simplification & summarization

AI-driven reading-level estimation

Lesson database stored in-memory (hackathon mode)

Accepts Opus webhook for final audit & approval<h2/>

<h1>🤖 Opus Workflow (Fully Integrated)<h1/>

<h2>The Opus pipeline includes:

1.API Trigger using inputs:

lesson_id, teacher_id, profile, language

2.Fetch Lesson node
Fetches lesson content from FastAPI backend.

3.Agentic AI Review
Gemini evaluates clarity, accessibility issues, structure, and reading level.
Generates:

decision (ready_for_students or needs_changes)

issues list

overall comments

suggested reading level

4.Optional Human Reviewer
Teacher or moderator can approve or reject.

5.Webhook Delivery
Opus POSTs results to:
/api/lessons/{lesson_id}/opus-webhook<h2/>
FastAPI updates the lesson status, audit trail, and metadata.

6.Student Dashboard Updates Automatically
Students instantly see approved content.<h2/>



<h1>🧠 Architecture<h1/>

<h2>Frontend (React + Vite + Vercel)
            ↓
     FastAPI Backend (Render)
            ↓
     Gemini 2.5 Flash (AI)
            ↓
       Opus Workflow
            ↓
Webhook → FastAPI → Lesson Updated → Students See It<h2/>


<h1>🛠️ Tech Stack<h1/>

<h2>1.Frontend

React + Vite

TypeScript

Custom CSS

Deployed on Vercel

2.Backend

FastAPI

Uvicorn

Python 3.10+

PDF extraction (pypdf)

Environment-managed secrets

Hosted on Render

3.AI

Gemini 2.5 Flash (simplification + summarization + reading level)

Opus Workflow Engine (agentic review + audit + approval)<h2/>

🔧 Setup Guide
1️⃣ Clone the repository

git clone https://github.com/Umer2000/EduAccessAI.git
cd EduAccessAI

⚙️ Backend Setup (FastAPI)
Create .env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL_ID=gemini-2.5-flash
OPUS_API_URL=your_opus_workflow_url
OPUS_API_KEY=optional

Install dependencies
pip install -r requirements.txt

Run backend locally
uvicorn main:app --reload

Backend runs at:
http://127.0.0.1:8000

🖥️ Frontend Setup (Vite + React)
Go to frontend folder
cd frontend
Create .env
VITE_API_BASE_URL=http://127.0.0.1:8000
npm install
npm run dev

☁️ Deployment
🟣 Backend → Render

Create Web Service

Build command:
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
Add environment variables

🟢 Frontend → Vercel

Import GitHub repo

Add Vercel env var:
VITE_API_BASE_URL=https://eduaccessai.onrender.com/
Build: npm run build
Output: dist/

Current Status

✔ Teacher–Student dashboard complete

✔ Gemini simplification working

✔ Render backend live

✔ Vercel frontend live

✔ Spanish + English support

✔ Lesson storage + reading levels

✔ Webhook endpoint for Opus ready

⏳ Opus workflow integration in progress


Roadmap

🔵 Add more languages 

🔵 Add image-to-text OCR for image-only PDFs

🔵 Add multiple student accounts per teacher

🔵 Add advanced TTS (via ElevenLabs or Google TTS)

🔵 Store lessons in a real database (Supabase or Firestore)

🔵 Add student progress tracking

