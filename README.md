# Sistema de Gestión, Menú y Pagos QR para Restaurantes

Proyecto de Grado — Ingeniería de Sistemas
Fundación de Educación Superior Nueva América

**Equipo:** David Yused Pulido Pardo · Eduar de Jesús Ortiz Causil · Jhoan Steven Soto Daza

## Descripción

Prototipo funcional (MVP) de un sistema de pedidos y pagos por código QR para restaurantes.
Permite al comensal escanear un QR de su mesa, ver el menú digital, agregar platos al carrito
y enviar el pedido, con paneles diferenciados para Administrador, Chef y Mesero.

## Stack técnico (MVP actual)

- **Backend:** Python 3 + Flask
- **Base de datos:** SQLite (se crea automáticamente al ejecutar la app)
- **Frontend:** HTML + CSS + JavaScript (Jinja2 templates, sin framework SPA)
- **Generación de QR:** librería `qrcode`

> Nota: el documento de arquitectura del proyecto (carpeta `04_Arquitectura` en Drive) contempla
> un stack de producción con React/Next.js, PostgreSQL y AWS. El stack actual corresponde a la
> decisión de alcance tomada para el MVP académico; ver sección de Arquitectura del documento final.

## Instalación y ejecución local

```bash
pip install -r requirements.txt
python app.py
```

La consola mostrará que el servidor corre en `http://127.0.0.1:5000`.

## Despliegue en un ambiente real (DEV/UAT)

El segundo corte exige evidencia de un ambiente accesible fuera de `localhost`. Este proyecto
está listo para desplegarse gratis en **[Render](https://render.com)** (sin tarjeta de crédito,
750 horas gratis al mes), que fue la opción evaluada frente a Railway (ya no tiene plan gratis),
Fly.io (pide tarjeta desde el registro) y PythonAnywhere (su plan gratuito no soporta WebSockets,
que este proyecto necesita).

**Pasos:**

1. Crear una cuenta en [render.com](https://render.com) con tu cuenta de GitHub (no pide tarjeta).
2. New → Blueprint → seleccionar este repositorio. Render detecta automáticamente `render.yaml`
   y configura el servicio (build, start command, y una `FLASK_SECRET_KEY` segura generada sola).
3. Apply → esperar el primer build (unos minutos).
4. Render entrega una URL pública tipo `https://restaurante-qr-app.onrender.com`.

**Limitaciones del plan gratuito a tener en cuenta:**

- El servicio se "duerme" tras 15 minutos sin tráfico; la primera petición después de eso tarda
  hasta ~1 minuto en responder (arranque en frío). Normal para un ambiente de pruebas académico.
- El archivo `restaurant.db` (SQLite) vive en disco efímero: se reinicia en cada nuevo despliegue.
  Para datos persistentes entre despliegues habría que migrar a una base de datos gestionada
  (ej. PostgreSQL, también disponible gratis en Render por 30 días) — ver sección de Arquitectura
  del documento final para la discusión de este trade-off.

## Variables de entorno

Antes de ejecutar en cualquier ambiente distinto a pruebas locales, define:

```bash
export FLASK_SECRET_KEY="una-clave-larga-y-aleatoria"
```

Si no se define, la aplicación usa una clave de desarrollo solo para pruebas locales
(ver `app.py`).

## Credenciales de prueba (staff)

| Usuario | Clave | Rol |
|---|---|---|
| admin | 1234 | Administrador |
| chef | 1234 | Cocina |
| mesero | 1234 | Servicio |

## Estructura del repositorio

```
app.py              Aplicación Flask (rutas públicas, autenticación, API)
templates/           Vistas Jinja2 (cliente, login, admin, chef, mesero)
static/              CSS y JS del cliente
requirements.txt     Dependencias Python
```

## Flujo de ramas (GitHub Flow)

Este repositorio sigue [GitHub Flow](https://docs.github.com/es/get-started/using-github/github-flow):
cada funcionalidad o corrección se desarrolla en una rama descriptiva y se integra a `main`
mediante Pull Request.

## Seguridad

Los hallazgos de seguridad identificados y su estado de remediación se documentan en
`08_Seguridad` del Drive del proyecto, con referencia a OWASP WSTG y ASVS.
