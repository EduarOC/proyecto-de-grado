# Actualización para Issue #31

## 1. Cronograma con Fechas Reales (Para Sección 5.1)

Reemplazar la tabla genérica de la **sección 5.1** con esta (basada en el inicio de clases del 3 de agosto):

| Semana | Fechas Reales | Actividades Sugeridas (Fase del Proyecto) |
| :--- | :--- | :--- |
| **Semana 1** | 3 de agosto – 9 de agosto | Levantamiento de requerimientos y definición del proyecto. |
| **Semana 2** | 10 de agosto – 16 de agosto | Diagnóstico de la empresa y estado del arte. |
| **Semana 3** | 17 de agosto – 23 de agosto | Diseño de arquitectura y diagramas (MER, flujos). |
| **Semana 4** | 24 de agosto – 30 de agosto | Configuración inicial del entorno y Docker (`auth-proxy`, `inventory-service`). |
| **Semana 5** | 31 de agosto – 6 de septiembre | Implementación de Keycloak / Entra ID y pruebas de login. |
| **Semana 6** | 7 de septiembre – 13 de septiembre | Integración del panel visual e inventario. |
| **Semana 7** | 14 de septiembre – 20 de septiembre | Análisis de Calidad y Seguridad (SonarQube, OWASP ZAP). |
| **Semana 8** | 21 de septiembre – 27 de septiembre | Ajustes finales, documentación y entrega del primer corte. |

---

## 2. Nuevos Riesgos (Para Sección 5.2 - Matriz de Riesgos)

Agregar estos riesgos a los ya existentes en la **sección 5.2**:

**Riesgo 4: Limitaciones de hardware con Docker**
* **Probabilidad:** Media
* **Impacto:** Alto
* **Descripción:** Incompatibilidad o falta de recursos (RAM/CPU) para ejecutar múltiples contenedores de Docker en los equipos de desarrollo.
* **Mitigación:** Optimizar el `docker-compose.yml` para consumir menos recursos y asegurar requisitos mínimos de hardware.

**Riesgo 5: Conectividad con el tenant de Entra ID**
* **Probabilidad:** Alta
* **Impacto:** Alto
* **Descripción:** Dificultades técnicas o de red al intentar sincronizar el tenant real de la empresa por políticas restrictivas de TI.
* **Mitigación:** Realizar pruebas de concepto (PoC) tempranas y solicitar permisos de administrador con anticipación.

**Riesgo 6: Curva de aprendizaje en SonarQube y ZAP**
* **Probabilidad:** Media
* **Impacto:** Medio
* **Descripción:** Retrasos en las tareas de evaluación de calidad debido a falta de experiencia previa con estas herramientas.
* **Mitigación:** Reservar tiempo adicional en el sprint para investigación técnica y revisión de la documentación oficial.
