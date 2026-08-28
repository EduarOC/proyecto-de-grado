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
