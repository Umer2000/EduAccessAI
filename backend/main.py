from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional, Any
import shutil
import uuid
import os
import json
import requests
from dotenv import load_dotenv

from pypdf import PdfReader

# -------------------- Load environment + configure Gemini --------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
USE_GEMINI = bool(GEMINI_API_KEY)

GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_ID}:generateContent"







# -------------------- FastAPI app setup --------------------

app = FastAPI(
    title="EduAccess AI Backend",
    description="Backend service for converting learning materials into accessible formats.",
    version="0.4.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for hackathon/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- Data models --------------------

class ConvertResponse(BaseModel):
    lesson_id: str
    profile: str
    simplified_text: str
    bullet_summary: List[str]
    reading_level: Optional[str] = None


class LessonStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class Lesson(BaseModel):
    lesson_id: str
    title: str
    teacher_id: str
    profile: str
    language: str  # "en" or "es"
    status: LessonStatus
    simplified_text: str
    bullet_summary: List[str]
    reading_level: Optional[str] = None
    audit_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class OpusWebhookPayload(BaseModel):
    simplified_text: str
    bullet_summary: List[str]
    reading_level: Optional[str] = None
    status: LessonStatus = LessonStatus.APPROVED
    audit_json: Dict[str, Any]


# -------------------- In-memory store (fine for hackathon) --------------------

LESSONS: Dict[str, Lesson] = {}

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# -------------------- File helpers --------------------

def save_upload_to_disk(upload_file: UploadFile) -> str:
    file_id = str(uuid.uuid4())
    ext = Path(upload_file.filename).suffix or ".bin"
    dest = UPLOAD_DIR / f"{file_id}{ext}"

    with dest.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return str(dest)


def detect_file_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in [".jpg", ".jpeg", ".png", ".webp"]:
        return "image"
    return "unknown"


def extract_text_from_pdf(path: str, max_chars: int = 6000) -> str:
    """
    Simple PDF text extraction for demo (first ~6000 chars).
    """
    reader = PdfReader(path)
    chunks: List[str] = []
    for page in reader.pages:
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if txt.strip():
            chunks.append(txt)
        if len(" ".join(chunks)) > max_chars:
            break
    return " ".join(chunks)[:max_chars].strip()


# -------------------- Gemini helpers --------------------

def normalize_language_label(language: str) -> str:
    """
    Map short codes (en, es) to nicer labels for prompts.
    """
    if not language:
        return "English"
    lang = language.strip().lower()
    if lang in ("en", "eng", "english"):
        return "English"
    if lang in ("es", "spa", "spanish", "español", "espanol"):
        return "Spanish"
    return language


def call_gemini_simplify(
    raw_text: str,
    profile: str,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Call Gemini via REST API (v1beta) to generate:
      - simplified_text
      - bullet_summary[]
      - reading_level

    Uses model: gemini-1.5-flash-latest
    """
    if not USE_GEMINI or not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key not configured")

    lang = (language or "").strip().lower()
    if lang.startswith("es"):
        lang_label = "Spanish"
    else:
        lang_label = "English"

    # Accessibility style
    if profile == "dyslexic":
        style = (
            "for a student with dyslexia or reading difficulties. "
            "Use short sentences, simple vocabulary, and clear structure."
        )
    else:
        style = (
            "for a blind or low-vision student using a screen reader. "
            "Use clear structure, avoid visual-only references like 'see above', "
            "and make it easy to follow when read aloud."
        )

    # Language instructions
    if lang_label == "Spanish":
        language_instructions = (
            "Translate and simplify the content into Spanish. "
            "All JSON values (simplified_text, bullet_summary items, reading_level) "
            "MUST be written in Spanish. Do NOT include any English sentences."
        )
    else:
        language_instructions = (
            "Write all JSON values in English. "
            "Keep vocabulary simple and clear."
        )

    prompt = f"""
You are an accessibility assistant {style}

{language_instructions}

Given the following educational text, produce a JSON object with these keys:

- simplified_text: a simplified, short version of the content, friendly and clear.
- bullet_summary: an array of 3–6 short bullet points with the key ideas.
- reading_level: a rough reading level label like "Grade 5", "Grade 8", "Intro college", etc.

VERY IMPORTANT:
- Respond ONLY with valid JSON.
- Do NOT wrap the JSON in backticks or Markdown.
- Do NOT add any explanations before or after the JSON.

Text:
\"\"\"{raw_text}\"\"\""""

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    resp = requests.post(GEMINI_ENDPOINT, headers=headers, json=body, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {resp.status_code}: {resp.text}")

    resp_json = resp.json()
    try:
        # Gemini returns candidates[0].content.parts[0].text
        text_out = resp_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response format: {e}, body={resp_json}") from e

    # text_out should be pure JSON per our instructions
    data = json.loads(text_out)

    return {
        "simplified_text": data.get("simplified_text", ""),
        "bullet_summary": data.get("bullet_summary", []),
        "reading_level": data.get("reading_level", "Unknown"),
    }



# -------------------- Fallback dummy --------------------

def dummy_result(profile: str) -> Dict[str, Any]:
    return {
        "simplified_text": (
            "This is a simplified version of your uploaded content. "
            "Once the full Gemini pipeline is configured, this will contain a real adapted lesson."
        ),
        "bullet_summary": [
            "Example key point 1",
            "Example key point 2",
            "Example key point 3",
        ],
        "reading_level": "Grade 6 (mock)",
    }


# -------------------- Core processing helper --------------------

def process_upload_file(
    file: UploadFile,
    profile: str,
    language: str,
) -> Dict[str, Any]:
    """
    Shared logic for:
      - /api/materials/convert (simple API)
      - /api/lessons (teacher flow)
    """
    # 1) Save file
    local_path = save_upload_to_disk(file)
    file_type = detect_file_type(local_path)
    print(f"[INFO] Saved file to {local_path} (type={file_type}, profile={profile}, lang={language})")

    # 2) Extract text (only PDFs for now)
    raw_text = ""
    if file_type == "pdf":
        try:
            raw_text = extract_text_from_pdf(local_path)
        except Exception as e:
            print("[ERROR] Failed to extract text from PDF:", e)
    else:
        print("[WARN] Non-PDF uploads currently use fallback text.")
        raw_text = ""

    # Decide whether to use Gemini for this request
    use_gemini_for_this = USE_GEMINI

    # If no text could be extracted, use dummy
    if not raw_text:
        print("[WARN] No text extracted; using dummy result.")
        result = dummy_result(profile)
    elif not use_gemini_for_this:
        print("[INFO] Gemini not configured; using dummy result.")
        result = dummy_result(profile)
    else:
        # Try Gemini, fall back if it fails
        try:
            result = call_gemini_simplify(raw_text, profile, language)
        except Exception as e:
            print("[ERROR] Gemini call failed, using dummy result:", e)
            result = dummy_result(profile)

    return result


# -------------------- Opus integration (stub) --------------------

def trigger_opus_workflow(lesson: Lesson) -> None:
    """
    Placeholder for calling Opus API to start the
    'Intake → Understand → Decide → Review → Deliver' workflow.
    """
    print(f"[OPUS] Would start workflow for lesson {lesson.lesson_id} (status={lesson.status})")


# -------------------- Routes --------------------

@app.post("/api/materials/convert", response_model=ConvertResponse)
async def convert_material(
    file: UploadFile = File(...),
    profile: str = Form(...),    # "dyslexic" or "blind"
    language: str = Form("en"),  # "en" or "es"
):
    """
    Simple one-off conversion endpoint (no lesson tracking).
    """
    result = process_upload_file(file, profile, language)

    return ConvertResponse(
        lesson_id=str(uuid.uuid4()),
        profile=profile,
        simplified_text=result.get("simplified_text", ""),
        bullet_summary=result.get("bullet_summary", []),
        reading_level=result.get("reading_level", "Unknown"),
    )


@app.post("/api/lessons", response_model=Lesson)
async def create_lesson(
    file: UploadFile = File(...),
    profile: str = Form(...),             # "dyslexic" or "blind"
    language: str = Form("en"),           # "en" or "es"
    title: str = Form("Untitled lesson"),
    teacher_id: str = Form("demo-teacher"),
):
    """
    Teacher uploads a new lesson.
    For demo:
      - We run the AI pipeline immediately.
      - We mark lesson as APPROVED directly.
    In a full Opus integration:
      - You would set status=PENDING and let Opus update it via webhook.
    """
    lesson_id = str(uuid.uuid4())
    created_at = datetime.utcnow()

    result = process_upload_file(file, profile, language)

    lesson = Lesson(
        lesson_id=lesson_id,
        title=title,
        teacher_id=teacher_id,
        profile=profile,
        language=language,
        status=LessonStatus.APPROVED,  # later: start as PENDING and let Opus decide
        simplified_text=result.get("simplified_text", ""),
        bullet_summary=result.get("bullet_summary", []),
        reading_level=result.get("reading_level", "Unknown"),
        audit_json=None,
        created_at=created_at,
        updated_at=created_at,
    )

    LESSONS[lesson_id] = lesson

    # Kick off Opus workflow (stub)
    trigger_opus_workflow(lesson)

    return lesson


@app.get("/api/lessons", response_model=List[Lesson])
async def list_lessons(
    teacher_id: Optional[str] = Query(None),
    status: Optional[LessonStatus] = Query(None),
    profile: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
):
    """
    List lessons with optional filters:
      - teacher_id
      - status (pending/in_review/approved/rejected)
      - profile (dyslexic/blind)
      - language (en/es)
    """
    items = list(LESSONS.values())

    if teacher_id:
        items = [l for l in items if l.teacher_id == teacher_id]
    if status:
        items = [l for l in items if l.status == status]
    if profile:
        items = [l for l in items if l.profile == profile]
    if language:
        items = [l for l in items if l.language == language]

    items.sort(key=lambda l: l.created_at, reverse=True)
    return items


@app.get("/api/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str):
    lesson = LESSONS.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@app.post("/api/lessons/{lesson_id}/opus-webhook", response_model=Lesson)
async def opus_webhook(lesson_id: str, payload: OpusWebhookPayload):
    """
    Called by Opus when the workflow finishes a review cycle.
    Updates:
      - status (approved/rejected/in_review)
      - simplified_text, bullet_summary, reading_level
      - audit_json (full provenance)
    """
    lesson = LESSONS.get(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson.simplified_text = payload.simplified_text
    lesson.bullet_summary = payload.bullet_summary
    lesson.reading_level = payload.reading_level
    lesson.status = payload.status
    lesson.audit_json = payload.audit_json
    lesson.updated_at = datetime.utcnow()

    LESSONS[lesson_id] = lesson
    print(f"[OPUS] Updated lesson {lesson_id} via webhook with status={lesson.status}")
    return lesson


@app.get("/")
async def root():
    return {"message": "EduAccess AI backend is running."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
