const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

export async function scanFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/scan/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Scan failed");
  }
  return res.json();
}

export async function trainModel(file, prompt) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("prompt", prompt);

  const res = await fetch(`${API_BASE}/prompt/train`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Training failed");
  }
  return res.json();
}

export async function listModels() {
  const res = await fetch(`${API_BASE}/model/list`);
  if (!res.ok) {
    throw new Error("Failed to fetch models");
  }
  return res.json();
}
