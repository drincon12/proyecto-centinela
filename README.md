
🛡️ PROYECTO CENTINELA — GRUPO 4


Plataforma contenerizada DevSecOps para análisis de desinformación y OSINT

📌 Descripción General
Centinela es una plataforma de análisis de URLs sospechosas que detecta amenazas, malware y desinformación. Implementa un pipeline DevSecOps completo con herramientas FOSS, integrando seguridad desde la planificación hasta la operación.

🧱 Arquitectura del Proyecto
🔧 Componentes
frontend: React + Vite servido con Nginx

backend: FastAPI para orquestación y endpoints

scraping-service: extrae contenido HTML y lo envía a RabbitMQ

publishing-service: publica resultados en cola

analysis-api: expone resultados vía API

analysis-worker: ejecuta análisis de desinformación

postgres: base de datos relacional

rabbitmq: broker de mensajería

grafana: visualización de métricas/logs

prometheus: recolección de métricas

loki: agregación de logs

promtail: recolección de logs

falco: monitoreo de seguridad en tiempo real

📁 Estructura del Proyecto
Código
proyecto-centinela/
├── backend/
├── frontend/
├── scraping-service/
├── publishing-service/
├── analysis-api/
├── analysis-worker/
├── deploy/
│   ├── Monitoring/ (Grafana, Prometheus, Loki, Promtail)
│   └── Security/ (Falco)
├── docker-compose.yml
├── .github/workflows/ (CI/CD DevSecOps)
└── docs/ (diagramas Threat Dragon, evidencias)
🧠 Diseño de Arquitectura
Modelado de amenazas con OWASP Threat Dragon (STRIDE + DFD)

Diagrama de componentes completo en docs/

Evidencias en Issue #1 y workflows

🔐 Pipeline DevSecOps — Fases y Herramientas
🟣 Fase 1: Planificación
Actividad: Requisitos de seguridad, modelado de amenazas

Herramientas: GitHub Issues, OWASP Threat Dragon

Evidencia: Issue #1

🔵 Fase 2: Codificación
Actividad: Desarrollo, SAST, SCA, pre-commit

Herramientas:

Gitleaks (pre-commit)

Semgrep + Bandit (SAST)

Trivy (SCA)

Evidencia: Issue #8

🟢 Fase 3: Construcción
Actividad: Build de imágenes, escaneo de CVEs

Herramientas: Docker, Trivy, GitHub Actions

Evidencia: .github/workflows/devsecops.yml

🟡 Fase 4: Pruebas
Actividad: Unitarias, integración, DAST

Herramientas: Pytest, OWASP ZAP (baseline scan)

Evidencia: ZAP integrado en CI

🟠 Fase 5: Release & Deploy
Actividad: Versionado, despliegue con IaC

Herramientas: Docker Compose, Trivy (IaC scan)

Evidencia: docker-compose.yml, deploy/

🔴 Fase 6: Operación y Monitoreo
Actividad: Logs, métricas, seguridad en tiempo real

Herramientas: Prometheus, Grafana, Loki, Promtail, Falco

Evidencia: Issue #10

📊 Observabilidad
Logs centralizados con Loki + Promtail

Métricas con Prometheus

Dashboards en Grafana

Seguridad en tiempo real con Falco

⚙️ Requisitos Previos
Docker y Docker Compose

Node.js y npm (para desarrollo local del frontend)

Python 3.11+ con venv (para backend y servicios)

Acceso a puertos: 3000, 8000, 9000, 3100, 9090, 17673, 5432

🚀 Despliegue Local
bash
git clone https://github.com/drincon12/proyecto-centinela.git
cd proyecto-centinela
docker compose up -d --build
Accede a:

Frontend: http://localhost:3000

Backend: http://localhost:8000

Grafana: http://localhost:3001

RabbitMQ: http://localhost:17673
