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
