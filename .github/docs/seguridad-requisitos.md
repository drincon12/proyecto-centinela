# Requisitos de Seguridad - Proyecto Centinela

## 1. Autenticación y Autorización
- El backend debe utilizar autenticación basada en JWT.
- Acciones sensibles (publicación en redes, análisis, escritura en DB)
  deben requerir permisos específicos.
- Todo el tráfico debe viajar por HTTPS en producción.

## 2. Protección de Datos
- Ninguna contraseña, token o clave API debe estar en el código fuente.
- Todas las credenciales deben almacenarse en variables de entorno (.env).
- La base de datos debe utilizar un usuario con privilegios mínimos.
- No registrar información sensible en los logs.

## 3. Seguridad de Código (Shift-Left)
- Todo commit debe ejecutar análisis SAST:
  - Semgrep
  - Bandit (para servicios Python)
- Debe ejecutarse análisis de secretos con Gitleaks antes del commit.
- Debe ejecutarse SCA (análisis de dependencias) con Trivy o Dependency-Check.

## 4. Seguridad de Contenedores
- Todas las imágenes Docker deben escanearse con Trivy en el pipeline.
- Las imágenes deben usar versiones slim de Python y Node para reducir superficie de ataque.
- No ejecutar contenedores como root (cuando sea posible).

## 5. Seguridad de Infraestructura (IaC)
- Todos los archivos de Terraform deben escanearse con Checkov.
- Los recursos deben seguir buenas prácticas:
  - Puertos mínimos expuestos.
  - Reglas de firewall estrictas.
  - Acceso SSH restringido por IP.
  - No utilizar claves hardcodeadas.

## 6. Seguridad en Tiempo de Ejecución (Runtime)
- Instalar Falco en el servidor para detectar:
  - Apertura de shells en contenedores.
  - Accesos sospechosos a archivos del sistema.
  - Modificaciones inesperadas dentro del contenedor.

## 7. Procesos Operativos
- Gestión de vulnerabilidades: todas las vulnerabilidades críticas encontradas por Trivy, ZAP o Checkov deben corregirse antes de producción.
- Controles de monitoreo:
  - Prometheus para métricas.
  - Grafana para dashboards.
- Logs centralizados: Stack ELK o Loki.

