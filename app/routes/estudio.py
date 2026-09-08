"""
app/routes/estudio.py
---------------------
Blueprint del Estudio Bíblico. Tiene dos partes:
  1. Página pública de presentación del estudio (/estudio)
  2. Aula privada, protegida con login (/estudio/aula)
"""
import calendar
from datetime import date, datetime

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models import Anuncio, Clase, Recurso, Usuario

bp = Blueprint("estudio", __name__)

NIVELES = [
    {"nombre": "Nivel 1 · Fundamentos",
     "resumen": "Qué es la Biblia, cómo llegó hasta nosotros y cómo leerla sin sacar los textos de contexto.",
     "temas": ["Panorama del Antiguo y Nuevo Testamento", "Cómo estudiar un pasaje",
               "La persona de Jesús en los Evangelios", "Arrepentimiento, fe y bautismo"]},
    {"nombre": "Nivel 2 · Doctrina",
     "resumen": "Las enseñanzas centrales de la fe cristiana, explicadas con el texto bíblico en la mano.",
     "temas": ["Dios: Padre, Hijo y Espíritu Santo", "La obra de la cruz y la resurrección",
               "La iglesia y sus ordenanzas", "Oración y vida devocional"]},
    {"nombre": "Nivel 3 · Servicio",
     "resumen": "Cómo servir dentro de la congregación y acompañar a otros en su caminar.",
     "temas": ["Dones y ministerios", "Familia y hogar según las Escrituras",
               "Acompañamiento y consejería básica", "Preparación de una enseñanza"]},
]


# ===========================================================================
#  PARTE PÚBLICA
# ===========================================================================
@bp.route("/")
def informacion():
    """Presentación del estudio: temas, niveles, próximas 3 fechas, inscripción."""
    proximas = (Clase.query
                .filter(Clase.publicada.is_(True), Clase.fecha >= datetime.now())
                .order_by(Clase.fecha)
                .limit(3).all())
    return render_template("estudio/informacion.html", proximas=proximas, niveles=NIVELES)


# ===========================================================================
#  LOGIN / LOGOUT
# ===========================================================================
@bp.route("/acceso", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("estudio.aula"))

    if request.method == "POST":
        usuario_txt = (request.form.get("usuario") or "").strip().lower()
        contrasena = request.form.get("contrasena") or ""
        recordar = bool(request.form.get("recordar"))

        usuario = Usuario.query.filter_by(usuario=usuario_txt).first()

        # Mensaje genérico a propósito: no revelamos si el usuario existe.
        if usuario is None or not usuario.revisar_contrasena(contrasena):
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template("estudio/login.html", usuario_previo=usuario_txt), 401

        if not usuario.activo:
            flash("Tu acceso está desactivado. Comunícate con la administración.", "error")
            return render_template("estudio/login.html", usuario_previo=usuario_txt), 403

        login_user(usuario, remember=recordar)
        usuario.ultimo_ingreso = datetime.utcnow()
        db.session.commit()

        # 'next' permite volver a la página que se intentaba abrir.
        destino = request.args.get("next")
        if not destino or not destino.startswith("/"):
            destino = url_for("estudio.aula")
        return redirect(destino)

    return render_template("estudio/login.html", usuario_previo="")


@bp.route("/salir")
@login_required
def logout():
    # OJO con el orden. logout_user() deja escrito en la sesión un aviso
    # ("_remember": "clear") para que Flask-Login borre la cookie de
    # "mantener la sesión iniciada" al terminar la petición.
    # Si llamáramos a session.clear() DESPUÉS, borraríamos ese aviso y la
    # cookie sobreviviría: la persona seguiría dentro tras cerrar sesión.
    session.clear()
    logout_user()
    flash("Cerraste sesión correctamente.", "exito")
    return redirect(url_for("estudio.informacion"))


# ===========================================================================
#  AULA PRIVADA
# ===========================================================================
def _matriz_mes(anio, mes, clases):
    """
    Devuelve la cuadrícula del mes para pintar el calendario.
    Cada celda: {'dia': 5, 'del_mes': True, 'hoy': False, 'clases': [...]}
    """
    por_dia = {}
    for c in clases:
        if c.fecha.year == anio and c.fecha.month == mes:
            por_dia.setdefault(c.fecha.day, []).append(c)

    cal = calendar.Calendar(firstweekday=0)   # 0 = lunes
    semanas = []
    for semana in cal.monthdatescalendar(anio, mes):
        fila = []
        for dia in semana:
            del_mes = (dia.month == mes)
            fila.append({
                "dia": dia.day,
                "del_mes": del_mes,
                "hoy": dia == date.today(),
                "clases": por_dia.get(dia.day, []) if del_mes else [],
            })
        semanas.append(fila)
    return semanas


@bp.route("/aula")
@login_required
def aula():
    ahora = datetime.now()

    # Las 2 próximas clases (lo que pidió el pastor que se vea primero)
    proximas = (Clase.query
                .filter(Clase.publicada.is_(True), Clase.fecha >= ahora)
                .order_by(Clase.fecha)
                .limit(2).all())

    # Mes que se está viendo en el calendario (?anio=&mes=)
    try:
        anio = int(request.args.get("anio", ahora.year))
        mes = int(request.args.get("mes", ahora.month))
        if not 1 <= mes <= 12:
            raise ValueError
    except (TypeError, ValueError):
        anio, mes = ahora.year, ahora.month

    todas = Clase.query.filter(Clase.publicada.is_(True)).all()
    semanas = _matriz_mes(anio, mes, todas)

    mes_ant = (anio - 1, 12) if mes == 1 else (anio, mes - 1)
    mes_sig = (anio + 1, 1) if mes == 12 else (anio, mes + 1)

    anuncios = Anuncio.query.order_by(Anuncio.fijado.desc(), Anuncio.creado_en.desc()).limit(4).all()
    recursos = Recurso.query.order_by(Recurso.creado_en.desc()).limit(6).all()

    return render_template(
        "estudio/aula.html",
        proximas=proximas, semanas=semanas, anio=anio, mes=mes,
        mes_ant=mes_ant, mes_sig=mes_sig,
        anuncios=anuncios, recursos=recursos,
    )


@bp.route("/aula/clases")
@login_required
def lista_clases():
    """Todo el cronograma: lo que viene y lo que ya se dictó."""
    ahora = datetime.now()
    futuras = (Clase.query.filter(Clase.publicada.is_(True), Clase.fecha >= ahora)
               .order_by(Clase.fecha).all())
    pasadas = (Clase.query.filter(Clase.publicada.is_(True), Clase.fecha < ahora)
               .order_by(Clase.fecha.desc()).all())
    return render_template("estudio/clases.html", futuras=futuras, pasadas=pasadas)


@bp.route("/aula/clase/<int:clase_id>")
@login_required
def detalle_clase(clase_id):
    clase = db.get_or_404(Clase, clase_id)
    return render_template("estudio/detalle_clase.html", clase=clase)


@bp.route("/aula/recursos")
@login_required
def lista_recursos():
    recursos = Recurso.query.order_by(Recurso.creado_en.desc()).all()
    return render_template("estudio/recursos.html", recursos=recursos, niveles=NIVELES)


@bp.route("/aula/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        actual = request.form.get("actual") or ""
        nueva = request.form.get("nueva") or ""
        repetir = request.form.get("repetir") or ""

        if not current_user.revisar_contrasena(actual):
            flash("La contraseña actual no coincide.", "error")
        elif len(nueva) < 6:
            flash("La nueva contraseña debe tener al menos 6 caracteres.", "error")
        elif nueva != repetir:
            flash("Las dos contraseñas nuevas no son iguales.", "error")
        else:
            current_user.poner_contrasena(nueva)
            db.session.commit()
            flash("Tu contraseña fue actualizada.", "exito")
            return redirect(url_for("estudio.perfil"))

    return render_template("estudio/perfil.html")
