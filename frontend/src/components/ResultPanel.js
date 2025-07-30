import React from "react";

const ResultPanel = ({ result }) => {
  if (!result) return null; // nothing to render if no result yet

  const tableData = result.table_data || []; // fallback to empty array

  return (
    <div className="result-panel">
      <div className="section" style={{ marginBottom: "2rem" }}>
        <h2>Transcript</h2>
        <pre>{result.transcript || "No transcript available."}</pre>
      </div>

      <div className="result-grid">
        <div className="section">
          <h2>Tone Progression</h2>
          {result.tone_plot ? (
            <img
              src={`http://localhost:5000${result.tone_plot}`}
              alt="Tone Plot"
            />
          ) : (
            <p>No tone plot available.</p>
          )}
        </div>

        <div className="section">
          <h2>Smoothed Tone</h2>
          {result.smoothed_plot ? (
            <img
              src={`http://localhost:5000${result.smoothed_plot}`}
              alt="Smoothed Plot"
            />
          ) : (
            <p>No smoothed plot available.</p>
          )}
        </div>
      </div>

      <div className="section" style={{ marginTop: "2rem" }}>
        <h2>Tone Table</h2>
        <div className="table-wrapper">
          {tableData.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Speaker</th>
                  <th>Start-End (s)</th>
                  <th>Transcript</th>
                  <th>Tone</th>
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, idx) => (
                  <tr key={idx}>
                    <td>{row.speaker || "-"}</td>
                    <td>{row.start_end || "-"}</td>
                    <td>{row.transcript || "-"}</td>
                    <td>{row.tone || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No tone table data available.</p>
          )}
        </div>
      </div>

      <div className="section" style={{ marginTop: "2rem" }}>
        <h2>LLM Feedback</h2>
        <p>{result.feedback || "No feedback available."}</p>
      </div>

      <div className="section" style={{ marginTop: "2rem" }}>
        <h2>LLM Transcript Feedback</h2>
        <p>{result.transcript_feedback || "No transcript feedback available."}</p>
      </div>
    </div>
  );
};

export default ResultPanel;