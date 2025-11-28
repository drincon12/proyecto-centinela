import { useState } from "react";
import "./App.css";

// Usa variable de entorno si existe, si no, apunta directo a tu VM
const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://192.168.254.128:8000";

function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!url.trim()) {
      setError("Por favor ingresa una URL.");
      return;
    }

    try {
      setLoading(true);

      // 👉 ahora llamamos al endpoint /analyze del backend
      const resp = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!resp.ok) {
        const txt = await resp.text(); // <- nombre correcto
        throw new Error(`Error del backend: ${resp.status} - ${txt}`);
      }

      const data = await resp.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Error al conectar con la API.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#111",
        color: "#fff",
        padding: "3rem",
      }}
    >
      <h1 style={{ fontSize: "3rem", marginBottom: "1rem" }}>Centinela</h1>
      <p style={{ maxWidth: 600, marginBottom: "2rem", color: "#ccc" }}>
        Plataforma para análisis básico de desinformación / OSINT.
      </p>

      <form onSubmit={handleSubmit} style={{ maxWidth: 600, marginBottom: "1rem" }}>
        <label style={{ display: "block", marginBottom: "0.5rem" }}>
          URL a analizar:
        </label>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.ejemplo.com/noticia"
          style={{
            width: "100%",
            padding: "0.75rem 1rem",
            borderRadius: 4,
            border: "1px solid #444",
            background: "#222",
            color: "#fff",
            marginBottom: "1rem",
          }}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.75rem 1.5rem",
            borderRadius: 4,
            border: "none",
            background: loading ? "#555" : "#1d9bf0",
            color: "#fff",
            fontWeight: "bold",
            cursor: loading ? "default" : "pointer",
          }}
        >
          {loading ? "Analizando..." : "Enviar a scraping"}
        </button>
      </form>

      {error && (
        <p style={{ color: "#ff6b6b", marginTop: "1rem" }}>
          <strong>Error:</strong> {error}
        </p>
      )}

      {result && (
        <div
          style={{
            marginTop: "2rem",
            padding: "1.5rem",
            background: "#1a1a1a",
            borderRadius: 8,
            maxWidth: 800,
          }}
        >
          <h2 style={{ marginBottom: "0.5rem" }}>Resultado</h2>

          <p>
            <strong>URL:</strong> {result.url}
          </p>
          <p>
            <strong>Título:</strong> {result.title}
          </p>
          <p>
            <strong>Resumen:</strong> {result.summary}
          </p>
          <p>
            <strong>Score:</strong> {(result.score * 100).toFixed(1)}%
          </p>
          <p>
            <strong>Clasificación:</strong> {result.label}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;
