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
} from "lucide-react";
import "./styles.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [pdfFile, setPdfFile] = useState(null);
  const [formId, setFormId] = useState("FR-01");
  const [loading, setLoading] = useState(false);

  // 🔥 NEW: store validation history
  const [summaryHistory, setSummaryHistory] = useState([]);

  const forms = ["FR-01", "FR-02", "FR-34"];

  const handleSubmit = async () => {
    if (!pdfFile) {
      alert("Please upload a PDF file.");
      return;
    }

    setMessages((prev) => [
      ...prev,
      { role: "user", text: `Validate ${formId}` },
    ]);

    setLoading(true);

    const fd = new FormData();
    fd.append("pdf", pdfFile);
    fd.append("form_id", formId);

    try {
      const res = await validateForm(fd);

      setMessages((prev) => [
        ...prev,
        { role: "bot", data: res.validation },
      ]);

      // 🔥 Store summary instead of replacing
      setSummaryHistory((prev) => [
        {
          formId,
          ...res.validation,
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
      {/* LEFT MAIN PANEL */}
      <div className="app-container">
        <div className="header">
          <ShieldCheck size={28} />
          <span>Insurance Forms Validation Agent</span>
        </div>

        <div className="chat-box">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.text && <div className="bubble">{msg.text}</div>}

              {msg.data && <ValidationResults data={msg.data} />}
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
          <select
            value={formId}
            onChange={(e) => setFormId(e.target.value)}
          >
            {forms.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>

          <label className="file-upload">
            <Upload size={16} />
            {pdfFile ? pdfFile.name : "Upload PDF"}
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

      {/* RIGHT SUMMARY HISTORY PANEL */}
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

/* ================= VALIDATION RESULT ================= */

function ValidationResults({ data }) {
  return (
    <div className="result-card">
      <div
        className={`overall ${
          data.overall_status === "PASS"
            ? "overall-pass"
            : "overall-fail"
        }`}
      >
        {data.overall_status === "PASS" ? (
          <CheckCircle size={20} />
        ) : (
          <XCircle size={20} />
        )}
        Overall Status: {data.overall_status}
      </div>

      {data.results.map((r, index) => (
        <div
          key={index}
          className={`field-card ${
            r.status === "PASS" ? "pass" : "fail"
          }`}
        >
          <div className="field-header">
            <FileText size={16} />
            <strong>{r.json_path}</strong>
          </div>

          <div className="field-grid">
            <div>Expected</div>
            <div>{r.expected_value}</div>

            <div>Value from Form PDF</div>
            <div>{r.actual_value || "Not Found"}</div>

            <div>Value Match</div>
            <div>{r.value_match ? "✅" : "❌"}</div>

            <div>Position Match</div>
            <div>{r.position_match ? "✅" : "❌"}</div>

            <div>Reason</div>
            <div>{r.reason}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ================= SUMMARY CARD ================= */

function SummaryCard({ data }) {
  const total = data.results.length;
  const passed = data.results.filter((r) => r.status === "PASS").length;
  const failed = total - passed;
  const percentage = Math.round((passed / total) * 100);

  return (
    <div
      className={`summary-card ${
        data.overall_status === "PASS" ? "glow-pass" : "glow-fail"
      }`}
    >
      <div className="summary-header">
        <span className="summary-form">
          Form: {data.formId}
        </span>
        <span className="summary-time">{data.timestamp}</span>
      </div>

      <div
        className={`summary-status ${
          data.overall_status === "PASS" ? "pass" : "fail"
        }`}
      >
        {data.overall_status}
      </div>

      <div className="metric-row">
        <div>Total</div>
        <div>{total}</div>
      </div>

      <div className="metric-row pass-text">
        <div>Passed</div>
        <div>{passed}</div>
      </div>

      <div className="metric-row fail-text">
        <div>Failed</div>
        <div>{failed}</div>
      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="percentage">
        {percentage}% Success Rate
      </div>
    </div>
  );
}