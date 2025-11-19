README — Proyecto Centinela - Grupo 4 

Plataforma contenerizada de análisis de desinformación con pipeline DevSecOps completo

1. Descripción General

Proyecto Centinela es una plataforma de análisis de desinformación que implementa un pipeline DevSecOps de ciclo completo, integrando seguridad en todas las fases del desarrollo mediante herramientas 100% open source (FOSS).

El objetivo principal del proyecto no es construir una aplicación compleja, sino demostrar el uso de DevSecOps extremo a extremo: seguridad en el código, seguridad en la construcción de imágenes, pruebas dinámicas, escaneo de infraestructura y seguridad en tiempo real.

2. Arquitectura General del Proyecto

El sistema está compuesto por microservicios independientes, contenerizados con Docker:

 - Frontend: SPA en React/Vue (input de URL y visualización de resultados)

 - Backend API Gateway: FastAPI / Node.js

 - Servicio de Scraping: Python + BeautifulSoup

 - Servicio de Análisis: Python + NLP (NLTK/VADER)

 - Base de Datos: PostgreSQL o MongoDB

 - Mensajería: RabbitMQ o Redis

 - Orquestación: Docker Compose / K3s

 - Pipeline CI/CD/CS: GitHub Actions (antes GitLab CI)

📌 Todos los servicios cuentan con su propio Dockerfile y se despliegan mediante docker-compose.yml o manifests de Kubernetes (opcional).

3. DevSecOps: Fases y Herramientas Utilizadas

A continuación se documenta paso a paso qué se implementó en cada fase.

🗂️ 4. FASE 1 — PLAN
✔ Actividades realizadas

  - Definición de requisitos funcionales y no funcionales.

  - Identificación de posibles amenazas al sistema.

  - Construcción de un Modelo de Amenazas usando OWASP Threat Dragon.

  - Elaboración del Diagrama de Flujo de Datos (DFD).

✔ Herramientas

  - OWASP Threat Dragon → DFD + amenazas STRIDE

  - GitHub Projects → gestión de requerimientos y tareas

🧑‍💻 5. FASE 2 — CODE
✔ Actividades realizadas

1. Creación del repositorio GitHub.

2. Implementación del código de cada microservicio.

3. Configuración de hooks de seguridad en pre-commit.

4. Análisis estático de seguridad del código (SAST).

5. Análisis de dependencias vulnerables (SCA).

✔ Herramientas implementadas
* Pre-commit Hooks

  . Gitleaks: detectar secretos, contraseñas, tokens API.

  . TruffleHog (opcional).

🧪 SAST

  * Semgrep (reglas de seguridad general).

  * Bandit (si el servicio usa Python).

📦 SCA

  * Trivy escanea requirements.txt, package.json, etc.

  * OWASP Dependency-Check (opcional).

✔ Resultado

Cada vez que un desarrollador realiza un commit:

  * Se detectan secretos expuestos.

  * Se validan vulnerabilidades en dependencias.

  * Se ejecutan escaneos del código fuente.
