import React, { useState } from "react";
import FileUploader from "../components/FileUploader";
import RedactionViewer from "../components/RedactionViewer";
import RiskMeter from "../components/RiskMeter";
import { scanFile } from "../services/api";

export default function UploadPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const data = await scanFile(file);
      setResult(data);
    } catch (err) {
      setError(err.message || "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <h1>PII Scanner</h1>
      <p>Upload a document, image, or CSV to detect and mask PII data.</p>

      <FileUploader onUpload={handleUpload} loading={loading} />

      {error && <div className="error-message">{error}</div>}

      {result && (
        <div className="results">
          <RiskMeter risk={result.risk} />
          <RedactionViewer
            maskedText={result.masked_text}
            detections={result.detections}
          />
        </div>
      )}
    </div>
  );
}
