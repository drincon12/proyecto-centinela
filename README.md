README — Proyecto Centinela - Grupo 4 

Plataforma contenerizada de análisis de desinformación con pipeline DevSecOps completo

## 1. Objetivo general

Diseñar, implementar, desplegar y operar una aplicación de microservicios que:

- Reciba URLs sospechosas.
- Realice scraping y un análisis básico de riesgo.
- Almacene los resultados en una base de datos.
- Expuesta a través de un frontend SPA para analistas de seguridad.
- Se integre con un pipeline de CI/CD y herramientas FOSS de seguridad.

1. Descripción General

Proyecto Centinela es una plataforma de análisis de desinformación que implementa un pipeline DevSecOps de ciclo completo, integrando seguridad en todas las fases del desarrollo mediante herramientas 100% open source (FOSS).

El objetivo principal del proyecto no es construir una aplicación compleja, sino demostrar el uso de DevSecOps extremo a extremo: seguridad en el código, seguridad en la construcción de imágenes, pruebas dinámicas, escaneo de infraestructura y seguridad en tiempo real.

## 2. Arquitectura

La solución se compone de los siguientes servicios:

- **Frontend (React / Vite)**  
  SPA que ofrece:
  - Dashboard de seguridad (métricas y últimos análisis).
  - Analizador de URLs.
  - Vista de monitoreo (logs / métricas de la plataforma).

- **Backend API (FastAPI)**  
  Actúa como **API Gateway**:
  - `POST /scrape`: envía URLs a RabbitMQ para procesamiento asíncrono.
  - `POST /analyze`: llama a `analysis-service` y devuelve el resultado al frontend.
  - `GET /health`: endpoint de salud.
  - `GET /metrics`: exporta métricas Prometheus.

- **Scraping Service (Python)**  
  Worker que encola y procesa tareas provenientes de RabbitMQ (pendiente de extender para scraping avanzado).

- **Analysis Service (FastAPI)**  
  Microservicio que:
  - Recibe una URL.
  - Hace scraping HTTP básico.
  - Extrae título y resumen del contenido.
  - Calcula un `score` y un `label` (LOW / MEDIUM / HIGH).
  - Persiste el resultado en PostgreSQL.

- **Publishing Service (placeholder)**  
  Servicio preparado para futuras integraciones con APIs sociales (Mastodon, Reddit, X/Twitter).

- **Base de Datos (PostgreSQL)**  
  Almacena los análisis realizados en la tabla `url_analysis`.

- **Broker de Mensajes (RabbitMQ)**  
  Facilita la comunicación asíncrona entre el API Gateway y los workers de scraping.

- **Monitoreo (Prometheus + Grafana)**  
  - `backend-api` expone métricas en `/metrics`.
  - Prometheus scrapea las métricas.
  - Grafana muestra dashboards con:
    - tráfico del API.
    - latencias de `/analyze`.

### Diagrama (alta nivel)

*(aquí puedes insertar una imagen con el diagrama de contenedores)*

## 3. Tecnologías principales

- **Frontend**: React, Vite, CSS personalizado.
- **Backend / Servicios**: Python, FastAPI, Requests, BeautifulSoup.
- **Mensajería**: RabbitMQ.
- **Base de Datos**: PostgreSQL.
- **Contenedores**: Docker, Docker Compose.
- **CI/CD**: GitHub Actions (build, pruebas, SAST con Checkov / etc.).
- **Monitoreo**: Prometheus, Grafana.

## 4. Puesta en marcha local

### 4.1. Requisitos

- Docker + Docker Compose
- Git
- Node.js 18+ (para desarrollo del frontend)
- Python 3.11+ (para desarrollo local fuera de contenedores)

### 4.2. Clonar repositorio

```bash
git clone https://github.com/drincon12/proyecto-centinela.git
cd proyecto-centinela
