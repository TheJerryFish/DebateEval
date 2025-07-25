import React, { useState } from "react";

const FileUpload = ({ onAnalyze }) => {
  const [file, setFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (file) onAnalyze(file);
  };

  return (
    <div className="upload-section">
      <input
        type="file"
        accept=".mp3"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button type="submit" onClick={handleSubmit}>
        Analyze
      </button>
    </div>
  );
};

export default FileUpload;