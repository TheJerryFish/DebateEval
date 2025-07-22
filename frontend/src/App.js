// frontend/src/App.js
import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import ResultPanel from "./components/ResultPanel";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Analysis failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>DebateEval App</h1>
      <FileUpload onAnalyze={handleAnalyze} />
      {loading && <p>Analyzing audio...</p>}
      {result && <ResultPanel result={result} />}
    </div>
  );
}

export default App;