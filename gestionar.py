"""
gestionar.py
------------
Herramienta de terminal para administrar la base de datos sin abrir el sitio.
Útil cuando pierdes la contraseña de administrador y no puedes entrar al panel.

USO:
    python gestionar.py                       muestra esta ayuda
    python gestionar.py listar                lista todas las personas con acceso
    python gestionar.py crear                 crea un acceso nuevo (te va preguntando)
    python gestionar.py clave USUARIO         cambia la contraseña de alguien
    python gestionar.py borrar USUARIO        elimina a alguien definitivamente
    python gestionar.py desactivar USUARIO    le quita el acceso sin borrar sus datos
    python gestionar.py activar USUARIO       le devuelve el acceso
    python gestionar.py resumen               cuántos registros hay en cada tabla
    python gestionar.py respaldo              guarda una copia de seguridad de la BD

Ejemplos:
    python gestionar.py crear
    python gestionar.py clave isai
    python gestionar.py borrar mariagomez
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import (Anuncio, Clase, Culto, Evento, MensajeContacto,
                        Ministerio, Pastor, Recurso, Tarea, Usuario)

app = create_app()

VERDE = "\033[92m"
ROJO = "\033[91m"
GRIS = "\033[90m"
FIN = "\033[0m"


def ok(texto):
    print(f"{VERDE}✓{FIN} {texto}")


def error(texto):
    print(f"{ROJO}✗{FIN} {texto}")


def buscar(nombre_usuario):
    """Busca a una persona por su nombre de usuario o avisa si no existe."""
    persona = Usuario.query.filter_by(usuario=nombre_usuario.strip().lower()).first()
    if persona is None:
        error(f"No existe ningún usuario llamado «{nombre_usuario}».")
        print(f"{GRIS}  Usa 'python gestionar.py listar' para ver los que hay.{FIN}")
    return persona


# ---------------------------------------------------------------------------
# COMANDOS
# ---------------------------------------------------------------------------
def cmd_listar():
    personas = Usuario.query.order_by(Usuario.rol, Usuario.nombre).all()
    if not personas:
        print("No hay ninguna persona registrada todavía.")
        return

    print(f"\n{len(personas)} persona(s) con acceso:\n")
    print(f"  {'USUARIO':<16} {'NOMBRE':<26} {'ROL':<14} {'ESTADO':<12} ÚLTIMO INGRESO")
    print(f"  {'-' * 16} {'-' * 26} {'-' * 14} {'-' * 12} {'-' * 16}")
    for p in personas:
        estado = "activo" if p.activo else "DESACTIVADO"
        rol = "administrador" if p.es_admin else p.nivel
        ingreso = p.ultimo_ingreso.strftime("%d/%m/%Y") if p.ultimo_ingreso else "nunca"
        print(f"  {p.usuario:<16} {p.nombre:<26} {rol:<14} {estado:<12} {ingreso}")
    print()


def cmd_crear():
    print("\nCrear un acceso nuevo. Deja vacío para cancelar.\n")

    nombre_usuario = input("  Usuario (sin espacios, ej. mariagomez): ").strip().lower()
    if not nombre_usuario:
        print("Cancelado."); return
    if Usuario.query.filter_by(usuario=nombre_usuario).first():
        error(f"Ya existe alguien con el usuario «{nombre_usuario}»."); return

    nombre = input("  Nombre completo: ").strip()
    if not nombre:
        print("Cancelado."); return

    contrasena = input("  Contraseña provisional (mínimo 6 caracteres): ").strip()
    if len(contrasena) < 6:
        error("La contraseña debe tener al menos 6 caracteres."); return

    correo = input("  Correo (opcional): ").strip()
    telefono = input("  Teléfono (opcional): ").strip()
    nivel = input("  Nivel [Nivel 1]: ").strip() or "Nivel 1"

    respuesta = input("  ¿Es administrador? (s/N): ").strip().lower()
    rol = "admin" if respuesta == "s" else "estudiante"

    persona = Usuario(usuario=nombre_usuario, nombre=nombre, correo=correo,
                      telefono=telefono, nivel=nivel, rol=rol)
    persona.poner_contrasena(contrasena)
    db.session.add(persona)
    db.session.commit()

    ok(f"Acceso creado para {nombre}.")
    print(f"\n  Entrégale estos datos en privado:")
    print(f"    Usuario:    {nombre_usuario}")
    print(f"    Contraseña: {contrasena}")
    print(f"\n{GRIS}  Pídele que la cambie desde 'Mi perfil' al entrar.{FIN}\n")


def cmd_clave(nombre_usuario):
    persona = buscar(nombre_usuario)
    if persona is None:
        return

    nueva = input(f"\n  Nueva contraseña para {persona.nombre}: ").strip()
    if len(nueva) < 6:
        error("La contraseña debe tener al menos 6 caracteres."); return

    persona.poner_contrasena(nueva)
    db.session.commit()
    ok(f"Contraseña de {persona.nombre} actualizada a: {nueva}\n")


def cmd_borrar(nombre_usuario):
    persona = buscar(nombre_usuario)
    if persona is None:
        return

    if persona.es_admin and Usuario.query.filter_by(rol="admin").count() <= 1:
        error("Es el último administrador. Crea otro antes de borrarlo."); return

    print(f"\n  Vas a eliminar a {ROJO}{persona.nombre}{FIN} ({persona.usuario}).")
    print(f"  {GRIS}Esto no se puede deshacer.{FIN}")
    confirmacion = input(f"  Escribe «{persona.usuario}» para confirmar: ").strip()

    if confirmacion != persona.usuario:
        print("Cancelado. No se borró nada."); return

    nombre = persona.nombre
    db.session.delete(persona)
    db.session.commit()
    ok(f"{nombre} fue eliminado definitivamente.\n")


def cmd_estado(nombre_usuario, activo):
    persona = buscar(nombre_usuario)
    if persona is None:
        return
    persona.activo = activo
    db.session.commit()
    ok(f"{persona.nombre}: acceso {'activo' if activo else 'desactivado'}.\n")


def cmd_resumen():
    tablas = [
        ("Personas con acceso", Usuario), ("Pastores", Pastor),
        ("Horarios de culto", Culto), ("Ministerios", Ministerio),
        ("Eventos", Evento), ("Clases del estudio", Clase),
        ("Tareas", Tarea), ("Avisos del aula", Anuncio),
        ("Material de apoyo", Recurso), ("Mensajes de contacto", MensajeContacto),
    ]
    ruta = Path(app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", ""))
    peso = ruta.stat().st_size / 1024 if ruta.exists() else 0

    print(f"\n  Base de datos: {ruta}")
    print(f"  Tamaño: {peso:.0f} KB\n")
    for etiqueta, modelo in tablas:
        print(f"    {etiqueta:<24} {modelo.query.count():>4}")

    sin_leer = MensajeContacto.query.filter_by(leido=False).count()
    if sin_leer:
        print(f"\n  {ROJO}Tienes {sin_leer} mensaje(s) de contacto sin leer.{FIN}")
    print()


def cmd_respaldo():
    origen = Path(app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", ""))
    if not origen.exists():
        error("Todavía no existe la base de datos."); return

    carpeta = origen.parent / "respaldos"
    carpeta.mkdir(exist_ok=True)
    destino = carpeta / f"iglesia-{datetime.now():%Y-%m-%d_%H%M}.db"
    shutil.copy2(origen, destino)

    ok(f"Copia guardada en:\n    {destino}\n")


# ---------------------------------------------------------------------------
# ENTRADA
# ---------------------------------------------------------------------------
COMANDOS_CON_USUARIO = {"clave", "borrar", "activar", "desactivar"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    comando = sys.argv[1].lower()
    argumento = sys.argv[2] if len(sys.argv) > 2 else None

    if comando in COMANDOS_CON_USUARIO and not argumento:
        error(f"Falta el usuario. Ejemplo: python gestionar.py {comando} isai")
        sys.exit(1)

    with app.app_context():
        if comando == "listar":
            cmd_listar()
        elif comando == "crear":
            cmd_crear()
        elif comando == "clave":
            cmd_clave(argumento)
        elif comando == "borrar":
            cmd_borrar(argumento)
        elif comando == "activar":
            cmd_estado(argumento, True)
        elif comando == "desactivar":
            cmd_estado(argumento, False)
        elif comando == "resumen":
            cmd_resumen()
        elif comando == "respaldo":
            cmd_respaldo()
        else:
            error(f"No conozco el comando «{comando}».")
            print(__doc__)
