from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from urllib.parse import urlparse
import os
import psycopg2
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="Centinela Analysis Service")

class AnalyzePayload(BaseModel):
    url: HttpUrl

class AnalyzeResult(BaseModel):
    url: HttpUrl
    title: str
    summary: str
    score: float
    label: str

# Configuración DB
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "centinela_db")
DB_USER = os.getenv("DB_USER", "centinela")
DB_PASSWORD = os.getenv("DB_PASSWORD", "centinela")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

def ensure_table_exists():
    ddl = """
    CREATE TABLE IF NOT EXISTS url_analysis (
        id SERIAL PRIMARY KEY,
        url TEXT NOT NULL,
        title TEXT,
        summary TEXT,
        score REAL,
        label VARCHAR(16),
        analyzed_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    """
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
    conn.close()

ensure_table_exists()

def simple_score_from_url(url: str) -> float:
    parsed = urlparse(url)
    score = 0.0
    if parsed.scheme != "https":
        score += 0.4
    if parsed.hostname and parsed.hostname.count(".") > 2:
        score += 0.2
    for word in ["free", "promo", "win", "prize", "click"]:
        if word in url.lower():
            score += 0.2
            break
    return min(score, 1.0)

def label_from_score(score: float) -> str:
    if score < 0.34: return "LOW"
    if score < 0.67: return "MEDIUM"
    return "HIGH"

def extract_title_and_summary(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "Sin título"
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    text = " ".join(paragraphs)[:800]
    if not text:
        text = "No se encontró contenido relevante."
    return title, text

@app.post("/analyze", response_model=AnalyzeResult)
def analyze(payload: AnalyzePayload):
    url = str(payload.url)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo obtener la URL: {exc}")

    title, summary = extract_title_and_summary(resp.text)
    score = simple_score_from_url(url)
    label = label_from_score(score)

    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO url_analysis (url, title, summary, score, label, analyzed_at) VALUES (%s,%s,%s,%s,%s,%s)",
                (url, title, summary, score, label, datetime.utcnow())
            )
    conn.close()

    return AnalyzeResult(url=url, title=title, summary=summary, score=score, label=label)

@app.get("/health")
def health():
    return {"status": "ok"}
