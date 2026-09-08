"""
app/models.py
-------------
Cada clase = una tabla en SQLite. Cada atributo db.Column = una columna.
SQLAlchemy (el ORM) traduce esto a SQL por nosotros: en vez de escribir
"SELECT * FROM clase WHERE publicada = 1" escribimos Clase.query.filter_by(...).
"""
from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


# ===========================================================================
#  1. USUARIOS DEL AULA (estudio bíblico)
# ===========================================================================
class Usuario(UserMixin, db.Model):
    """
    UserMixin le regala a la clase los métodos que Flask-Login necesita
    (is_authenticated, get_id, etc.). Nosotros solo agregamos lo nuestro.
    """
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(60), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(120))
    telefono = db.Column(db.String(40))
    contrasena_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default="estudiante", nullable=False)  # admin | estudiante
    activo = db.Column(db.Boolean, default=True, nullable=False)
    nivel = db.Column(db.String(60), default="Nivel 1")
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_ingreso = db.Column(db.DateTime)

    # --- contraseñas: NUNCA se guardan en texto plano ----------------------
    def poner_contrasena(self, texto_plano: str) -> None:
        # pbkdf2:sha256 funciona en cualquier instalación de Python.
        # (scrypt, el método por defecto de Werkzeug, no está disponible en
        #  algunas versiones de Python de macOS.)
        self.contrasena_hash = generate_password_hash(
            texto_plano, method="pbkdf2:sha256:600000"
        )

    def revisar_contrasena(self, texto_plano: str) -> bool:
        return check_password_hash(self.contrasena_hash, texto_plano)

    @property
    def es_admin(self) -> bool:
        return self.rol == "admin"

    @property
    def primer_nombre(self) -> str:
        return self.nombre.split()[0] if self.nombre else self.usuario

    def __repr__(self):
        return f"<Usuario {self.usuario} ({self.rol})>"


@login_manager.user_loader
def cargar_usuario(user_id):
    """Flask-Login guarda solo el id en la cookie; esto lo vuelve un objeto."""
    return db.session.get(Usuario, int(user_id))


# ===========================================================================
#  2. CLASES DEL ESTUDIO BÍBLICO
# ===========================================================================
class Clase(db.Model):
    __tablename__ = "clase"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=False)
    tema = db.Column(db.String(160))
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, nullable=False, index=True)
    duracion_min = db.Column(db.Integer, default=90)
    modalidad = db.Column(db.String(30), default="Presencial")   # Presencial | Virtual | Mixta
    lugar = db.Column(db.String(160), default="Templo principal")
    enlace = db.Column(db.String(400))          # link de la clase virtual
    nivel = db.Column(db.String(60), default="Nivel 1")
    publicada = db.Column(db.Boolean, default=True, nullable=False)
    creada_en = db.Column(db.DateTime, default=datetime.utcnow)

    # Una clase tiene muchas tareas. cascade: si borro la clase, borro sus tareas.
    tareas = db.relationship(
        "Tarea", backref="clase", cascade="all, delete-orphan",
        order_by="Tarea.id", lazy="selectin",
    )

    @property
    def ya_paso(self) -> bool:
        return self.fecha < datetime.now()

    @property
    def dias_faltantes(self) -> int:
        return (self.fecha.date() - date.today()).days

    def __repr__(self):
        return f"<Clase {self.fecha:%d/%m/%Y} {self.titulo}>"


class Tarea(db.Model):
    __tablename__ = "tarea"

    id = db.Column(db.Integer, primary_key=True)
    clase_id = db.Column(db.Integer, db.ForeignKey("clase.id"), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    cita_biblica = db.Column(db.String(120))
    fecha_entrega = db.Column(db.Date)

    def __repr__(self):
        return f"<Tarea {self.titulo}>"


# ===========================================================================
#  3. CONTENIDO DEL AULA (avisos y material de apoyo)
# ===========================================================================
class Anuncio(db.Model):
    """Avisos internos que solo ven los estudiantes al iniciar sesión."""
    __tablename__ = "anuncio"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fijado = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)


class Recurso(db.Model):
    """Material de apoyo: guías, audios, videos, lecturas."""
    __tablename__ = "recurso"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=False)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(40), default="Documento")  # Documento | Video | Audio | Lectura
    enlace = db.Column(db.String(400))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)


# ===========================================================================
#  4. CONTENIDO PÚBLICO DE LA IGLESIA
# ===========================================================================
class Culto(db.Model):
    __tablename__ = "culto"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    dia = db.Column(db.String(40), nullable=False)
    hora = db.Column(db.String(40), nullable=False)
    descripcion = db.Column(db.String(300))
    dirigido_a = db.Column(db.String(120), default="Toda la congregación")
    orden = db.Column(db.Integer, default=0)


class Evento(db.Model):
    __tablename__ = "evento"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, nullable=False, index=True)
    lugar = db.Column(db.String(160), default="Templo principal")
    categoria = db.Column(db.String(60), default="General")
    destacado = db.Column(db.Boolean, default=False)
    publicado = db.Column(db.Boolean, default=True)


class Pastor(db.Model):
    __tablename__ = "pastor"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    cargo = db.Column(db.String(120), nullable=False)
    anios_servicio = db.Column(db.Integer, default=0)
    desde = db.Column(db.Integer)             # año en que empezó a servir
    resena = db.Column(db.Text)
    enfasis = db.Column(db.String(200))       # "Enseñanza bíblica, discipulado"
    foto = db.Column(db.String(120))          # nombre del archivo en static/img/pastores
    orden = db.Column(db.Integer, default=0)


class Ministerio(db.Model):
    __tablename__ = "ministerio"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(20), default="•")
    responsable = db.Column(db.String(120))
    orden = db.Column(db.Integer, default=0)


class MensajeContacto(db.Model):
    """Lo que la gente escribe en el formulario de contacto."""
    __tablename__ = "mensaje_contacto"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(120))
    telefono = db.Column(db.String(40))
    asunto = db.Column(db.String(160))
    mensaje = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
