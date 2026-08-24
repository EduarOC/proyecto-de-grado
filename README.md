# IdentityHub — Plataforma de Gestión Unificada de Identidad e Inventario de Aplicativos

Proyecto de Grado — Ingeniería de Sistemas
Fundación de Educación Superior Nueva América

**Equipo:** David Yused Pulido Pardo · Eduar de Jesús Ortiz Causil · Jhoan Steven Soto Daza

> ⚠️ Este repositorio contenía originalmente un sistema de pedidos por QR para restaurantes.
> Ese trabajo se conserva íntegro en la rama [`archivo/restaurante-qr-v1`](../../tree/archivo/restaurante-qr-v1)
> y en el tag `v0-restaurante-qr` — no se descartó, se archivó como evidencia de un ciclo de
> desarrollo completo antes del cambio de enfoque.

## El problema

Las empresas medianas administran decenas de aplicativos (correo, CRM, ERP, herramientas internas),
pero solo una minoría soporta Single Sign-On (SSO) de forma nativa. Implementar SSO comercial
(Okta, Azure AD Premium) cuesta desde 6 USD/usuario/mes solo por la plataforma de identidad —
sin contar que muchos proveedores de software cobran un cargo adicional ("SSO tax") por habilitar
SAML/OIDC en sus planes empresariales. El resultado: la mayoría de las PYMES vive con contraseñas
sueltas, sin inventario centralizado de quién tiene acceso a qué, y con un riesgo de seguridad
crítico y muy común — cuentas de exempleados que nadie revocó porque no había un solo lugar desde
donde hacerlo.

## La propuesta

IdentityHub no reinventa los protocolos de autenticación (eso sería un riesgo de seguridad
innecesario). Se construye **sobre Keycloak** (Identity Provider open source, estándar de la
industria) y aporta valor real en dos capas:

1. **Broker de identidad para aplicativos sin soporte nativo de SSO**: un proxy de autenticación
   (patrón `auth reverse proxy`, el mismo que usan herramientas como Pomerium o Datawiza) que se
   antepone a aplicaciones legacy o de plan básico, resolviendo la autenticación sin que la
   aplicación protegida necesite ningún cambio.
2. **Inventario y automatización de accesos**: catálogo de qué usuario tiene acceso a qué
   aplicativo, detección de licencias pagadas sin uso, y — la funcionalidad de mayor impacto en
   seguridad real — **revocación centralizada en el offboarding**: cuando alguien sale de la
   empresa, se le retira el acceso a todos los aplicativos desde un solo lugar.

## Estado del proyecto

Este repositorio contiene por ahora el **esqueleto técnico inicial** (arquitectura, Keycloak
levantado vía Docker, y el servicio de inventario en construcción). La investigación de mercado,
la justificación académica y las encuestas/entrevistas del primer corte **deben ser elaboradas por
el equipo** — ver `INVESTIGACION_PENDIENTE.md` para el checklist concreto de qué recopilar.

## Stack técnico

- **Identity Provider:** [Keycloak](https://www.keycloak.org/) (open source, protocolo OIDC/SAML)
- **Backend de inventario:** Python + Flask (mismo stack que el equipo ya domina)
- **Base de datos:** PostgreSQL
- **Orquestación local:** Docker Compose

## Estructura del repositorio

```
docker-compose.yml       Levanta Keycloak + PostgreSQL + el servicio de inventario en local
inventory-service/       Backend Flask: catálogo de apps, usuarios, licencias, offboarding
docs/
  ARQUITECTURA.md         Diagrama y explicación de los 2 componentes técnicos centrales
  INVESTIGACION_PENDIENTE.md   Checklist de investigación real que debe hacer el equipo
```

## Cómo levantar el entorno local

```bash
docker compose up -d
```

Esto levanta Keycloak en `http://localhost:8080` (admin/admin por defecto — cambiar antes de
cualquier uso real) y el servicio de inventario en `http://localhost:5000`.

## Flujo de trabajo

Este repositorio sigue [GitHub Flow](https://docs.github.com/es/get-started/using-github/github-flow),
documentado en `CONTRIBUTING.md`. Las plantillas de Issues y Pull Requests ya están configuradas
en `.github/` y aplican igual que en el proyecto anterior.
