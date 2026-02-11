import { useState, useEffect } from "react";
import { validateFiles } from "./api";
import "./styles.css";

import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
ChartJS.register(ArcElement, Tooltip, Legend);

/* =========================================
   Typing Animation Component
========================================= */
function TypingMessage({ text }) {
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i));
      i++;
      if (i > text.length) clearInterval(interval);
    }, 20);

    return () => clearInterval(interval);
  }, [text]);

  return <p>{displayed}</p>;
}

/* =========================================
   Main App
========================================= */
export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [formNumber, setFormNumber] = useState("ABC123");
  const [darkMode, setDarkMode] = useState(false);

  const forms = ["ABC123", "DEF344", "GHI567", "JKL890", "MNO222"];

  /* =========================================
     File Change
  ========================================= */
  function handleFileChange(e) {
    setPdfFile(e.target.files[0]);
  }

  /* =========================================
     Submit Validation
  ========================================= */
  async function handleSubmit(e) {
    e.preventDefault();

    if (!pdfFile) {
      alert("Please upload PDF.");
      return;
    }

    setMessages(prev => [
      ...prev,
      { sender: "user", text: `📤 Validate Form: ${formNumber}` }
    ]);

    setLoading(true);

    const fd = new FormData();
    fd.append("pdf", pdfFile);
    fd.append("form_id", formNumber);

    try {
      const res = await validateFiles(fd);

      setMessages(prev => [
        ...prev,
        { sender: "bot", result: res }
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        { sender: "bot", text: "❌ Validation failed. Please check backend." }
      ]);
    } finally {
      setLoading(false);
      setPdfFile(null); // reset file input
    }
  }

  /* =========================================
     New Validation (Clean Reset)
  ========================================= */
  function handleNewValidation() {
    setMessages([]);
    setPdfFile(null);
  }

  /* =========================================
     Dark / Light Mode Toggle
  ========================================= */
  function handleThemeToggle() {
    setDarkMode(prev => !prev);
    document.body.classList.toggle("dark-mode");
  }

  /* =========================================
     UI
  ========================================= */
  return (
    <div className="chat-wrapper">

      {/* Dark Mode Toggle */}
      <button className="dark-toggle" onClick={handleThemeToggle}>
        {darkMode ? "🌞 Light" : "🌙 Dark"}
      </button>

      <div className="chat-title">
        ✨ Insurance Form Validator
      </div>

      <div className="chat-container">

        {/* ================= CHAT SECTION ================= */}
        <div className="chat-box">

          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>

              {/* Text Messages */}
              {msg.text &&
                (msg.sender === "bot" ? (
                  <TypingMessage text={msg.text} />
                ) : (
                  <p>{msg.text}</p>
                ))}

              {/* ================= RESULT CARD ================= */}
              {msg.result && (
                <div className={`result-card ${darkMode ? "dark-result" : ""}`}>

                  {/* STATUS */}
                  <div className="status-header">
                    <span
                      className={`status-badge ${
                        msg.result.summary?.failed === 0 ? "success" : "fail"
                      }`}
                    >
                      {msg.result.summary?.failed === 0
                        ? "✅ FORM VALIDATION PASSED"
                        : "❌ FORM VALIDATION FAILED"}
                    </span>
                  </div>

                  {/* SUMMARY GRID */}
                  <div className="summary-grid">
                    <div>
                      Total<br />
                      <strong>{msg.result.summary?.total_fields}</strong>
                    </div>
                    <div>
                      Passed<br />
                      <strong>{msg.result.summary?.passed}</strong>
                    </div>
                    <div>
                      Failed<br />
                      <strong>{msg.result.summary?.failed}</strong>
                    </div>
                  </div>

                  {/* DONUT CHART */}
                  <div className="chart-wrapper">
                    <Doughnut
                      data={{
                        labels: ["Passed", "Failed"],
                        datasets: [
                          {
                            data: [
                              msg.result.summary?.passed || 0,
                              msg.result.summary?.failed || 0
                            ],
                            backgroundColor: ["#16a34a", "#dc2626"]
                          }
                        ]
                      }}
                      options={{
                        cutout: "65%",
                        plugins: { legend: { position: "bottom" } }
                      }}
                    />
                  </div>

                  {/* FAILED FIELDS */}
                  {msg.result.failed_fields?.length > 0 && (
                    <div className="failed-section">
                      <h4>❌ Failed Fields</h4>

                      {msg.result.failed_fields.map((f, i) => (
                        <div key={i} className="field-card fail-card">

                          <div className="field-header">
                            <strong>{f.tag}</strong>
                            <span className="fail-text">FAILED</span>
                          </div>

                          <div className="value-section">
                            <p>
                              <strong>Expected:</strong>{" "}
                              {f.expected || "—"}
                            </p>
                            <p>
                              <strong>Extracted:</strong>{" "}
                              {f.extracted || "—"}
                            </p>
                          </div>

                          {f.reason && (
                            <p className="reason">
                              <strong>Reason:</strong> {f.reason}
                            </p>
                          )}

                          {f.confidence !== undefined && (
                            <div className="confidence-wrapper">
                              <div className="confidence-bar">
                                <div
                                  className="confidence-fill"
                                  style={{
                                    width: `${Math.round(f.confidence * 100)}%`
                                  }}
                                />
                              </div>
                              <small>
                                Confidence: {Math.round(f.confidence * 100)}%
                              </small>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* PASSED FIELDS */}
                  {msg.result.passed_fields?.length > 0 && (
                    <div className="passed-section">
                      <h4>✅ Passed Fields</h4>

                      {msg.result.passed_fields.map((f, i) => (
                        <div key={i} className="field-card pass-card">
                          <div className="field-header">
                            <strong>{f.tag}</strong>
                            <span className="pass-text">PASSED</span>
                          </div>
                          <div className="value-section">
                            <p><strong>Expected:</strong> {f.expected || "—"}</p>
                            <p><strong>Extracted:</strong> {f.extracted || "—"}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                </div>
              )}
            </div>
          ))}

          {/* Loading State */}
          {loading && (
            <div className="message bot">
              <TypingMessage text="🔎 Running OCR + Validation + AI checks..." />
            </div>
          )}

          {/* NEW VALIDATION BUTTON */}
          {messages.length > 0 && !loading && (
            <div className="new-validation-wrapper">
              <button
                className="new-validation-btn"
                onClick={handleNewValidation}
              >
                🔄 New Validation
              </button>
            </div>
          )}
        </div>

        {/* ================= FORM PANEL ================= */}
        <form className="upload-panel" onSubmit={handleSubmit}>

          <div className="upload-group">
            <label>📑 Select Form</label>
            <select
              value={formNumber}
              onChange={(e) => setFormNumber(e.target.value)}
            >
              {forms.map((form, i) => (
                <option key={i} value={form}>{form}</option>
              ))}
            </select>
          </div>

          <div className="upload-group">
            <label>📄 Upload Filled Form (PDF)</label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              key={pdfFile ? pdfFile.name : "empty"}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="upload-button"
          >
            {loading ? "Validating…" : "Validate Form"}
          </button>

        </form>

      </div>
    </div>
  );
}
