"""
config.example.py
-----------------
PLANTILLA de configuración. Los valores de aquí son de ejemplo.

Para usar el proyecto:
    1. Copia este archivo:   cp config.example.py config.py
    2. Edita config.py con los datos reales de tu iglesia
    3. config.py está en .gitignore: nunca se sube al repositorio

Nunca escribas aquí números de teléfono, cuentas bancarias ni claves reales.
"""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Clave usada por Flask para firmar las cookies de sesión.
    # En producción se define como variable de entorno.
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-solo-para-desarrollo-local")

    # Ruta del archivo SQLite. Queda dentro de /instance (carpeta privada de Flask).
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "iglesia.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Duración de la cookie "mantener la sesión iniciada".
    # Flask-Login espera un timedelta, no un número de segundos.
    REMEMBER_COOKIE_DURATION = timedelta(days=14)


# ---------------------------------------------------------------------------
# DATOS DE LA IGLESIA  (edita solo esto para actualizar el sitio)
# ---------------------------------------------------------------------------
IGLESIA = {
    "nombre": "Comunidad Cristiana Juan 3:16",
    "nombre_corto": "Juan 3:16",
    "lema": "Una comunidad para toda la familia",
    "direccion": "Calle 00 #00-00, Barrio Ejemplo",
    "ciudad": "Bogotá, Colombia",
    "correo": "contacto@comunidadjuan316.org",
    "telefono": "+57 300 000 0000",

    # --- WhatsApp -----------------------------------------------------------
    # Formato internacional SIN espacios, SIN "+", SIN guiones. Ej: 573000000000
    "whatsapp_oracion": "573000000000",       # línea de oración
    "whatsapp_inscripcion": "573000000000",   # chat del pastor Daniel (inscripciones)
    "whatsapp_admin": "573000000000",         # soporte de acceso al estudio

    # --- Redes --------------------------------------------------------------
    "facebook": "https://facebook.com/",
    "instagram": "https://instagram.com/",
    "youtube": "https://youtube.com/",

    # --- Mapa (opcional): pega aquí el "src" del iframe de Google Maps -------
    "mapa_embed": "",
}

# Mensajes que se abren pre-escritos en WhatsApp
MENSAJES_WHATSAPP = {
    "oracion": "Hola, buen día. Escribo desde la página web para pedir oración.",
    "inscripcion": "Hola, buen día. Escribo desde la página web porque quiero inscribirme al estudio bíblico.",
    "acceso": "Hola, buen día. Soy estudiante del estudio bíblico y tengo problemas para ingresar a mi cuenta.",
    "general": "Hola, buen día. Escribo desde la página web de la iglesia.",
}

# Medios para ofrendas y donaciones
DONACIONES = {
    "intro": (
        "Las ofrendas sostienen el funcionamiento de la iglesia, la obra social y "
        "el apoyo a las familias de la congregación. Toda entrega es voluntaria."
    ),
    "medios": [
        {"tipo": "Cuenta de ahorros", "entidad": "Bancolombia", "numero": "000-000000-00",
         "titular": "Comunidad Cristiana Juan 3:16"},
        {"tipo": "Nequi", "entidad": "Nequi", "numero": "300 000 0000",
         "titular": "Comunidad Cristiana Juan 3:16"},
        {"tipo": "Presencial", "entidad": "En la iglesia", "numero": "Durante los cultos",
         "titular": "Ofrenda y diezmo"},
    ],
    "versiculo": {
        "texto": "Cada uno dé como propuso en su corazón: no con tristeza, ni por necesidad, "
                 "porque Dios ama al dador alegre.",
        "cita": "2 Corintios 9:7",
    },
}

# Versículo insignia de la iglesia (obligatorio en el sitio)
VERSICULO_JUAN_316 = {
    "texto": (
        "Porque de tal manera amó Dios al mundo, que ha dado a su Hijo unigénito, "
        "para que todo aquel que en él cree, no se pierda, mas tenga vida eterna."
    ),
    "cita": "Juan 3:16",
    "version": "Reina-Valera 1960",
}
