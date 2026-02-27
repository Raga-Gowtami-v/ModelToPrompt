import React, { useEffect, useState } from "react";
import { listModels } from "../services/api";

export default function Dashboard() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const data = await listModels();
        setModels(data.models || []);
      } catch (err) {
        console.error("Failed to fetch models:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, []);

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <section className="models-section">
        <h2>Trained Models</h2>
        {loading ? (
          <p>Loading...</p>
        ) : models.length === 0 ? (
          <p>No models trained yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Model ID</th>
                <th>Filename</th>
                <th>Size</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => (
                <tr key={m.id}>
                  <td>{m.id}</td>
                  <td>{m.filename}</td>
                  <td>{(m.size_bytes / 1024).toFixed(1)} KB</td>
                  <td>
                    <a href={`/api/model/download/${m.id}`}>Download</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
