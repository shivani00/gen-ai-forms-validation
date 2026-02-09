import { useState } from "react";
import { validateFiles } from "./api";
import "./styles.css";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    const fd = new FormData(e.target);
    const res = await validateFiles(fd);
    setResult(res);
    setLoading(false);
  }

  return (
    <div className="card">
      <h2>📄 Insurance PDF Validator</h2>
      <p className="subtitle">
        Upload the filled PDF, layout specification, and expected JSON to validate insurance forms.
      </p>

      <form onSubmit={submit}>
        <div className="input-group">
          <label>📄 Insurance PDF (Filled Form)</label>
          <input type="file" name="pdf" required />
          <small>Example: insurance_forms.pdf</small>
        </div>

        <div className="input-group">
          <label>📝 Word Layout Spec (Positions Only)</label>
          <input type="file" name="word" required />
          <small>Example: ABC123_spec.docx</small>
        </div>

        <div className="input-group">
          <label>🧾 Expected Data (JSON)</label>
          <input type="file" name="data" required />
          <small>Example: ABC123.json</small>
        </div>

        <button disabled={loading}>
          {loading ? "Validating…" : "Validate Document"}
        </button>
      </form>

      {result && (
        <div className="results">
          <h3>✅ Validation Results</h3>

          {/* {result.results.map((r, i) => (
            <div key={i} className="result-card">
              <div className="result-header">
                <strong>{r.tag}</strong>
                <span className={`status ${r.status === "PASS" ? "pass" : "fail"}`}>
                  {r.status}
                </span>
              </div>

              {r.confidence !== undefined && (
                <>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${Math.round(r.confidence * 100)}%` }}
                    />
                  </div>
                  <small>Confidence: {Math.round(r.confidence * 100)}%</small>
                </>
              )}

              <p className="explanation">{r.explanation}</p>
            </div>
          ))} */}
          {result.results.map((r, i) => (
            <div key={i} className="result-card">
              <div className="result-header">
                <strong>{r.tag}</strong>
                <span className={`status ${r.status === "PASS" ? "pass" : "fail"}`}>
                  {r.status}
                </span>
              </div>

              {/* ✅ NEW: Show Expected and Extracted */}
              <div className="value-section">
                <p>
                  <strong>Expected:</strong>{" "}
                  <span className="expected">{r.expected || "—"}</span>
                </p>

                <p>
                  <strong>Extracted:</strong>{" "}
                  <span className="extracted">{r.extracted || "—"}</span>
                </p>
              </div>

              {r.confidence !== undefined && (
                <>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${Math.round(r.confidence * 100)}%` }}
                    />
                  </div>
                  {/* <small>Confidence: {Math.round(r.confidence * 100)}%</small> */}
                </>
              )}

              <p className="explanation">{r.explanation}</p>
            </div>
          ))}

        </div>
      )}
    </div>
  );
}
