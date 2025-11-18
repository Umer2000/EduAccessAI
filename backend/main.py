from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
import shutil
import uuid
import os
import json

import google.generativeai as genai
from pypdf import PdfReader

# -------------------- Load environment + configure Gemini --------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
USE_GEMINI = bool(GEMINI_API_KEY)

if USE_GEMINI:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None


# -------------------- FastAPI app setup --------------------

app = FastAPI(
    title="EduAccess AI Backend",
    description="Backend service for converting learning materials into accessible formats.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- Data models --------------------

class ConvertResponse(BaseModel):
    lesson_id: str
    profile: str
    simplified_text: str
    bullet_summary: list[str]
    reading_level: str | None = None


# -------------------- File helpers --------------------

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


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
    chunks: list[str] = []
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
    Map short codes (en, ur) to nicer labels for prompts.
    """
    if not language:
        return "English"
    lang = language.strip().lower()
    if lang in ("en", "eng", "english"):
        return "English"
    if lang in ("ur", "urdu"):
        return "Urdu"
    return language


def call_gemini_simplify(
    raw_text: str,
    profile: str,
    language: str = "en",
) -> dict:
    """
    Call Gemini to generate:
      - simplified_text
      - bullet_summary[]
      - reading_level

    IMPORTANT:
    - If language is Urdu, we explicitly tell Gemini to TRANSLATE + simplify and
      to respond ONLY in Urdu for all JSON values.
    """
    if not USE_GEMINI or not gemini_model:
        raise RuntimeError("Gemini not configured")

    lang_label = normalize_language_label(language)

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
    if lang_label.lower().startswith("urdu"):
        language_instructions = (
            "Translate and simplify the content into Urdu. "
            "All JSON values (simplified_text, bullet_summary items, reading_level) "
            "MUST be written in Urdu script only (except numbers and the grade number). "
            "Do NOT include any English sentences or explanations."
        )
    elif lang_label.lower().startswith("english"):
        language_instructions = (
            "Write all JSON values in English. "
            "Keep vocabulary simple and clear."
        )
    else:
        language_instructions = (
            f"Write all JSON values in {lang_label}. "
            "Do not mix languages unless necessary for technical terms."
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
\"\"\"{raw_text}\"\"\"
"""

    response = gemini_model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.5,
            "max_output_tokens": 512,
        },
    )

    txt = response.text.strip()

    # Strip markdown code fences if present (just in case)
    if txt.startswith("```"):
        txt = txt.strip("`")
        if "\n" in txt:
            txt = txt.split("\n", 1)[1]

    data = json.loads(txt)

    return {
        "simplified_text": data.get("simplified_text", ""),
        "bullet_summary": data.get("bullet_summary", []),
        "reading_level": data.get("reading_level", "Unknown"),
    }



# -------------------- Fallback dummy --------------------

def dummy_result(profile: str) -> dict:
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


# -------------------- Routes --------------------

@app.post("/api/materials/convert", response_model=ConvertResponse)
async def convert_material(
    file: UploadFile = File(...),
    profile: str = Form(...),   # "dyslexic" or "blind"
    language: str = Form("en"),
):
    """
    Main endpoint for converting learning materials into accessible formats.
    1) Save file
    2) Extract text (for PDF)
    3) Call Gemini (if configured), else use fallback
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

    # If no text could be extracted, still return something
        # Decide whether to use Gemini for this request
    lang_lower = (language or "").strip().lower()
    use_gemini_for_this = USE_GEMINI and not lang_lower.startswith("ur")

    # If no text could be extracted, or we are in Urdu mode, use dummy
    if not raw_text:
        print("[WARN] No text extracted; using dummy result.")
        result = dummy_result(profile)
    elif not use_gemini_for_this:
        print("[INFO] Skipping Gemini for this language; using dummy result.")
        result = dummy_result(profile)
    else:
        # 3) Try Gemini, fall back if it fails
        try:
            result = call_gemini_simplify(raw_text, profile, language)
        except Exception as e:
            print("[ERROR] Gemini call failed, using dummy result:", e)
            result = dummy_result(profile)


    return ConvertResponse(
        lesson_id=str(uuid.uuid4()),
        profile=profile,
        simplified_text=result.get("simplified_text", ""),
        bullet_summary=result.get("bullet_summary", []),
        reading_level=result.get("reading_level", "Unknown"),
    )


@app.get("/")
async def root():
    return {"message": "EduAccess AI backend is running."}
