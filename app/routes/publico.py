"""
app/routes/publico.py
---------------------
Blueprint del sitio público: toda la información general de la iglesia.
Un Blueprint es un "grupo de rutas" que luego se enchufa a la app.
"""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Clase, Culto, Evento, MensajeContacto, Ministerio, Pastor

bp = Blueprint("publico", __name__)


@bp.route("/")
def inicio():
    ahora = datetime.now()

    cultos = Culto.query.order_by(Culto.orden).all()
    pastores = Pastor.query.order_by(Pastor.orden).all()
    ministerios = Ministerio.query.order_by(Ministerio.orden).all()

    eventos = (Evento.query
               .filter(Evento.publicado.is_(True), Evento.fecha >= ahora)
               .order_by(Evento.fecha)
               .limit(6).all())

    # Vista previa del estudio bíblico: máximo 3 próximas fechas
    proximas_clases = (Clase.query
                       .filter(Clase.publicada.is_(True), Clase.fecha >= ahora)
                       .order_by(Clase.fecha)
                       .limit(3).all())

    return render_template(
        "publico/inicio.html",
        cultos=cultos, pastores=pastores, ministerios=ministerios,
        eventos=eventos, proximas_clases=proximas_clases,
    )


@bp.route("/contacto", methods=["POST"])
def contacto():
    """Guarda el mensaje del formulario en la base de datos."""
    nombre = (request.form.get("nombre") or "").strip()
    mensaje = (request.form.get("mensaje") or "").strip()

    if not nombre or not mensaje:
        flash("Escribe tu nombre y tu mensaje para poder responderte.", "error")
        return redirect(url_for("publico.inicio") + "#contacto")

    db.session.add(MensajeContacto(
        nombre=nombre,
        correo=(request.form.get("correo") or "").strip(),
        telefono=(request.form.get("telefono") or "").strip(),
        asunto=(request.form.get("asunto") or "Consulta general").strip(),
        mensaje=mensaje,
    ))
    db.session.commit()

    flash("Recibimos tu mensaje. Te responderemos pronto.", "exito")
    return redirect(url_for("publico.inicio") + "#contacto")
