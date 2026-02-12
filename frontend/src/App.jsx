import { useState } from "react";
import { validateForm } from "./api";
import "./styles.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [pdfFile, setPdfFile] = useState(null);
  const [formId, setFormId] = useState("FR-01");
  const [loading, setLoading] = useState(false);

  const forms = ["FR-01", "FR-02", "FR-03"];

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
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Validation failed. Please try again." },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="header">
        🤖 Insurance Visual Validation Agent
      </div>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.text && <p>{msg.text}</p>}

            {msg.data && msg.data.results && (
              <div className="result-card">
                <h3
                  className={
                    msg.data.overall_status === "PASS"
                      ? "overall-pass"
                      : "overall-fail"
                  }
                >
                  Overall: {msg.data.overall_status}
                </h3>

                {msg.data.results.map((r, index) => (
                  <div
                    key={index}
                    className={`field-card ${
                      r.status === "PASS" ? "pass" : "fail"
                    }`}
                  >
                    <div>
                      <strong>{r.json_path}</strong>
                    </div>

                    <div>Status: {r.status}</div>
                    <div>Expected: {r.expected_value}</div>
                    <div>Actual: {r.actual_value || "Not Found"}</div>
                    <div>
                      Value Match:{" "}
                      {r.value_match ? "✅ Yes" : "❌ No"}
                    </div>
                    <div>
                      Position Match:{" "}
                      {r.position_match ? "✅ Yes" : "❌ No"}
                    </div>
                    <div>Reason: {r.reason}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && <div className="message bot">Processing...</div>}
      </div>

      <div className="input-panel">
        <select value={formId} onChange={(e) => setFormId(e.target.value)}>
          {forms.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>

        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setPdfFile(e.target.files[0])}
        />

        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Validating..." : "Validate"}
        </button>
      </div>
    </div>
  );
}