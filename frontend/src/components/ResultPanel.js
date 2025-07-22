// frontend/src/components/ResultPanel.js
import React from "react";

const ResultPanel = ({ result }) => {
  return (
    <div>
      <h2>Transcript</h2>
      <pre>{result.transcript}</pre>

      <h2>Tone Progression</h2>
      <img src={`http://localhost:5000${result.tone_plot}`} alt="Tone Plot" width="100%" />

      <h2>Smoothed Tone</h2>
      <img src={`http://localhost:5000${result.smoothed_plot}`} alt="Smoothed Plot" width="100%" />

      <h2>Tone Table</h2>
      <pre>{result.table}</pre>
    </div>
  );
};

export default ResultPanel;