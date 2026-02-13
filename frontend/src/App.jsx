import { useState } from "react";
import { validateForm } from "./api";
import {
  CheckCircle,
  XCircle,
  ShieldCheck,
  Upload,
  Send,
  Layers,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

import "./styles.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [summaryHistory, setSummaryHistory] = useState([]);

  const handleSubmit = async () => {
    if (!pdfFile) {
      alert("Please upload a PDF file.");
      return;
    }

    setMessages((prev) => [
      ...prev,
      { role: "user", text: "Validate uploaded policy document" },
    ]);

    setLoading(true);

    const fd = new FormData();
    fd.append("pdf", pdfFile);

    try {
      const res = await validateForm(fd);

      setMessages((prev) => [
        ...prev,
        { role: "bot", data: res },
      ]);

      setSummaryHistory((prev) => [
        { ...res, timestamp: new Date().toLocaleTimeString() },
        ...prev,
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Validation failed." },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="layout">
      {/* LEFT PANEL */}
      <div className="app-container">
        <div className="header">
          <ShieldCheck size={28} />
          <span>Insurance Policy Validation Agent</span>
        </div>

        <div className="chat-box">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.text && <div className="bubble">{msg.text}</div>}
              {msg.data && <ValidationSession data={msg.data} />}
            </div>
          ))}

          {loading && (
            <div className="bubble loading">
              🔄 Processing validation...
            </div>
          )}
        </div>

        <div className="input-panel">
          <label className="file-upload">
            <Upload size={16} />
            {pdfFile ? pdfFile.name : "Upload Policy PDF"}
            <input
              type="file"
              accept=".pdf"
              hidden
              onChange={(e) => setPdfFile(e.target.files[0])}
            />
          </label>

          <button onClick={handleSubmit} disabled={loading}>
            <Send size={16} />
            {loading ? "Validating..." : "Validate"}
          </button>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="summary-panel">
        <div className="summary-title">
          <Layers size={18} />
          <span>Forms Summary</span>
        </div>

        {summaryHistory.length === 0 ? (
          <div className="empty-summary">No validations yet.</div>
        ) : (
          summaryHistory.map((session, index) =>
            session.results.map((form, idx) => (
              <SideFormCard key={`${index}-${idx}`} form={form} />
            ))
          )
        )}
      </div>
    </div>
  );
}

/* ================= SESSION ================= */

function ValidationSession({ data }) {
  if (data.status !== "completed") {
    return <div className="bubble">Validation failed.</div>;
  }

  return (
    <div className="result-card">
      {data.results.map((form, index) => (
        <FormResult key={index} form={form} />
      ))}
    </div>
  );
}

/* ================= FORM RESULT ================= */

function FormResult({ form }) {
  const [expanded, setExpanded] = useState(true);

  if (form.status !== "completed") {
    return (
      <div className="form-card fail">
        <div className="form-id">{form.form_id}</div>
        <div>{form.error}</div>
      </div>
    );
  }

  const results = form.validation?.results || [];
  const total = results.length;
  const passed = results.filter((r) => r.status === "PASS").length;
  const failed = total - passed;
  const percentage = total ? Math.round((passed / total) * 100) : 0;
  const isPass = percentage === 100;

  return (
    <div className={`form-card ${isPass ? "glow-pass" : "glow-fail"}`}>
      {/* HEADER */}
      <div
        className="form-header clickable"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="form-title">
          {isPass ? <CheckCircle size={18} /> : <XCircle size={18} />}
          <span className="form-id">{form.form_id}</span>
        </div>

        <div className="form-metrics">
          {percentage}% {expanded ? <ChevronUp size={18}/> : <ChevronDown size={18}/>}
        </div>
      </div>

      {/* STATS */}
      <div className="mini-stats">
        <span className="pass-text">✔ {passed}</span>
        <span className="fail-text">✖ {failed}</span>
        <span>Total: {total}</span>
      </div>

      {/* FIELD DETAILS */}
      {expanded && (
        <div className="form-details">
          {results.map((r, index) => (
            <div
              key={index}
              className={`field-block ${
                r.status === "PASS" ? "pass" : "fail"
              }`}
            >
              <div className="field-row">
                <span>Expected:</span>
                <span>{r.expected_value || "—"}</span>
              </div>

              <div className="field-row">
                <span>Value from PDF:</span>
                <span>{r.actual_value || "—"}</span>
              </div>

              <div className="field-row">
                <span>Value Match:</span>
                <span>{r.value_match ? "✔" : "✖"}</span>
              </div>

              <div className="field-row">
                <span>Position Match:</span>
                <span>{r.position_match ? "✔" : "✖"}</span>
              </div>

              <div className="field-reason">
                Reason: {r.reason}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ================= RIGHT SUMMARY CARD ================= */

function SideFormCard({ form }) {
  if (form.status !== "completed") return null;

  const results = form.validation?.results || [];
  const total = results.length;
  const passed = results.filter((r) => r.status === "PASS").length;
  const failed = total - passed;
  const percentage = total ? Math.round((passed / total) * 100) : 0;
  const isPass = percentage === 100;

  return (
    <div className={`side-card ${isPass ? "glow-pass" : "glow-fail"}`}>
      <div className="side-header">
        <strong>{form.form_id}</strong>
        <span className={`badge ${isPass ? "pass" : "fail"}`}>
          {isPass ? "PASS" : "FAIL"}
        </span>
      </div>

      <div className="side-stats">
        <div>✔ {passed}</div>
        <div>✖ {failed}</div>
        <div>Total: {total}</div>
      </div>

      <div className="side-progress">
        <div
          className="side-progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="side-percentage">
        {percentage}% Success Rate
      </div>
    </div>
  );
}