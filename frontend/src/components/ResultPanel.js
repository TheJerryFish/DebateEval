import React from "react";

const ResultPanel = ({ result }) => {
  return (
    <div className="result-panel">
      <div className="section" style={{ marginBottom: "2rem" }}>
        <h2>Transcript</h2>
        <pre>{result.transcript}</pre>
      </div>

      <div className="result-grid">
        <div className="section">
          <h2>Tone Progression</h2>
          <img
            src={`http://localhost:5000${result.tone_plot}`}
            alt="Tone Plot"
          />
        </div>

        <div className="section">
          <h2>Smoothed Tone</h2>
          <img
            src={`http://localhost:5000${result.smoothed_plot}`}
            alt="Smoothed Plot"
          />
        </div>
      </div>

      <div className="section" style={{ marginTop: "2rem" }}>
        <h2>Tone Table</h2>
        <div className="table-wrapper">
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
              {result.table_data.map((row, idx) => (
                <tr key={idx}>
                  <td>{row.speaker}</td>
                  <td>{row.start_end}</td>
                  <td>{row.transcript}</td>
                  <td>{row.tone}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="section" style={{ marginTop: "2rem" }}>
        <h2>LLM Feedback</h2>
        <p>{result.feedback}</p>
      </div>

      <div className="section" style={{ marginTop: "2rem" }}>
        <h2>LLM Transcript Feedback</h2>
        <p>{result.transcript_feedback}</p>
      </div>
    </div>
    
  );
};

export default ResultPanel;