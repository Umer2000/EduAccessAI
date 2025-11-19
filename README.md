# **🎓 EduAccess AI**
<h2>Transforms classroom materials into dyslexia-friendly and screen-reader-ready content using Gemini + Opus.<h2/>
<h2>Power Point Presentation Link https://docs.google.com/presentation/d/1RCJdNovGxJhpGoBsq0KLagEu2k0WZkxU/edit?usp=sharing&ouid=103135272738788649143&rtpof=true&sd=true<h2/>
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

FastAPI + Uvicorn

Python

PDF extraction (pypdf)

Deployed on Render

3.AI

Gemini 2.5 Flash (simplification, summarization, language adaptation)

4.Automation

Opus Workflow Engine

API trigger

Fetch content

Agentic decisioning

Automated quality checks

Webhook callback<h2/>

<h1>🔧 Setup Guide<h1/>
<h2/>1️⃣ Clone the repository

git clone https://github.com/Umer2000/EduAccessAI.git
cd EduAccessAI<h2>

<h1>⚙️ Backend Setup (FastAPI)<h1/>
<h2>.env example
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL_ID=gemini-2.5-flash
OPUS_API_URL=https://api.opus.ai/workflows/<id>/start
OPUS_API_KEY=your_opus_api_key


Install dependencies
pip install -r requirements.txt


Run backend locally
uvicorn main:app --reload


Backend runs at:
http://127.0.0.1:8000<h2/>

<h1>🖥️ Frontend Setup (Vite + React)<h1/>
            
<h2>Go to frontend folder
cd frontend
Create .env
VITE_API_BASE_URL=http://127.0.0.1:8000
            
Install and Run
npm install
npm run dev<h2/>

<h1>☁️ Deployment<h1/>
<h2>🟣 Backend → Render

Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port $PORT

Add environment variables

🟢 Frontend → Vercel

Import GitHub repo

Add Vercel env var:
VITE_API_BASE_URL=https://eduaccessai.onrender.com/
Build: npm run build
Output directory: dist/<h2/>

<h1>📌 Current Status<h1/>

<h2>✔ Teacher dashboard

✔ Student dashboard

✔ Gemini 2.5 Flash integration

✔ Real-time PDF processing

✔ Language support: English + Spanish

✔ Live backend (Render)

✔ Live frontend (Vercel)

✔ Opus workflow fully integrated

✔ Webhook updating lessons correctly

✔ Full end-to-end accessibility pipeline<h2/>


<h1>Roadmap<h1/>

<h2>🔵 Add OCR for images-only PDFs 

🔵 Add more languages

🔵 Add real database (Supabase / Firebase)

🔵 Add student analytics & reading progress

🔵Multi-teacher multi-classroom support

🔵 Improve audio using advanced TTS<h2/>

<h1>👤 Author<h1/>

<h2>Team: Genesis Hackers<h2/>
 <h2>Umer Anis- AI Developer<h2/>
             
<h2>Shadab Ahmed-Accessibility Advocate<h2/>
<h2>Built for the AI Genesis Hackathon(lablab.ai)<h2/>

