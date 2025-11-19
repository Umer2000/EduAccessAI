import React, { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

type Profile = "dyslexic" | "blind";
type Language = "en" | "es";
type LessonStatus = "pending" | "in_review" | "approved" | "rejected";

type Lesson = {
  lesson_id: string;
  title: string;
  teacher_id: string;
  profile: Profile;
  language: string; // "en" or "es"
  status: LessonStatus;
  simplified_text: string;
  bullet_summary: string[];
  reading_level: string | null;
  audit_json?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

type Mode = "teacher" | "student";

const DEMO_TEACHER_ID = "demo-teacher-1";

function App() {
  const [mode, setMode] = useState<Mode>("teacher");

  // Shared lesson state
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [activeLesson, setActiveLesson] = useState<Lesson | null>(null);

  // Teacher upload form
  const [profile, setProfile] = useState<Profile>("dyslexic");
  const [language, setLanguage] = useState<Language>("en");
  const [title, setTitle] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Student filters
  const [studentProfile, setStudentProfile] = useState<Profile>("dyslexic");
  const [studentLanguage, setStudentLanguage] = useState<Language>("en");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    } else {
      setFile(null);
    }
  };

  const handleTeacherSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ) => {
    e.preventDefault();
    setError(null);

    if (!file) {
      setError("Please upload a file first.");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("profile", profile);
      formData.append("language", language);
      formData.append("title", title || "Untitled lesson");
      formData.append("teacher_id", DEMO_TEACHER_ID);

      const res = await fetch(`${API_BASE_URL}/api/lessons`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const lesson = (await res.json()) as Lesson;
      setLessons((prev) => [lesson, ...prev]);
      setActiveLesson(lesson);
      setFile(null);
      setTitle("");
    } catch (err) {
      console.error(err);
      setError(
        "Something went wrong while processing the file. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleListen = () => {
    if (!activeLesson) return;
    const utterance = new SpeechSynthesisUtterance(
      activeLesson.simplified_text || ""
    );
    utterance.rate = 0.95;
    speechSynthesis.speak(utterance);
  };

  const fetchLessons = async (params: Record<string, string | undefined>) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value) searchParams.append(key, value);
    });

    const query = searchParams.toString();
    const url = `${API_BASE_URL}/api/lessons${query ? `?${query}` : ""}`;

    try {
      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`Failed to fetch lessons: ${res.status}`);
      }
      const data = (await res.json()) as Lesson[];
      setLessons(data);
      if (data.length > 0) {
        setActiveLesson(data[0]);
      } else {
        setActiveLesson(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Load teacher lessons when in teacher mode
  useEffect(() => {
    if (mode === "teacher") {
      fetchLessons({ teacher_id: DEMO_TEACHER_ID });
    }
  }, [mode]);

  // Load approved lessons for students when in student mode or filters change
  useEffect(() => {
    if (mode === "student") {
      fetchLessons({
        status: "approved",
        profile: studentProfile,
        language: studentLanguage,
      });
    }
  }, [mode, studentProfile, studentLanguage]);

  const isTeacher = mode === "teacher";

  return (
    <div className={`ea-root ${false ? "ea-dark" : ""}`}>
      <div className="ea-backdrop" />

      {/* Centered shell for navbar + content */}
      <div className="ea-shell">
        {/* Top navbar */}
        <nav className="ea-navbar">
          <div className="ea-navbar-left">
            <div className="ea-logo-circle">EA</div>
            <div>
              <span className="ea-navbar-title">EduAccess AI</span>
              <span className="ea-navbar-tagline">
                Accessible learning, powered by Gemini + Opus.
              </span>
            </div>
          </div>
          <div className="ea-navbar-right">
            <div className="ea-mode-toggle">
              <button
                type="button"
                className={`ea-pill ea-pill-small ${
                  mode === "teacher" ? "ea-pill-active" : ""
                }`}
                onClick={() => setMode("teacher")}
              >
                👩‍🏫 Teacher
              </button>
              <button
                type="button"
                className={`ea-pill ea-pill-small ${
                  mode === "student" ? "ea-pill-active" : ""
                }`}
                onClick={() => setMode("student")}
              >
                🧑‍🎓 Student
              </button>
            </div>
          </div>
        </nav>

        <header className="ea-header">
          <h1 className="ea-title">
            {isTeacher
              ? "Make every lesson accessible."
              : "Learn from accessible lessons."}
          </h1>
          <p className="ea-subtitle">
            {isTeacher
              ? "Upload classroom materials and let EduAccess AI + Opus turn them into student-ready accessible lessons."
              : "Browse approved lessons adapted for your profile and language, then read or listen as you learn."}
          </p>
        </header>

        <main className="ea-main">
          {/* LEFT CARD */}
          <section className="ea-card ea-card-left">
            {isTeacher ? (
              <>
                <h2 className="ea-card-title">1 · Upload & Manage Lessons</h2>
                <p className="ea-card-text">
                  Choose an accessibility profile, upload a PDF or image, and
                  EduAccess AI prepares an adapted lesson. Opus can later review
                  and approve it in your workflow.
                </p>

                <form className="ea-form" onSubmit={handleTeacherSubmit}>
                  <label className="ea-label">Lesson title</label>
                  <input
                    className="ea-input"
                    type="text"
                    placeholder="e.g. Photosynthesis basics"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />

                  <label className="ea-label">Accessibility profile</label>
                  <div className="ea-pill-group">
                    <button
                      type="button"
                      className={`ea-pill ${
                        profile === "dyslexic" ? "ea-pill-active" : ""
                      }`}
                      onClick={() => setProfile("dyslexic")}
                    >
                      Dyslexic
                    </button>
                    <button
                      type="button"
                      className={`ea-pill ${
                        profile === "blind" ? "ea-pill-active" : ""
                      }`}
                      onClick={() => setProfile("blind")}
                    >
                      Blind
                    </button>
                  </div>

                  <label className="ea-label">Output language</label>
                  <div className="ea-pill-group">
                    <button
                      type="button"
                      className={`ea-pill ${
                        language === "en" ? "ea-pill-active" : ""
                      }`}
                      onClick={() => setLanguage("en")}
                    >
                      English
                    </button>
                    <button
                      type="button"
                      className={`ea-pill ${
                        language === "es" ? "ea-pill-active" : ""
                      }`}
                      onClick={() => setLanguage("es")}
                    >
                      Spanish
                    </button>
                  </div>

                  <label className="ea-label">
                    Upload material (PDF or image)
                  </label>
                  <label className="ea-dropzone">
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png,.webp"
                      onChange={handleFileChange}
                    />
                    <span className="ea-dropzone-icon">📄</span>
                    <span className="ea-dropzone-text">
                      {file ? file.name : "Click to choose a file"}
                    </span>
                  </label>

                  <button
                    className="ea-primary-btn"
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? "Processing…" : "Upload & Convert"}
                  </button>

                  {error && <p className="ea-error">{error}</p>}

                  <p className="ea-hint">
                    In a full Opus workflow, this lesson will go through AI +
                    human review before being marked as approved for students.
                  </p>
                </form>

                <h3 className="ea-section-heading">Your lessons</h3>
                {lessons.length === 0 ? (
                  <p className="ea-placeholder-sub">
                    You don't have any lessons yet. Upload your first one!
                  </p>
                ) : (
                  <ul className="ea-list ea-list-condensed">
                    {lessons.map((lesson) => (
                      <li
                        key={lesson.lesson_id}
                        className={`ea-list-item-clickable ${
                          activeLesson?.lesson_id === lesson.lesson_id
                            ? "ea-list-item-active"
                            : ""
                        }`}
                        onClick={() => setActiveLesson(lesson)}
                      >
                        <div className="ea-list-item-main">
                          <span className="ea-list-title">{lesson.title}</span>
                          <span className="ea-chip-mini">
                            {lesson.profile === "dyslexic"
                              ? "Dyslexia"
                              : "Blind"}
                            {" · "}
                            {lesson.language === "es" ? "Spanish" : "English"}
                          </span>
                        </div>
                        <span className={`ea-status ea-status-${lesson.status}`}>
                          {lesson.status}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </>
            ) : (
              <>
                <h2 className="ea-card-title">1 · Choose Your Learning Mode</h2>
                <p className="ea-card-text">
                  Pick your accessibility profile and language, then browse
                  lessons that your teachers and Opus have already approved for
                  you.
                </p>

                <label className="ea-label">Profile</label>
                <div className="ea-pill-group">
                  <button
                    type="button"
                    className={`ea-pill ${
                      studentProfile === "dyslexic" ? "ea-pill-active" : ""
                    }`}
                    onClick={() => setStudentProfile("dyslexic")}
                  >
                    Dyslexic
                  </button>
                  <button
                    type="button"
                    className={`ea-pill ${
                      studentProfile === "blind" ? "ea-pill-active" : ""
                    }`}
                    onClick={() => setStudentProfile("blind")}
                  >
                    Blind
                  </button>
                </div>

                <label className="ea-label">Language</label>
                <div className="ea-pill-group">
                  <button
                    type="button"
                    className={`ea-pill ${
                      studentLanguage === "en" ? "ea-pill-active" : ""
                    }`}
                    onClick={() => setStudentLanguage("en")}
                  >
                    English
                  </button>
                  <button
                    type="button"
                    className={`ea-pill ${
                      studentLanguage === "es" ? "ea-pill-active" : ""
                    }`}
                    onClick={() => setStudentLanguage("es")}
                  >
                    Spanish
                  </button>
                </div>

                <h3 className="ea-section-heading">Available lessons</h3>
                {lessons.length === 0 ? (
                  <p className="ea-placeholder-sub">
                    No approved lessons yet for this profile/language. Check
                    back soon!
                  </p>
                ) : (
                  <ul className="ea-list ea-list-condensed">
                    {lessons.map((lesson) => (
                      <li
                        key={lesson.lesson_id}
                        className={`ea-list-item-clickable ${
                          activeLesson?.lesson_id === lesson.lesson_id
                            ? "ea-list-item-active"
                            : ""
                        }`}
                        onClick={() => setActiveLesson(lesson)}
                      >
                        <div className="ea-list-item-main">
                          <span className="ea-list-title">{lesson.title}</span>
                          <span className="ea-chip-mini">
                            Level: {lesson.reading_level || "Unknown"}
                          </span>
                        </div>
                        <span className="ea-status ea-status-approved">
                          approved
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </section>

          {/* RIGHT CARD */}
          <section className="ea-card ea-card-right">
            <h2 className="ea-card-title">2 · Accessible Output</h2>

            {!activeLesson && (
              <div className="ea-placeholder">
                <p>Processed content will appear here.</p>
                <p className="ea-placeholder-sub">
                  {isTeacher
                    ? "Upload a lesson or select one from the list on the left."
                    : "Select a lesson from the left to start reading."}
                </p>
              </div>
            )}

            {activeLesson && (
              <div className="ea-output">
                <div className="ea-output-header">
                  <span className="ea-chip">
                    {activeLesson.profile === "dyslexic"
                      ? "Dyslexia mode"
                      : "Blind mode"}
                  </span>
                  <span className="ea-chip-secondary">
                    Reading level: {activeLesson.reading_level || "Unknown"}
                  </span>
                  <span className={`ea-status ea-status-${activeLesson.status}`}>
                    {activeLesson.status}
                  </span>
                </div>

                <div className="ea-output-actions">
                  <button
                    className="ea-secondary-btn"
                    type="button"
                    onClick={handleListen}
                  >
                    🔊 Listen
                  </button>
                </div>

                <h3 className="ea-section-heading">
                  {activeLesson.title || "Simplified text"}
                </h3>
                <p className="ea-accessible-text">
                  {activeLesson.simplified_text}
                </p>

                {activeLesson.bullet_summary?.length > 0 && (
                  <>
                    <h3 className="ea-section-heading">Key points</h3>
                    <ul className="ea-list">
                      {activeLesson.bullet_summary.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </>
                )}

                {isTeacher && activeLesson.audit_json && (
                  <>
                    <h3 className="ea-section-heading">Opus review audit</h3>
                    <pre className="ea-audit-block">
                      {JSON.stringify(activeLesson.audit_json, null, 2)}
                    </pre>
                  </>
                )}
              </div>
            )}
          </section>
        </main>

        <footer className="ea-footer">
          Built for the AI Genesis Hackathon · EduAccess AI · Gemini + Opus
        </footer>
      </div>
    </div>
  );
}

export default App;
