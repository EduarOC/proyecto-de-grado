"""
IdentityHub - Servicio de Inventario

Catálogo de aplicativos, usuarios y accesos. Este es el esqueleto inicial: modelo de datos
y endpoints básicos de lectura. La integración real con la API de administración de Keycloak
(para ejecutar la revocación de accesos en el offboarding) es el siguiente paso técnico del
proyecto, documentado en docs/ARQUITECTURA.md.
"""
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://identityhub:identityhub_dev_password@localhost:5432/identityhub")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Aplicativo(Base):
    __tablename__ = "aplicativos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    # 'nativo' = soporta OIDC/SAML directamente; 'proxy' = requiere el auth reverse proxy;
    # 'ninguno' = todavía sin integrar.
    tipo_soporte_sso = Column(String, nullable=False, default="ninguno")
    costo_licencia_mensual = Column(Float, default=0)

    accesos = relationship("Acceso", back_populates="aplicativo")


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, nullable=False, unique=True)
    keycloak_id = Column(String, nullable=True)
    # 'activo', 'offboarding', 'inactivo'
    estado = Column(String, nullable=False, default="activo")

    accesos = relationship("Acceso", back_populates="usuario")


class Acceso(Base):
    __tablename__ = "accesos"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    aplicativo_id = Column(Integer, ForeignKey("aplicativos.id"), nullable=False)
    fecha_otorgado = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_revocado = Column(DateTime, nullable=True)

    usuario = relationship("Usuario", back_populates="accesos")
    aplicativo = relationship("Aplicativo", back_populates="accesos")


class EventoOffboarding(Base):
    __tablename__ = "eventos_offboarding"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    aplicativos_revocados = Column(String)  # lista separada por comas, para el MVP
    responsable = Column(String, nullable=False)


@app.route("/api/aplicativos", methods=["GET"])
def listar_aplicativos():
    session = SessionLocal()
    try:
        apps = session.query(Aplicativo).all()
        return jsonify([
            {
                "id": a.id, "nombre": a.nombre,
                "tipo_soporte_sso": a.tipo_soporte_sso,
                "costo_licencia_mensual": a.costo_licencia_mensual,
            } for a in apps
        ])
    finally:
        session.close()


@app.route("/api/usuarios/<int:usuario_id>/accesos", methods=["GET"])
def accesos_de_usuario(usuario_id):
    session = SessionLocal()
    try:
        accesos = session.query(Acceso).filter_by(usuario_id=usuario_id, fecha_revocado=None).all()
        return jsonify([
            {"aplicativo_id": a.aplicativo_id, "fecha_otorgado": a.fecha_otorgado.isoformat()}
            for a in accesos
        ])
    finally:
        session.close()


@app.route("/api/usuarios/<int:usuario_id>/offboarding", methods=["POST"])
def iniciar_offboarding(usuario_id):
    """
    Punto de entrada del flujo crítico del proyecto (ver docs/ARQUITECTURA.md).
    TODO técnico pendiente: reemplazar la simulación de abajo por la llamada real a la API
    de administración de Keycloak (deshabilitar el usuario) y al auth proxy (invalidar sesión).
    """
    data = request.json or {}
    responsable = data.get("responsable", "desconocido")

    session = SessionLocal()
    try:
        usuario = session.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            return jsonify({"success": False, "error": "Usuario no encontrado"}), 404

        accesos_activos = session.query(Acceso).filter_by(usuario_id=usuario_id, fecha_revocado=None).all()
        nombres_apps = []
        for acceso in accesos_activos:
            acceso.fecha_revocado = datetime.now(timezone.utc)
            nombres_apps.append(acceso.aplicativo.nombre)

        usuario.estado = "offboarding"

        evento = EventoOffboarding(
            usuario_id=usuario_id,
            aplicativos_revocados=", ".join(nombres_apps),
            responsable=responsable,
        )
        session.add(evento)
        session.commit()

        return jsonify({
            "success": True,
            "aplicativos_revocados": nombres_apps,
            "nota": "Simulado a nivel de base de datos. Falta integrar la revocación real en Keycloak.",
        })
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
