import { useState } from "react";
import { createJob } from "../api/jobs";

export default function NewJobPage() {
  const [file, setFile] = useState(null);
  const [samplingFps, setSamplingFps] = useState(1.0);
  const [resizeWidth, setResizeWidth] = useState(512);
  const [grayscale, setGrayscale] = useState(false);
  const [blackWhite, setBlackWhite] = useState(false);
  const [imageFormat, setImageFormat] = useState("jpg");
  const [runExtract, setRunExtract] = useState(true);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    if (!file) return;

    setError("");
    setLoading(true);
    setResult(null);

    try {
      const fd = new FormData();
      fd.append("video", file);
      fd.append("sampling_fps", String(samplingFps));
      fd.append("resize_width", String(resizeWidth));
      fd.append("grayscale", String(grayscale));
      fd.append("black_white", String(blackWhite));
      fd.append("image_format", imageFormat);
      fd.append("run_extract", String(runExtract));

      const data = await createJob(fd);
      setResult(data);
    } catch (e2) {
      setError(String(e2.message || e2));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 16, fontFamily: "system-ui" }}>
      <h1 style={{ marginTop: 0 }}>New analysis</h1>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 10, border: "1px solid #eee", padding: 14, borderRadius: 14 }}>
        <label>
          Video file
          <input type="file" accept="video/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        </label>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
          <label>
            Sampling FPS
            <input type="number" step="0.1" value={samplingFps} onChange={(e) => setSamplingFps(Number(e.target.value))}
              style={{ width: "100%" }} />
          </label>

          <label>
            Resize width (required)
            <input type="number" value={resizeWidth} onChange={(e) => setResizeWidth(Number(e.target.value))}
              style={{ width: "100%" }} />
          </label>

          <label>
            Image format
            <select value={imageFormat} onChange={(e) => setImageFormat(e.target.value)} style={{ width: "100%" }}>
              <option value="jpg">jpg</option>
              <option value="png">png</option>
            </select>
          </label>
        </div>

        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          <label>
            <input
              type="checkbox"
              checked={blackWhite}
              onChange={(e) => {
                const v = e.target.checked;
                setBlackWhite(v);
                if (v) setGrayscale(false); // BW implies grayscale
              }}
            />{" "}
            Black & White
          </label>

          <label>
            <input
              type="checkbox"
              checked={grayscale}
              disabled={blackWhite}
              onChange={(e) => setGrayscale(e.target.checked)}
            />{" "}
            Grayscale
          </label>

          <label>
            <input type="checkbox" checked={runExtract} onChange={(e) => setRunExtract(e.target.checked)} />{" "}
            Run extraction immediately
          </label>
        </div>

        <button
          type="submit"
          disabled={!file || loading}
          style={{ padding: "10px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white" }}
        >
          {loading ? "Creating…" : "Create job"}
        </button>

        {error && <div style={{ color: "crimson" }}>{error}</div>}
        {result && (
          <div style={{ background: "#f7f7f7", border: "1px solid #eee", padding: 10, borderRadius: 10 }}>
            <div><b>Created job:</b> {result.job_id}</div>
            <div><b>Status:</b> {result.status}</div>
            <div style={{ fontSize: 12, color: "#555", marginTop: 6 }}>
              Go to <b>Jobs</b> page and select it.
            </div>
          </div>
        )}
      </form>
    </div>
  );
}