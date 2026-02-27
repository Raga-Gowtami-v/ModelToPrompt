import React from "react";
import { Link } from "react-router-dom";

export default function LandingPage() {
  return (
    <div className="landing-page">
      <h1>Secure Data & Automated ML Pipeline</h1>
      <p className="subtitle">
        Privacy-first PII detection and prompt-driven ML model training
      </p>

      <div className="landing-actions">
        <Link to="/sanitize" className="landing-card">
          <div className="icon">&#128274;</div>
          <h2>Sanitize Dataset</h2>
          <p>
            Upload a document, CSV, or image to detect and mask personally
            identifiable information.
          </p>
        </Link>

        <Link to="/train" className="landing-card">
          <div className="icon">&#129302;</div>
          <h2>Train Model from Dataset</h2>
          <p>
            Upload a sanitized CSV with a natural language prompt to
            automatically train and evaluate an ML model.
          </p>
        </Link>
      </div>
    </div>
  );
}
