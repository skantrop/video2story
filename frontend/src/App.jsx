import { Link, Route, Routes } from "react-router-dom";
import NewJobPage from "./pages/NewJobPage";
import JobsPage from "./pages/JobsPage";

export default function App() {
  return (
    <div style={{ height: "100vh" }}>
      <header style={{ padding: "10px 14px", borderBottom: "1px solid #eee", display: "flex", gap: 12 }}>
        <Link to="/" style={{ textDecoration: "none" }}>New analysis</Link>
        <Link to="/jobs" style={{ textDecoration: "none" }}>Jobs</Link>
      </header>

      <Routes>
        <Route path="/" element={<NewJobPage />} />
        <Route path="/jobs" element={<JobsPage />} />
      </Routes>
    </div>
  );
}