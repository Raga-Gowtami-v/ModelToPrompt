import React from "react";

const LEVEL_COLORS = {
  LOW: "#4caf50",
  MEDIUM: "#ff9800",
  HIGH: "#f44336",
};

export default function RiskMeter({ risk }) {
  if (!risk) return null;

  const color = LEVEL_COLORS[risk.level] || "#999";
  const percentage = Math.round(risk.score * 100);

  return (
    <div className="risk-meter">
      <h3>Risk Assessment</h3>
      <div className="meter-bar">
        <div
          className="meter-fill"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
      <p className="risk-level" style={{ color }}>
        {risk.level} ({percentage}%)
      </p>
      <p>{risk.total_detections} PII item(s) detected</p>
    </div>
  );
}
