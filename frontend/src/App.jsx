import { useState } from "react";
import { validateForm } from "./api";
import {
  CheckCircle,
  XCircle,
  FileText,
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

      // Store entire validation session in history
      setSummaryHistory((prev) => [
        {
          ...res,
          timestamp: new Date().toLocaleTimeString(),
        },
        ...prev,
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Validation failed. Please try again." },
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
            <div className="message bot">
              <div className="bubble loading">
                🔄 Processing validation...
              </div>
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
          <span>Validation History</span>
        </div>

        {summaryHistory.length === 0 ? (
          <div className="empty-summary">
            No validations yet.
          </div>
        ) : (
          summaryHistory.map((item, index) => (
            <SummaryCard key={index} data={item} />
          ))
        )}
      </div>
    </div>
  );
}

/* ================= MULTI-FORM SESSION VIEW ================= */

function ValidationSession({ data }) {
  if (data.status !== "completed") {
    return <div className="bubble">Validation failed.</div>;
  }

  return (
    <div className="result-card">
      <div className="overall overall-pass">
        <CheckCircle size={20} />
        Total Forms Detected: {data.total_forms}
      </div>

      {Array.isArray(data.results) &&
  data.results.map((form, index) => (
    <FormResult key={index} form={form} />
  ))}

    </div>
  );
}

function FormResult({ form }) {
  const [expanded, setExpanded] = useState(false);

  if (form.status !== "completed") {
    return (
      <div className="form-card fail">
        <div className="form-header">
          <strong>{form.form_id}</strong>
        </div>
        <div>{form.error}</div>
      </div>
    );
  }

  const results =
  form?.validation && Array.isArray(form.validation.results)
    ? form.validation.results
    : [];

  const total = results.length;
  const passed = results.filter((r) => r.status === "PASS").length;
  const failed = total - passed;
  const percentage = total > 0 ? Math.round((passed / total) * 100) : 0;

  const isPass = percentage === 100;

  return (
    <div
      className={`form-card ${isPass ? "glow-pass" : "glow-fail"}`}
    >
      {/* HEADER */}
      <div
        className="form-header clickable"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="form-title">
          {isPass ? (
            <CheckCircle size={18} />
          ) : (
            <XCircle size={18} />
          )}
          <strong>{form.form_id}</strong>
        </div>

        <div className="form-metrics">
          <span>{percentage}%</span>
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>
      </div>

      {/* PROGRESS BAR */}
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="mini-stats">
        <span className="pass-text">✔ {passed}</span>
        <span className="fail-text">✖ {failed}</span>
        <span>Total: {total}</span>
      </div>

      {/* COLLAPSIBLE CONTENT */}
      {expanded && (
  <div className="form-details">
    {results.map((r, index) => (
      <div
        key={index}
        className={`field-row ${
          r.status === "PASS" ? "pass" : "fail"
        }`}
      >
        <div className="field-left">
          <strong>{r.json_path}</strong>
          <div className="field-reason">{r.reason}</div>
        </div>

        <div className="field-right">
          <div>{r.status}</div>
          <div className="small-text">
            Expected: {r.expected_value || "—"}
          </div>
          <div className="small-text">
            Actual: {r.actual_value || "—"}
          </div>
        </div>
      </div>
    ))}
  </div>
)}

    </div>
  );
}

/* ================= SUMMARY CARD ================= */

function SummaryCard({ data }) {
  return (
    <div className="summary-card glow-pass">
      <div className="summary-header">
        <span className="summary-form">
          Forms: {data.total_forms}
        </span>
        <span className="summary-time">{data.timestamp}</span>
      </div>

      <div className="summary-status pass">
        Completed
      </div>
    </div>
  );
}
