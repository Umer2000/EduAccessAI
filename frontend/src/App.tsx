import { useState } from "react";
import "./App.css";

type ApiResult = {
  lesson_id: string;
  profile: string;
  simplified_text: string;
  bullet_summary: string[];
  reading_level: string;
};

function App() {
  const [profile, setProfile] = useState<"dyslexic" | "blind">("dyslexic");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ApiResult | null>(null);
  const [dark, setDark] = useState(false);
  const [language, setLanguage] = useState<"en" | "ur">("en");
  


  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setResult(null);
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    } else {
      setFile(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!file) {
      setError("Please upload a file first.");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("profile", profile);
      formData.append("language", language); // <-- send selected language

      const res = await fetch("http://localhost:8000/api/materials/convert", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = (await res.json()) as ApiResult;
      setResult(data);
    } catch (err: any) {
      console.error(err);
      setError("Something went wrong while processing the file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleListen = () => {
    if (!result) return;
    const utterance = new SpeechSynthesisUtterance(result.simplified_text);
    utterance.rate = 0.95;
    speechSynthesis.speak(utterance);
  };

  return (
    <div className={`ea-root ${dark ? "ea-dark" : ""}`}>
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
                Accessible learning, powered by AI.
              </span>
            </div>
          </div>
          <div className="ea-navbar-right">
            <button
              type="button"
              className="ea-theme-toggle"
              onClick={() => setDark((prev) => !prev)}
            >
              <span className="ea-theme-icon">{dark ? "🌙" : "☀️"}</span>
              <span className="ea-theme-label">
                {dark ? "Dark" : "Light"} mode
              </span>
            </button>
          </div>
        </nav>

        <header className="ea-header">
          <h1 className="ea-title">Make every lesson accessible.</h1>
          <p className="ea-subtitle">
            Upload classroom materials and instantly generate dyslexia-friendly
            or screen-reader-ready versions with teacher-in-the-loop control.
          </p>
        </header>

        <main className="ea-main">
          {/* LEFT CARD */}
          <section className="ea-card ea-card-left">
            <h2 className="ea-card-title">1 · Upload & Configure</h2>
            <p className="ea-card-text">
              Choose an accessibility profile, upload a PDF or image, and let
              EduAccess AI prepare an easier-to-consume version for your learner.
            </p>

            <form className="ea-form" onSubmit={handleSubmit}>
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
                    language === "ur" ? "ea-pill-active" : ""
                  }`}
                  onClick={() => setLanguage("ur")}
                >
                  Urdu (beta)
                </button>
              </div>

              <label className="ea-label">Upload material (PDF or image)</label>
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
                {loading ? "Processing…" : "Make Accessible"}
              </button>

              {error && <p className="ea-error">{error}</p>}

              <p className="ea-hint">
                EduAccess AI is a prototype. Educators can always review and edit
                the AI output before sharing.
              </p>
            </form>
          </section>

          {/* RIGHT CARD */}
          <section className="ea-card ea-card-right">
            <h2 className="ea-card-title">2 · Accessible Output</h2>

            {!result && !loading && (
              <div className="ea-placeholder">
                <p>Processed content will appear here.</p>
                <p className="ea-placeholder-sub">
                  Start by uploading a file on the left to see how EduAccess
                  transforms it.
                </p>
              </div>
            )}

            {loading && (
              <div className="ea-loader">
                <div className="ea-spinner" />
                <p>AI is preparing an accessible version…</p>
              </div>
            )}

            {result && !loading && (
              <div className="ea-output">
                <div className="ea-output-header">
                  <span className="ea-chip">
                    {result.profile === "dyslexic"
                      ? "Dyslexia mode"
                      : "Blind mode"}
                  </span>
                  <span className="ea-chip-secondary">
                    Reading level: {result.reading_level}
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

                <h3 className="ea-section-heading">Simplified text</h3>
                <p className="ea-accessible-text">
                  {result.simplified_text}
                </p>

                {result.bullet_summary?.length > 0 && (
                  <>
                    <h3 className="ea-section-heading">Key points</h3>
                    <ul className="ea-list">
                      {result.bullet_summary.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}
          </section>
        </main>

        <footer className="ea-footer">
          Built for the AI Genesis Hackathon · EduAccess AI
        </footer>
      </div>
    </div>
  );
}

export default App;
