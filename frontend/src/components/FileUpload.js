// frontend/src/components/FileUpload.js
import React, { useState } from "react";

const FileUpload = ({ onAnalyze }) => {
  const [file, setFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (file) onAnalyze(file);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" accept=".mp3" onChange={(e) => setFile(e.target.files[0])} />
      <button type="submit">Analyze</button>
    </form>
  );
};

export default FileUpload;