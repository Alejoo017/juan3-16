"""
app/routes/admin.py
-------------------
Panel de administración (solo para usuarios con rol 'admin').
Desde aquí el pastor crea clases, pega el link de la clase, agrega tareas,
publica avisos, sube material y administra los accesos de los estudiantes.
"""
from datetime import datetime
from functools import wraps

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from ..extensions import db
from ..models import (Anuncio, Clase, Evento, MensajeContacto, Recurso, Tarea,
                      Usuario)

bp = Blueprint("admin", __name__)


# --- Decorador propio: exige sesión iniciada Y rol admin -------------------
def solo_admin(f):
    @wraps(f)
    @login_required
    def envoltura(*args, **kwargs):
        if not current_user.es_admin:
            abort(403)
        return f(*args, **kwargs)
    return envoltura


def _a_fecha_hora(texto, por_defecto=None):
    """Convierte '2026-09-18T19:00' (input datetime-local) a datetime."""
    try:
        return datetime.strptime(texto, "%Y-%m-%dT%H:%M")
    except (TypeError, ValueError):
        return por_defecto


def _a_fecha(texto):
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


# ===========================================================================
#  PANEL PRINCIPAL
# ===========================================================================
@bp.route("/")
@solo_admin
def panel():
    clases = Clase.query.order_by(Clase.fecha.desc()).all()
    estudiantes = Usuario.query.order_by(Usuario.nombre).all()
    anuncios = Anuncio.query.order_by(Anuncio.creado_en.desc()).all()
    recursos = Recurso.query.order_by(Recurso.creado_en.desc()).all()
    eventos = Evento.query.order_by(Evento.fecha.desc()).all()
    mensajes = MensajeContacto.query.order_by(MensajeContacto.creado_en.desc()).limit(30).all()
    sin_leer = MensajeContacto.query.filter_by(leido=False).count()

    return render_template(
        "estudio/admin.html",
        clases=clases, estudiantes=estudiantes, anuncios=anuncios,
        recursos=recursos, eventos=eventos, mensajes=mensajes, sin_leer=sin_leer,
        seccion=request.args.get("seccion", "clases"),
    )


# ===========================================================================
#  CLASES
# ===========================================================================
@bp.route("/clase/guardar", methods=["POST"])
@solo_admin
def guardar_clase():
    clase_id = request.form.get("clase_id")
    clase = db.session.get(Clase, int(clase_id)) if clase_id else Clase()

    fecha = _a_fecha_hora(request.form.get("fecha"), clase.fecha if clase_id else None)
    if fecha is None:
        flash("Revisa la fecha y la hora de la clase.", "error")
        return redirect(url_for("admin.panel", seccion="clases"))

    clase.titulo = (request.form.get("titulo") or "").strip() or "Clase sin título"
    clase.tema = (request.form.get("tema") or "").strip()
    clase.descripcion = (request.form.get("descripcion") or "").strip()
    clase.fecha = fecha
    clase.modalidad = request.form.get("modalidad") or "Presencial"
    clase.lugar = (request.form.get("lugar") or "").strip()
    clase.enlace = (request.form.get("enlace") or "").strip()
    clase.nivel = request.form.get("nivel") or "Nivel 1"
    clase.duracion_min = int(request.form.get("duracion_min") or 90)
    clase.publicada = bool(request.form.get("publicada"))

    if not clase_id:
        db.session.add(clase)
    db.session.commit()

    flash("Clase guardada." if clase_id else "Clase creada.", "exito")
    return redirect(url_for("admin.panel", seccion="clases"))


@bp.route("/clase/<int:clase_id>/enlace", methods=["POST"])
@solo_admin
def guardar_enlace(clase_id):
    """Atajo: pegar o cambiar solo el link de la clase."""
    clase = db.get_or_404(Clase, clase_id)
    clase.enlace = (request.form.get("enlace") or "").strip()
    db.session.commit()
    flash("Enlace de la clase actualizado.", "exito")
    return redirect(request.referrer or url_for("admin.panel", seccion="clases"))


@bp.route("/clase/<int:clase_id>/eliminar", methods=["POST"])
@solo_admin
def eliminar_clase(clase_id):
    clase = db.get_or_404(Clase, clase_id)
    db.session.delete(clase)          # sus tareas se borran en cascada
    db.session.commit()
    flash("Clase eliminada.", "exito")
    return redirect(url_for("admin.panel", seccion="clases"))


# ===========================================================================
#  TAREAS
# ===========================================================================
@bp.route("/clase/<int:clase_id>/tarea", methods=["POST"])
@solo_admin
def crear_tarea(clase_id):
    clase = db.get_or_404(Clase, clase_id)
    titulo = (request.form.get("titulo") or "").strip()
    if not titulo:
        flash("La tarea necesita un título.", "error")
        return redirect(url_for("admin.panel", seccion="clases"))

    db.session.add(Tarea(
        clase_id=clase.id,
        titulo=titulo,
        descripcion=(request.form.get("descripcion") or "").strip(),
        cita_biblica=(request.form.get("cita_biblica") or "").strip(),
        fecha_entrega=_a_fecha(request.form.get("fecha_entrega")),
    ))
    db.session.commit()
    flash("Tarea agregada a la clase.", "exito")
    return redirect(url_for("admin.panel", seccion="clases"))


@bp.route("/tarea/<int:tarea_id>/eliminar", methods=["POST"])
@solo_admin
def eliminar_tarea(tarea_id):
    tarea = db.get_or_404(Tarea, tarea_id)
    db.session.delete(tarea)
    db.session.commit()
    flash("Tarea eliminada.", "exito")
    return redirect(url_for("admin.panel", seccion="clases"))


# ===========================================================================
#  AVISOS Y MATERIAL
# ===========================================================================
@bp.route("/anuncio/guardar", methods=["POST"])
@solo_admin
def guardar_anuncio():
    titulo = (request.form.get("titulo") or "").strip()
    contenido = (request.form.get("contenido") or "").strip()
    if not titulo or not contenido:
        flash("El aviso necesita título y contenido.", "error")
        return redirect(url_for("admin.panel", seccion="avisos"))

    db.session.add(Anuncio(titulo=titulo, contenido=contenido,
                           fijado=bool(request.form.get("fijado"))))
    db.session.commit()
    flash("Aviso publicado en el aula.", "exito")
    return redirect(url_for("admin.panel", seccion="avisos"))


@bp.route("/anuncio/<int:anuncio_id>/eliminar", methods=["POST"])
@solo_admin
def eliminar_anuncio(anuncio_id):
    db.session.delete(db.get_or_404(Anuncio, anuncio_id))
    db.session.commit()
    flash("Aviso eliminado.", "exito")
    return redirect(url_for("admin.panel", seccion="avisos"))


@bp.route("/recurso/guardar", methods=["POST"])
@solo_admin
def guardar_recurso():
    titulo = (request.form.get("titulo") or "").strip()
    if not titulo:
        flash("El material necesita un título.", "error")
        return redirect(url_for("admin.panel", seccion="material"))

    db.session.add(Recurso(
        titulo=titulo,
        descripcion=(request.form.get("descripcion") or "").strip(),
        tipo=request.form.get("tipo") or "Documento",
        enlace=(request.form.get("enlace") or "").strip(),
    ))
    db.session.commit()
    flash("Material agregado.", "exito")
    return redirect(url_for("admin.panel", seccion="material"))


@bp.route("/recurso/<int:recurso_id>/eliminar", methods=["POST"])
@solo_admin
def eliminar_recurso(recurso_id):
    db.session.delete(db.get_or_404(Recurso, recurso_id))
    db.session.commit()
    flash("Material eliminado.", "exito")
    return redirect(url_for("admin.panel", seccion="material"))


# ===========================================================================
#  ESTUDIANTES (accesos)
# ===========================================================================
@bp.route("/estudiante/crear", methods=["POST"])
@solo_admin
def crear_estudiante():
    usuario_txt = (request.form.get("usuario") or "").strip().lower()
    nombre = (request.form.get("nombre") or "").strip()
    contrasena = request.form.get("contrasena") or ""

    if not usuario_txt or not nombre or len(contrasena) < 6:
        flash("Usuario, nombre y una contraseña de mínimo 6 caracteres son obligatorios.", "error")
        return redirect(url_for("admin.panel", seccion="estudiantes"))

    if Usuario.query.filter_by(usuario=usuario_txt).first():
        flash(f"El usuario «{usuario_txt}» ya existe.", "error")
        return redirect(url_for("admin.panel", seccion="estudiantes"))

    nuevo = Usuario(
        usuario=usuario_txt, nombre=nombre,
        correo=(request.form.get("correo") or "").strip(),
        telefono=(request.form.get("telefono") or "").strip(),
        nivel=request.form.get("nivel") or "Nivel 1",
        rol=request.form.get("rol") or "estudiante",
    )
    nuevo.poner_contrasena(contrasena)
    db.session.add(nuevo)
    db.session.commit()

    flash(f"Acceso creado para {nombre}. Entrega el usuario y la contraseña en privado.", "exito")
    return redirect(url_for("admin.panel", seccion="estudiantes"))


@bp.route("/estudiante/<int:usuario_id>/contrasena", methods=["POST"])
@solo_admin
def reiniciar_contrasena(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    nueva = request.form.get("nueva") or ""
    if len(nueva) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "error")
    else:
        usuario.poner_contrasena(nueva)
        db.session.commit()
        flash(f"Contraseña de {usuario.nombre} actualizada.", "exito")
    return redirect(url_for("admin.panel", seccion="estudiantes"))


@bp.route("/estudiante/<int:usuario_id>/editar", methods=["POST"])
@solo_admin
def editar_estudiante(usuario_id):
    """Corregir nombre, correo, teléfono, nivel o rol de una persona."""
    usuario = db.get_or_404(Usuario, usuario_id)

    nombre = (request.form.get("nombre") or "").strip()
    if not nombre:
        flash("El nombre no puede quedar vacío.", "error")
        return redirect(url_for("admin.panel", seccion="estudiantes"))

    nuevo_rol = request.form.get("rol") or usuario.rol
    # No dejar la iglesia sin ningún administrador
    if usuario.es_admin and nuevo_rol != "admin":
        if Usuario.query.filter_by(rol="admin").count() <= 1:
            flash("No puedes quitar el último administrador.", "error")
            return redirect(url_for("admin.panel", seccion="estudiantes"))

    usuario.nombre = nombre
    usuario.correo = (request.form.get("correo") or "").strip()
    usuario.telefono = (request.form.get("telefono") or "").strip()
    usuario.nivel = request.form.get("nivel") or usuario.nivel
    usuario.rol = nuevo_rol
    db.session.commit()

    flash(f"Datos de {usuario.nombre} actualizados.", "exito")
    return redirect(url_for("admin.panel", seccion="estudiantes"))


@bp.route("/estudiante/<int:usuario_id>/eliminar", methods=["POST"])
@solo_admin
def eliminar_estudiante(usuario_id):
    """
    Borra a una persona de forma definitiva.
    Antes de borrar hay dos candados: no puedes borrarte a ti mismo y no
    puedes borrar al último administrador que queda.
    """
    usuario = db.get_or_404(Usuario, usuario_id)

    if usuario.id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for("admin.panel", seccion="estudiantes"))

    if usuario.es_admin and Usuario.query.filter_by(rol="admin").count() <= 1:
        flash("No puedes eliminar al último administrador.", "error")
        return redirect(url_for("admin.panel", seccion="estudiantes"))

    # Confirmación escrita: hay que teclear el usuario exacto
    confirmacion = (request.form.get("confirmacion") or "").strip().lower()
    if confirmacion != usuario.usuario:
        flash(f"Para eliminar a {usuario.nombre} debes escribir «{usuario.usuario}» en la casilla de confirmación.", "error")
        return redirect(url_for("admin.panel", seccion="estudiantes"))

    nombre = usuario.nombre
    db.session.delete(usuario)
    db.session.commit()

    flash(f"{nombre} fue eliminado definitivamente.", "exito")
    return redirect(url_for("admin.panel", seccion="estudiantes"))


@bp.route("/estudiante/<int:usuario_id>/estado", methods=["POST"])
@solo_admin
def cambiar_estado(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)
    if usuario.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "error")
    else:
        usuario.activo = not usuario.activo
        db.session.commit()
        flash(f"Acceso de {usuario.nombre}: {'activo' if usuario.activo else 'desactivado'}.", "exito")
    return redirect(url_for("admin.panel", seccion="estudiantes"))


# ===========================================================================
#  EVENTOS PÚBLICOS Y MENSAJES
# ===========================================================================
@bp.route("/evento/guardar", methods=["POST"])
@solo_admin
def guardar_evento():
    fecha = _a_fecha_hora(request.form.get("fecha"))
    titulo = (request.form.get("titulo") or "").strip()
    if not titulo or fecha is None:
        flash("El evento necesita título, fecha y hora.", "error")
        return redirect(url_for("admin.panel", seccion="eventos"))

    db.session.add(Evento(
        titulo=titulo,
        descripcion=(request.form.get("descripcion") or "").strip(),
        fecha=fecha,
        lugar=(request.form.get("lugar") or "Templo principal").strip(),
        categoria=request.form.get("categoria") or "General",
        destacado=bool(request.form.get("destacado")),
    ))
    db.session.commit()
    flash("Evento publicado en la página principal.", "exito")
    return redirect(url_for("admin.panel", seccion="eventos"))


@bp.route("/evento/<int:evento_id>/eliminar", methods=["POST"])
@solo_admin
def eliminar_evento(evento_id):
    db.session.delete(db.get_or_404(Evento, evento_id))
    db.session.commit()
    flash("Evento eliminado.", "exito")
    return redirect(url_for("admin.panel", seccion="eventos"))


@bp.route("/mensaje/<int:mensaje_id>/leido", methods=["POST"])
@solo_admin
def marcar_leido(mensaje_id):
    mensaje = db.get_or_404(MensajeContacto, mensaje_id)
    mensaje.leido = not mensaje.leido
    db.session.commit()
    return redirect(url_for("admin.panel", seccion="mensajes"))
