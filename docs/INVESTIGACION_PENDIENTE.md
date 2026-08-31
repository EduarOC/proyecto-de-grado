# Investigación pendiente (a elaborar por el equipo)

Este documento existe porque el reglamento del proyecto de grado prohíbe explícitamente que
una herramienta de IA invente fuentes, encuestas, resultados o conclusiones. Todo lo de este
archivo debe completarse con información real, recopilada por ustedes.

## 1. Diagnóstico de su propia empresa (fuente primaria — la más fuerte que tienen)

El origen de este proyecto es una necesidad real que uno de ustedes vive en su trabajo. Eso es
oro para la "Justificación" del documento — pero necesita quedar documentado formalmente:

- [ ] Inventario real: ¿cuántos aplicativos usa la empresa? ¿Cuáles tienen SSO y cuáles no?
- [x] **Plataforma confirmada: Microsoft Entra ID.** El conector real de descubrimiento de
      Shadow IT ya está construido en `discovery-connectors/entra_id.py` — ver instrucciones de
      configuración (registro de app, permisos, admin consent) al inicio de ese archivo.
- [ ] Ejecutar `discovery-connectors/entra_id.py` contra el tenant real una vez configurada la
      app registrada en Entra ID, y guardar los resultados como evidencia real para la
      sustentación (cuántas apps de Shadow IT aparecieron, cuáles quedaron con riesgo alto).
- [ ] Entrevista corta (puede ser al jefe de TI, o auto-relatada si el integrante es quien vive
      el problema) documentando: tiempo perdido administrando accesos manualmente, incidentes de
      cuentas no revocadas a tiempo, costo actual de licencias de aplicativos.
- [ ] Cotización real: pedir una cotización (o revisar el pricing público) de Entra ID
      Governance ($6-12 USD/usuario/mes según fuente, ver `docs/ARQUITECTURA.md`) para el número
      de usuarios de la empresa, para tener una cifra propia de cuánto costaría la alternativa
      comercial que ya incluye Lifecycle Workflows.

## 2. Validación de que el problema no es exclusivo de una empresa

- [ ] Encuestar (Google Forms) a 5-10 personas que trabajen en TI o administración de sistemas
      en otras empresas: ¿cuántos aplicativos administran? ¿tienen SSO en todos? ¿qué tan
      doloroso es el proceso de offboarding hoy?
- [ ] Tabular resultados y generar gráficas (igual que se documentó en la guía original de
      investigación) para sustentar que el problema es generalizable, no anecdótico.

## 3. Estado del arte (competencia) — punto de partida, deben profundizar

Durante la conversación de definición del proyecto se identificaron estas referencias de mercado
como punto de partida. El equipo debe ampliar esta investigación con fuentes propias:

- **Identity Providers comerciales:** Okta, Microsoft Entra ID (Azure AD), Auth0.
- **SaaS Management Platforms:** Zylo, Torii, BetterCloud (categoría de inventario de
  aplicativos/licencias, orientada a empresas grandes).
- **Identity brokers open source:** Keycloak, Authelia, Pomerium (patrón de proxy de
  autenticación para apps sin soporte nativo).

Tarea del equipo: buscar si existe algún competidor directo enfocado específicamente en PYMES
colombianas/latinoamericanas, y documentar en qué se diferenciaría IdentityHub.

## 4. Marco teórico

Teoría a desarrollar por el equipo, con fuentes propias, incluyendo como mínimo:

- Qué es SSO y por qué reduce riesgo de seguridad (fatiga de contraseñas, superficie de ataque).
- Qué es un Identity Provider y el rol de los protocolos OIDC/SAML.
- Qué es Shadow IT y por qué es un riesgo de gobierno de TI.
- Qué es el patrón "auth reverse proxy" / "identity broker".

## 5. Objetivo general y específicos

Redactar siguiendo el mismo formato que ya usaron en el proyecto anterior (ver
`Documento_Primer_Corte.docx` archivado en Drive como referencia de formato, no de contenido).
