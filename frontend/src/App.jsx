import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import UploadPage from "./pages/UploadPage";
import PromptPage from "./pages/PromptPage";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <div className="app">
      <nav className="navbar">
        <Link to="/" className="nav-brand">Secure Data & ML</Link>
        <div className="nav-links">
          <Link to="/sanitize">Sanitize</Link>
          <Link to="/train">Train Model</Link>
          <Link to="/dashboard">Dashboard</Link>
        </div>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/sanitize" element={<UploadPage />} />
          <Route path="/train" element={<PromptPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  );
}
