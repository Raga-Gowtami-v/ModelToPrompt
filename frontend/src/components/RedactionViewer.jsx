import React from "react";

export default function RedactionViewer({ maskedText, detections }) {
  if (!maskedText) return null;

  return (
    <div className="redaction-viewer">
      <h3>Masked Output</h3>
      <pre className="masked-text">{maskedText}</pre>

      {detections && detections.length > 0 && (
        <div className="detections-list">
          <h3>Detections ({detections.length})</h3>
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Value</th>
                <th>Confidence</th>
                <th>Detector</th>
              </tr>
            </thead>
            <tbody>
              {detections.map((d, i) => (
                <tr key={i}>
                  <td className="pii-type">{d.type}</td>
                  <td className="pii-value">{d.value}</td>
                  <td>{(d.confidence * 100).toFixed(0)}%</td>
                  <td>{d.detector}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
