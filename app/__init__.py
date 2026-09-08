"""
app/__init__.py
---------------
Patrón "Application Factory": en vez de crear la app en una variable global,
la creamos dentro de una función. Ventajas: se puede crear una app de prueba
distinta a la de producción, y se evitan imports circulares.
"""
from datetime import datetime
from urllib.parse import quote

from flask import Flask

from config import Config, DONACIONES, IGLESIA, MENSAJES_WHATSAPP, VERSICULO_JUAN_316
from .extensions import db, login_manager
from .utils import filtros_fecha


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # --- 1. Conectar las extensiones a ESTA app ---------------------------
    db.init_app(app)
    login_manager.init_app(app)

    # --- 2. Registrar los blueprints (grupos de rutas) --------------------
    from .routes.publico import bp as bp_publico
    from .routes.estudio import bp as bp_estudio
    from .routes.admin import bp as bp_admin

    app.register_blueprint(bp_publico)                      # /
    app.register_blueprint(bp_estudio, url_prefix="/estudio")   # /estudio/...
    app.register_blueprint(bp_admin, url_prefix="/estudio/admin")

    # --- 3. Filtros propios para Jinja (fechas en español) ----------------
    filtros_fecha(app)

    # --- 4. Variables disponibles en TODAS las plantillas -----------------
    @app.context_processor
    def variables_globales():
        def wa(numero_key, mensaje_key="general"):
            """Arma el link de WhatsApp con mensaje pre-escrito."""
            numero = IGLESIA.get(numero_key, "")
            texto = MENSAJES_WHATSAPP.get(mensaje_key, "")
            return f"https://wa.me/{numero}?text={quote(texto)}"

        return {
            "iglesia": IGLESIA,
            "juan316": VERSICULO_JUAN_316,
            "donaciones": DONACIONES,
            "wa": wa,
            "anio_actual": datetime.now().year,
            "ahora": datetime.now(),
        }

    # --- 5. Páginas de error ----------------------------------------------
    from flask import render_template

    @app.errorhandler(404)
    def no_encontrado(e):
        return render_template("error.html", codigo=404,
                               titulo="No encontramos esta página",
                               mensaje="Puede que el enlace haya cambiado."), 404

    @app.errorhandler(403)
    def sin_permiso(e):
        return render_template("error.html", codigo=403,
                               titulo="Acceso restringido",
                               mensaje="Esta sección es solo para la administración del estudio."), 403

    @app.errorhandler(500)
    def error_servidor(e):
        return render_template("error.html", codigo=500,
                               titulo="Algo salió mal",
                               mensaje="Estamos revisándolo. Intenta de nuevo en un momento."), 500

    # --- 6. Crear las tablas si aún no existen ----------------------------
    with app.app_context():
        db.create_all()

    return app
