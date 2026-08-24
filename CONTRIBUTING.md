# Guía de Trabajo en GitHub — Equipo Restaurante QR

Esta guía define cómo el equipo (David, Eduar, Jhoan) debe trabajar en este repositorio de
aquí en adelante, para que exista trazabilidad individual real y evidencia verificable en
cada corte, tal como lo exige el Plan de Calificación del proyecto de grado.

## 1. Configuración inicial (una sola vez, cada persona)

1. **Crear cuenta de GitHub** si no tienes una (con tu nombre real o uno identificable).
2. **Pedir a Eduar (dueño del repo) que te agregue como colaborador**: Settings → Collaborators
   → Add people → tu usuario de GitHub. Sin esto no podrás subir ramas propias.
3. **Clonar el repositorio** en tu computador:
   ```bash
   git clone https://github.com/EduarOC/proyecto-de-grado.git
   cd proyecto-de-grado
   ```
4. **Configurar tu identidad** (así los commits quedan a tu nombre, no genéricos):
   ```bash
   git config user.name "Tu Nombre Completo"
   git config user.email "tu-correo-asociado-a-github@ejemplo.com"
   ```
5. **Instalar dependencias y probar que corre:**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

## 2. El flujo de trabajo (GitHub Flow)

Este repositorio sigue [GitHub Flow](https://docs.github.com/es/get-started/using-github/github-flow).
Para **cada tarea** (una historia de usuario, un bug, una mejora):

1. Actualizar tu copia local de `main`:
   ```bash
   git checkout main
   git pull origin main
   ```
2. Crear una rama descriptiva (ver convención de nombres abajo):
   ```bash
   git checkout -b feature/nombre-corto-de-la-tarea
   ```
3. Trabajar y hacer **commits pequeños y frecuentes** (no un solo commit gigante al final).
4. Subir la rama:
   ```bash
   git push -u origin feature/nombre-corto-de-la-tarea
   ```
5. Abrir un **Pull Request** en GitHub hacia `main` (plantilla en la sección 5).
6. **Esperar revisión de al menos un compañero** antes de fusionar — no fusionar tu propio PR
   sin que alguien más lo haya leído.
7. Fusionar (Merge) solo después de la aprobación.
8. Borrar la rama una vez fusionada (GitHub lo ofrece automáticamente).

## 3. Convención de nombres de rama

| Prefijo | Uso | Ejemplo |
|---|---|---|
| `feature/` | Funcionalidad nueva | `feature/panel-calificaciones` |
| `fix/` | Corrección de un bug | `fix/carrito-cantidad-negativa` |
| `docs/` | Documentación | `docs/guia-trabajo-github` |
| `refactor/` | Reorganizar código sin cambiar comportamiento | `refactor/separar-rutas-api` |

## 4. Convención de mensajes de commit

Formato: `tipo(alcance opcional): descripción corta en presente`, seguido de un cuerpo que
explica **qué** cambia y **por qué** (no solo repetir el título).

Tipos: `feat` (funcionalidad nueva), `fix` (corrección), `docs`, `refactor`, `test`, `chore`.

**Ejemplos reales ya usados en este repositorio** (revísalos con `git log`):

```
fix(seguridad): hashear contraseñas de staff con werkzeug.security

Antes las contraseñas de admin/chef/mesero se guardaban y comparaban en texto
plano en SQLite. Ahora se usan generate_password_hash / check_password_hash.

Referencia: WSTG-ATHN-02, OWASP ASVS capítulo de Autenticación.
```

Evitar mensajes genéricos como `"cambios"`, `"arreglos"`, `"update"` — no dicen nada útil
para quien revise el historial después (incluido el jurado).

## 5. Plantilla de Pull Request

Al abrir un PR, incluir en la descripción:

- **Qué cambia** (1-2 frases).
- **Por qué** (qué problema resuelve, o a qué historia de usuario / issue responde).
- **Cómo se probó** (comandos ejecutados, casos verificados).
- Si resuelve un Issue, escribir `Closes #N` para que se cierre automáticamente al fusionar.

## 6. Revisión de código (Code Review) entre el equipo

- Antes de aprobar, leer el diff completo (pestaña "Files changed" del PR).
- Preguntarse: ¿entiendo qué hace este cambio? ¿está probado? ¿rompe algo más?
- Usar el botón **"Review changes"** en GitHub:
  - **Comment**: dudas o sugerencias sin bloquear.
  - **Approve**: listo para fusionar.
  - **Request changes**: hay algo que corregir antes de fusionar.
- Rotar quién revisa a quién — no debe ser siempre la misma persona aprobando todo.

## 7. Vincular tareas con Issues

Los pendientes técnicos viven en [Issues de GitHub](https://github.com/EduarOC/proyecto-de-grado/issues),
como complemento al tablero de ClickUp (ClickUp para gestión gerencial, Issues para lo técnico
enlazado al código). Al crear un Issue nuevo, usar la plantilla correspondiente (aparecen al
hacer clic en "New Issue"):

- **🐛 Reporte de Bug**: mismos campos de la plantilla oficial de la sección 12.3 de los
  Lineamientos (Ambiente, Descripción, Severidad, Responsable, Evidencia, Estado).
- **📋 Historia de Usuario**: mismos campos de la sección 12.2 (Como/Quiero/Para, Prioridad,
  Criterios de aceptación, Evidencia).

Issues abiertos actuales para practicar este flujo:

- #9 — Decisión sobre pasarela de pago real vs. simulada.
- #10 — Evaluar migración de SQLite a PostgreSQL.
- #11 — Trazabilidad individual (este mismo tema).

## 8. Checklist antes de cada exposición de los martes / cada corte

- [ ] ¿Hay commits de **esta semana** de los tres integrantes (no solo de uno)?
- [ ] ¿Los Pull Requests abiertos tienen al menos una revisión?
- [ ] ¿El README sigue reflejando cómo correr el proyecto hoy?
- [ ] ¿Los Issues cerrados corresponden a trabajo realmente hecho?
- [ ] ¿ClickUp tiene una tarjeta por cada Issue/PR relevante de la semana?

## 9. Errores comunes a evitar

- ❌ Trabajar directo en `main` sin crear una rama.
- ❌ Mensajes de commit genéricos que no explican nada.
- ❌ Que un solo integrante concentre todos los commits (mata la trazabilidad individual).
- ❌ Pull Requests enormes que mezclan varias cosas no relacionadas — dificulta la revisión.
- ❌ Fusionar sin que nadie más haya leído el cambio.
