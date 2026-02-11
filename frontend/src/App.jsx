import { useState } from "react";
import { validateFiles } from "./api";
import "./styles.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [formNumber, setFormNumber] = useState("");

  function handleFileChange(e) {
    setPdfFile(e.target.files[0]);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!pdfFile || !formNumber.trim()) {
      alert("Please enter form number and upload PDF.");
      return;
    }

    // User message
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
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { sender: "bot", text: "❌ Validation failed. Please check backend." }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-wrapper">
      <h2 className="chat-title">🤖 AI Document Validation</h2>

      <div className="chat-container">
        <div className="chat-box">

          {messages.length === 0 && (
            <div className="empty-state">
              Enter the form to validate and upload the PDF.
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>

              {msg.text && <p>{msg.text}</p>}

              {msg.result && (
                <div className="result-block">
                  <h4>
                    {msg.result.summary?.failed === 0
                      ? "✅ Document Passed"
                      : "❌ Document Failed"}
                  </h4>

                  {/* Failed Fields */}
                  {msg.result.failed_fields?.length > 0 && (
                    <>
                      <p className="section-title">❌ Failed Fields</p>
                      <ul>
                        {msg.result.failed_fields.map((f, i) => (
                          <li key={i}>{f.tag}</li>
                        ))}
                      </ul>
                    </>
                  )}

                  {/* Passed Fields */}
                  {msg.result.passed_fields?.length > 0 && (
                    <>
                      <p className="section-title">✅ Passed Fields</p>
                      <ul>
                        {msg.result.passed_fields.map((f, i) => (
                          <li key={i}>{f.tag}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              )}

            </div>
          ))}

          {loading && (
            <div className="message bot">
              <p>🔎 Validating document...</p>
            </div>
          )}
        </div>

        {/* Upload + Form Input */}
        <form className="upload-panel" onSubmit={handleSubmit}>

          <div className="upload-group">
            <label>🔢 Enter the form to validate:</label>
            <input
              type="text"
              placeholder="e.g., DEF344"
              value={formNumber}
              onChange={(e) => setFormNumber(e.target.value)}
              required
            />
          </div>

          <div className="upload-group">
            <label>📄 Upload Filled Insurance Form (PDF)</label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              required
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Validating…" : "Validate"}
          </button>

        </form>
      </div>
    </div>
  );
}
