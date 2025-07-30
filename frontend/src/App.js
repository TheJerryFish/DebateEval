// frontend/src/App.js
import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import ResultPanel from "./components/ResultPanel";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);       // full final result
  const [progress, setProgress] = useState("");     // streaming messages
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setResult(null);
    setProgress("Starting analysis");

    const res = await fetch("http://localhost:5000/analyze", {
      method: "POST",
      body: formData,
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // keep incomplete line

      for (let line of lines) {
        if (line.startsWith("data: ")) {
          const msg = line.slice(6);

          if (msg.startsWith("DONE::")) {
            const jsonData = JSON.parse(msg.slice(6));
            setResult(jsonData);
            setLoading(false);
            setProgress("");
          } else {
            setProgress(msg);
          }
        }
      }
    }
  };

  return (
    <div className="App">
      <h1>DebateEval App</h1>
      <FileUpload onAnalyze={handleAnalyze} />

      {loading && (
        <div className="loading-msg">
          <span>{progress}</span>
          <span className="dots">
            <span>.</span>
            <span>.</span>
            <span>.</span>
          </span>
        </div>
      )}

      {result && <ResultPanel result={result} />}
    </div>
  );
}

export default App;