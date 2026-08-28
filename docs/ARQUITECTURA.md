# Arquitectura de IdentityHub

## Componentes

```mermaid
flowchart TD
    subgraph Usuarios
        U[Empleado]
        Admin[Administrador de TI]
    end

    subgraph IdentityHub["IdentityHub (este proyecto)"]
        Proxy["Auth Reverse Proxy\n(para apps sin SSO nativo)"]
        Inventario["Servicio de Inventario\n(Flask + PostgreSQL)"]
        Discovery["Descubrimiento de Shadow IT\n(OAuth grants + puntaje de riesgo)"]
    end

    subgraph Identidad
        KC["Keycloak\n(Identity Provider - OIDC/SAML)"]
    end

    subgraph Aplicativos
        AppSSO["App con soporte OIDC/SAML nativo\n(ej. Google Workspace, Slack)"]
        AppLegacy["App legacy o de plan básico\nsin soporte de federación"]
        AppShadow["Apps conectadas por OAuth\nsin aprobación de TI (Shadow IT)"]
    end

    U -->|1. Login único| KC
    KC -->|2a. Federación directa| AppSSO
    U -->|2b. Accede via proxy| Proxy
    Proxy -->|3. Valida sesión con| KC
    Proxy -->|4. Inyecta credenciales/headers| AppLegacy
    U -.->|Conecta sin pasar por TI| AppShadow

    Admin -->|Gestiona catálogo, usuarios, licencias| Inventario
    Inventario -->|Consulta usuarios y sesiones activas| KC
    Inventario -->|Al offboarding: revoca acceso| KC
    Inventario -->|Al offboarding: revoca acceso| Proxy
    Discovery -->|5. Consulta OAuth grants otorgados| AppShadow
    Discovery -->|6. Importa hallazgos con puntaje de riesgo| Inventario
    Inventario -->|Al offboarding: revoca también Shadow IT| Discovery
```

## Por qué esta arquitectura (y no otra)

**Decisión 1 — No reinventar los protocolos de autenticación.**
Keycloak ya implementa OIDC y SAML de forma correcta y auditada por la comunidad de seguridad.
Escribir un proveedor de identidad propio sería un riesgo de seguridad innecesario y no aporta
valor académico real: el conocimiento técnico está en *orquestar* identidad, no en reimplementar
criptografía de sesión.

**Decisión 2 — El proxy de autenticación es la pieza que resuelve el problema real.**
La mayoría de plataformas de identidad (Okta, Azure AD) asumen que la aplicación protegida ya
habla SAML/OIDC. El problema que describe el equipo —aplicativos sin soporte nativo de SSO— no lo
resuelve un IdP por sí solo. Se necesita un componente intermedio (patrón *auth reverse proxy*)
que intercepte el tráfico, autentique contra Keycloak, y le pase la sesión a la aplicación protegida
sin que esta necesite ningún cambio en su código.

**Decisión 3 — El inventario es la capa de valor de negocio.**
Un IdP le dice "quién inició sesión". No le dice a un administrador "qué aplicativos existen en la
empresa, quién tiene acceso a cada uno, cuáles licencias se pagan sin usarse, y si a un exempleado
ya se le revocó todo". Esa capa de gestión —construida sobre la API de administración de Keycloak—
es la funcionalidad que un IdP comercial no resuelve de fábrica y donde está el aporte real del
proyecto.

**Decisión 4 — Descubrimiento de Shadow IT: el diferencial real frente a la competencia.**
Existen herramientas SSPM (SaaS Security Posture Management, ej. GAT, DoControl) que descubren
aplicativos conectados por OAuth sin aprobación de TI, pero son de precio empresarial y viven
separadas de la gestión de SSO/inventario. Existen IdP accesibles (Keycloak) pero no hacen
descubrimiento. Ninguna solución conocida, accesible para PYMES, une ambas cosas: descubrir
automáticamente lo que TI no sabe que existe, calificarlo por riesgo, y revocarlo en el mismo
flujo de offboarding que ya cubre los aplicativos conocidos. Esa unificación es el aporte
diferencial de IdentityHub.

El mecanismo real (documentado pero no integrado aún, ver sección siguiente) es consultar los
permisos OAuth otorgados vía Google Workspace Admin SDK o Microsoft Graph API — ambas plataformas
ya exponen esta información en su consola de administración (Security → API Controls), pero sin
una forma accesible de vincularla con la gestión de accesos y el offboarding.

## Modelo de datos (servicio de inventario)

| Tabla | Campos principales | Propósito |
|---|---|---|
| `aplicativos` | id, nombre, tipo_soporte_sso (nativo / proxy / ninguno), costo_licencia_mensual, **origen** (manual / oauth_discovery), **alcance_oauth**, **fecha_ultimo_uso**, **puntaje_riesgo** | Catálogo de software de la empresa, incluidos los descubiertos automáticamente |
| `usuarios` | id, nombre, correo, keycloak_id, estado (activo/offboarding/inactivo) | Espejo de los usuarios gestionados en Keycloak |
| `accesos` | usuario_id, aplicativo_id, fecha_otorgado, fecha_revocado | Quién tiene acceso a qué, con historial — no distingue origen manual/descubierto: el offboarding revoca ambos por igual |
| `eventos_offboarding` | usuario_id, fecha, aplicativos_revocados, responsable | Auditoría de qué se revocó y cuándo |

### Cálculo del puntaje de riesgo (Shadow IT)

Implementado en `calcular_puntaje_riesgo()` (`inventory-service/app.py`), basado en reglas
explicables (no un modelo de caja negra, para que sea defendible en la sustentación):

- **Alcance de permisos otorgado**: acceso amplio ("completo", "administrador") puntúa más alto
  que acceso de solo lectura.
- **Inactividad**: un token OAuth sin uso reciente puntúa más alto — es el patrón más citado en
  la investigación de shadow apps (cuentas de exempleados o apps abandonadas que nadie revocó).

Migrar esto a un modelo entrenado con datos reales de uso es una mejora natural para el tercer
corte, una vez el equipo tenga suficiente historial real de la empresa.

### Integración real pendiente (requiere credenciales que el equipo debe gestionar)

El endpoint `/api/discovery/importar` hoy acepta una lista ya extraída manualmente (por ejemplo,
copiada desde Admin Console → Security → API Controls → App Access Control de Google Workspace).
Para automatizarlo por completo:

1. Confirmar si la empresa de origen usa Google Workspace o Microsoft 365 (ver
   `docs/INVESTIGACION_PENDIENTE.md`).
2. Si es Google Workspace: usar el [Admin SDK Reports API / Token API](https://developers.google.com/admin-sdk/reports)
   con credenciales de administrador del dominio.
3. Si es Microsoft 365: usar [Microsoft Graph API — oauth2PermissionGrants](https://learn.microsoft.com/graph/api/resources/oauth2permissiongrant).
4. Reemplazar la llamada manual por un job periódico que consulte la API real y llame a
   `/api/discovery/importar` automáticamente.

## Flujo crítico: offboarding centralizado

1. El administrador marca a un usuario como "Offboarding" en el servicio de inventario.
2. El servicio consulta la tabla `accesos` para saber a qué aplicativos tiene acceso ese usuario.
3. Para aplicativos federados vía Keycloak: se desactiva la cuenta directamente en Keycloak
   (API de administración), lo que invalida su sesión en todas las apps con SSO nativo.
4. Para aplicativos detrás del auth proxy: se invalida su sesión en el proxy.
5. Se registra el evento completo en `eventos_offboarding` como evidencia de auditoría.

Este es el flujo que se debe demostrar funcionando en el segundo/tercer corte — es la
funcionalidad de mayor impacto de seguridad real del proyecto.

## Costos y despliegue

Todo el software de este proyecto (Keycloak, PostgreSQL, Flask) es libre y de código abierto:
cero costo de licencia. El único punto de fricción real es que Keycloak, al ser una aplicación
Java, necesita más memoria que una app simple de Flask.

### Verificar los límites de memoria en su propia máquina (paso obligatorio antes de desplegar)

`docker-compose.yml` ya trae `mem_limit: 512m` en Keycloak y en el servicio de inventario —
el mismo límite que da el plan gratuito de Render por servicio. Esto permite probar localmente
si Keycloak arranca bien dentro de ese límite, **antes** de desplegar y descubrir un problema
en producción:

```bash
docker compose up
# Esperar a que Keycloak termine de arrancar (puede tardar 30-60 segundos, es normal)
# Si el contenedor de keycloak se reinicia solo o muere, revisar:
docker stats
docker logs <nombre-del-contenedor-keycloak>
```

Si ven errores de memoria (`OutOfMemoryError` o el contenedor muriendo sin razón aparente),
bajen el valor de `-Xmx` en la variable `JAVA_OPTS_APPEND` de `docker-compose.yml` (por ejemplo,
de `300m` a `250m`) y prueben de nuevo.

> Nota de transparencia: estos valores se configuraron siguiendo el comportamiento documentado
> de Keycloak (el heap de la JVM se calcula como un porcentaje de la memoria del contenedor
> desde la versión 24), pero no se pudieron probar en un entorno Docker real durante la
> preparación de este esqueleto. Verificarlo localmente es responsabilidad del equipo antes
> de la sustentación.

### Desplegar Keycloak en Render

Render permite desplegar una imagen Docker existente (como `quay.io/keycloak/keycloak`) como
Web Service desde su dashboard, sin necesidad de un Blueprint (`render.yaml`) para esa parte
específica — es el camino más confiable dado que no se pudo verificar la sintaxis exacta del
Blueprint para imágenes externas:

1. Render → New → Web Service → "Deploy an existing image from a registry".
2. Imagen: `quay.io/keycloak/keycloak:25.0`.
3. Variables de entorno: las mismas que están en `docker-compose.yml` para el servicio
   `keycloak` (`KEYCLOAK_ADMIN`, `KEYCLOAK_ADMIN_PASSWORD`, `KC_DB`, `KC_DB_URL`, etc.,
   más `JAVA_OPTS_APPEND` con los mismos límites de memoria).
4. Start Command: `start-dev` (modo desarrollo; para un ambiente más parecido a producción,
   revisar la documentación oficial de Keycloak sobre el modo `start`).
5. Plan: Free.

El servicio de inventario (`identityhub-inventory` en `render.yaml`) sí se puede desplegar
directamente como Blueprint, igual que en el proyecto anterior.

### Si 512 MB no alcanza

Si tras probar localmente Keycloak sigue sin caber cómodamente en 512 MB, la alternativa es
correr Keycloak localmente durante la sustentación (con capturas/video como evidencia adicional
en Drive) y desplegar solo el servicio de inventario en Render — sigue siendo una entrega válida.

