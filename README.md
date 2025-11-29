🛡️ Proyecto Centinela

Arquitectura basada en DevSecOps y Microservicios – Proyecto Final

El Proyecto Centinela es una plataforma diseñada para analizar, clasificar y publicar contenido proveniente de URLs utilizando una arquitectura moderna de microservicios y un enfoque completo DevSecOps. Este documento presenta la versión final profesional del README, integrando la arquitectura completa, el flujo DevSecOps por fases, evidencias del modelado de amenazas, requisitos de seguridad y detalles de implementación del repositorio.

📌 Índice

Descripción General

Arquitectura del Sistema

Diagrama de Componentes

Estructura del Proyecto

Ciclo DevSecOps Implementado

Fase 1: Plan

Fase 2: Code

Fase 3: Build

Fase 4: Test

Fase 5: Release--deploy

Fase 6: Operate--monitor

Modelado de Amenazas y Evidencias

Requisitos de Seguridad

Workflows y Automatización

Tecnologías Utilizadas

Cómo Ejecutar el Proyecto

Contribución

Licencia

🧩 Descripción General

Centinela es una aplicación distribuida basada en microservicios que permite:

Analizar URLs enviadas por el usuario.

Realizar scraping y validar fuentes confiables.

Generar análisis de sentimiento sobre el contenido.

Publicar resultados en redes sociales mediante un servicio automatizado.

Registrar hallazgos y métricas en una base de datos central.

Todo el ciclo de desarrollo está integrado con prácticas DevSecOps, donde la seguridad está embebida desde la planificación hasta la operación.

🏗️ Arquitectura del Sistema

🔹 Diagrama de Componentes

El proyecto cuenta con un diagrama de arquitectura diseñado con OWASP Threat Dragon, ubicado en /docs/diagrams/threat-model.json, donde se representan:

<img width="833" height="558" alt="image" src="https://github.com/user-attachments/assets/403e2b1f-a872-47e0-9fd3-a751fd3b3855" />


🔹 Estructura del Proyecto

<img width="911" height="391" alt="image" src="https://github.com/user-attachments/assets/3e053071-9ee7-4b92-a879-407eb8e30d52" />


Cada microservicio cuenta con su propio Dockerfile, dependencias y procesos CI/CD definidos.

🔄 Ciclo DevSecOps Implementado

Las seis fases del pipeline DevSecOps fueron aplicadas completamente a este proyecto.

✅ Fase 1: PLAN (Planificación)

Actividad: definición de requisitos de seguridad y modelado de amenazas.
Herramientas FOSS:

Gestión: GitLab Issues / Taiga.

Modelado de amenazas: OWASP Threat Dragon (DFD + STRIDE).

Incluye:

Identificación de amenazas: Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevación de privilegios.

Definición inicial de requisitos de seguridad basada en OWASP ASVS.

✅ Fase 2: CODE (Codificación)

Actividad: desarrollo del código + SAST + SCA pre-commit.

Herramientas FOSS:

Gitleaks / TruffleHog → detección de secretos.

Semgrep → reglas de seguridad.

Bandit → análisis Python.

Dependency-Check / Trivy → SCA.

GitLab/GitHub repository.

Se añadieron hooks pre-commit para prevenir push de código inseguro.

✅ Fase 3: BUILD (Construcción)

Actividad: CI construye imágenes Docker y ejecuta escaneo.

Herramientas FOSS:

GitLab CI/CD o Jenkins.

Docker + Dockerfile.

Trivy o Grype (escaneo de imagen por CVEs).

✅ Fase 4: TEST (Pruebas)

Actividad: pruebas unitarias + integración + DAST.

Herramientas:

Pytest / Jest.

OWASP ZAP → modo baseline scan.

✅ Fase 5: RELEASE & DEPLOY

Actividad: versionado y despliegue automatizado.

Herramientas:

Infraestructura como Código: Terraform / Ansible.

Escaneo IaC: Checkov o tfsec.

Orquestación: K3s / Docker Compose.

Registro: GitLab Container Registry.

✅ Fase 6: OPERATE & MONITOR

Actividad: observabilidad y seguridad en tiempo de ejecución.

Herramientas:

Logs: Loki + Promtail + Grafana.

Métricas: Prometheus.

Runtime Security: Falco.

(Opcional SIEM) Wazuh para correlación.

🧨 Modelado de Amenazas y Evidencias

En /docs se almacenan:

Diagramas DFD creados con OWASP Threat Dragon.

Archivo exportado JSON del modelo.

Capturas de pantallas de validación STRIDE.

Amenazas identificadas:

Riesgo de scraping no validado → mitigado con listas blancas.

Inyección en parámetros del análisis NLP.

Acceso no autorizado al API Gateway.

Exposición excesiva del broker de mensajes.

🔐 Requisitos de Seguridad

Basados en OWASP ASVS Nivel 1 + mejores prácticas DevSecOps:

Autenticación vía tokens API.

Validación estricta de URLs antes de scraping.

Cifrado en tránsito (HTTPS).

Sanitización de contenido antes de NLP.

Roles mínimos en cada microservicio.

Imágenes Docker minimalistas (slim/alpine).

Logs firmados y centralizados.

⚙️ Workflows y Automatización

Incluye workflows YAML dentro de /workflows para:

SAST con Semgrep.

SCA con Trivy.

Construcción de imágenes.

Ejecución de ZAP.

Despliegue automatizado.

🛠️ Tecnologías Utilizadas

Frontend: Vue.js / React
Backend Gateway: Python FastAPI / Node.js
Microservicios: Python (Scrapy, BeautifulSoup, NLTK)
Base de Datos: PostgreSQL / MongoDB
Mensajería: RabbitMQ o Redis
CI/CD: GitHub Actions / GitLab CI
Contenedores: Docker + Compose
Security Tools: Semgrep, Bandit, Trivy, ZAP, Falco

▶️ Cómo Ejecutar el Proyecto

Despliegue Local

bash
git clone https://github.com/drincon12/proyecto-centinela.git
cd proyecto-centinela
docker compose up -d --build

- Accede a:

Frontend: http://localhost:3000

Backend: http://localhost:8000

Grafana: http://localhost:3001

RabbitMQ: http://localhost:17673

Los servicios se levantarán en sus puertos configurados.

🤝 Contribución

Crear rama feature/

Ejecutar pre-commit

Abrir Merge Request


👥 Autores

Paola Rincón — Backend, DevSecOps, Seguridad
Guillermo Medina 
Carolina Nieto 
Favian Garcia 
Brian Pinzon


📄 Licencia

Este proyecto está bajo la licencia MIT.
