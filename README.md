🎓 EduAccess AI
Instantly convert classroom PDFs into accessible lessons using Gemini 2.5 Flash + Opus workflows
🚀 Overview

EduAccess AI is an accessibility-focused platform that transforms traditional classroom materials into inclusive, student-ready learning experiences.
Teachers upload any PDF or worksheet, and the system automatically:

Extracts content

Simplifies language

Adapts the lesson for dyslexic or blind students

Generates reading levels

Passes the output through an Opus agentic review workflow for quality and safety

Publishes approved lessons to a student dashboard

Built for the AI Genesis Hackathon, EduAccess AI streamlines accessibility and improves learning for millions of students who struggle with reading disabilities or visual impairments.

✨ Features
👩‍🏫 Teacher Dashboard

Upload PDFs, images, or worksheets

Choose accessibility profile: Dyslexic or Blind

Choose output language: English or Spanish

View past lessons, status, and AI + human review logs

Trigger Opus workflow for quality assurance

🧑‍🎓 Student Dashboard

Filter lessons by profile and language

Read simplified text in a clean, accessible format

Listen using built-in text-to-speech

View key points and reading difficulty level

⚙️ Backend (FastAPI)

PDF extraction using pypdf

Gemini 2.5 Flash text simplification + summarization

Lesson storage

Webhook endpoint for Opus to return audit decisions

Fully CORS enabled for frontend

🤖 Opus Workflow

API-triggered workflow using inputs:
lesson_id, teacher_id, profile, language

Fetch lesson from backend

Agentic Review: clarity checks, accessibility checks, rule-based decision

Optional Human Review

Sends audit + status back to backend via webhook


🧠 Architecture

Frontend (React + Vite + Vercel)
         |
         v
Backend (FastAPI on Render)
         |
   Gemini 2.5 Flash
         |
         v
     Opus Workflow
         |
         v
Webhook → FastAPI → Updates Lesson → Students See Final Output

🛠️ Tech Stack

Frontend

React + Vite

TypeScript

Tailwind-like styling (custom CSS)

Text-to-Speech API

Hosted on Vercel

Backend

FastAPI

Uvicorn

Python 3.10+

PDF extraction (pypdf)

Environment-managed secrets

Hosted on Render

AI

Gemini 2.5 Flash (simplification + summarization + reading level)

Opus Workflow Engine (agentic review + audit + approval)

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

