from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
import re

app = FastAPI(title="Centinela Analysis Service")


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class AnalyzeResult(BaseModel):
    url: HttpUrl
    title: str
    summary: str
    score: float
    label: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResult)
def analyze(req: AnalyzeRequest):
    """
    Descarga la página, extrae un título y un resumen simple,
    y calcula un 'score' muy básico basado en palabras clave.
    """
    try:
        r = requests.get(str(req.url), timeout=10)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Error al obtener la URL: {exc}")

    html = r.text

    # ---- título muy simple desde <title> ----
    m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if m:
        title = m.group(1).strip()
    else:
        title = "Sin título"

    # ---- limpiar HTML para texto plano ----
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    # resumen (primeros 300 caracteres)
    summary = text[:300]

    # ---- scoring MUY simple por keywords ----
    lower = text.lower()
    negative = ["fake", "falso", "fraude", "mentira", "hoax", "bulo"]
    positive = ["oficial", "confirmado", "verificado", "autorizado"]

    score_raw = 0
    for w in positive:
        score_raw += lower.count(w)
    for w in negative:
        score_raw -= lower.count(w)

    # normalizamos a rango [0, 1]
    score = (score_raw + 5) / 10.0
    score = max(0.0, min(1.0, score))

    if score >= 0.6:
        label = "confiable"
    elif score >= 0.3:
        label = "sospechoso"
    else:
        label = "no confiable"

    return AnalyzeResult(
        url=req.url,
        title=title,
        summary=summary or "Sin contenido extraído.",
        score=score,
        label=label,
    )
