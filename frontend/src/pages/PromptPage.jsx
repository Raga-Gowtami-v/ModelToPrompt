import React, { useState } from "react";
import FileUploader from "../components/FileUploader";
import { trainModel } from "../services/api";

export default function PromptPage() {
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTrain = async () => {
    if (!file || !prompt.trim()) {
      setError("Please upload a CSV file and enter a prompt.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await trainModel(file, prompt);
      setResult(data);
    } catch (err) {
      setError(err.message || "Training failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prompt-page">
      <h1>Model Training</h1>
      <p>Upload a CSV file and describe what you want to predict.</p>

      <FileUploader
        onUpload={(f) => setFile(f)}
        accept=".csv"
        loading={false}
      />

      {file && <p className="file-selected">Selected: {file.name}</p>}

      <div className="prompt-input">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g. Classify the 'species' column based on other features"
          rows={4}
        />
        <button onClick={handleTrain} disabled={loading}>
          {loading ? "Training..." : "Train Model"}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {result && (
        <div className="train-result">
          <h2>Training Complete</h2>
          <p>Model ID: {result.model_id}</p>
          <p>Task: {result.task_type}</p>
          <p>Target: {result.target_column}</p>
          <p>Score: {result.score}</p>
          <a
            href={`/api/model/download/${result.model_id}`}
            className="download-btn"
          >
            Download .pkl
          </a>
        </div>
      )}
    </div>
  );
}
