import { useState } from "react";
import "./App.css";

// Usa variable de entorno si existe, si no, apunta directo a tu VM
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://192.168.254.128:8000";

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

      const resp = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!resp.ok) {
        const txt = await resp.text();
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
    <div className="centinela-root">
      {/* Aquí mantienes tu layout tipo mockup: navbar, etc.
          Yo solo dejo el área del Analizador de URL */}
      <main className="analizador-layout">
        <section className="analizador-card">
          <h1>Analizador de URLs</h1>
          <p className="analizador-subtitle">
            Detecta amenazas, malware y desinformación en sitios web.
          </p>

          <form onSubmit={handleSubmit} className="analizador-form">
            <label>Ingresa una URL para analizar</label>
            <span className="ejemplo">Ejemplo: https://ejemplo.com</span>

            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://ejemplo.com"
            />

            <button type="submit" disabled={loading}>
              {loading ? "Analizando..." : "Analizar"}
            </button>
          </form>

          {error && (
            <p className="error-text">
              <strong>Error:</strong> {error}
            </p>
          )}
        </section>

        {result && (
          <section className="resultado-card">
            <h2>Nivel de Amenaza</h2>
            <div className={`badge badge-${result.label.toLowerCase()}`}>
              {result.label}
            </div>

            <div className="resultado-meta">
              <span>URL analizada:</span>
              <code>{result.url}</code>
            </div>

            <div className="resultado-detalle">
              <h3>{result.title}</h3>
              <p>{result.summary}</p>
              <p className="resultado-score">
                Score: {result.score.toFixed(2)}
              </p>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
