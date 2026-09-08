"""
semilla.py
----------
Llena la base de datos con el contenido inicial del sitio.
Se ejecuta una sola vez:      python semilla.py
Para borrar todo y empezar de cero:   python semilla.py --reiniciar

OJO: los textos de abajo son un punto de partida. Edítalos con la información
real de la iglesia (o cámbialos desde el panel de administración).
"""
import os
import sys
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models import (Anuncio, Clase, Culto, Evento, Ministerio, Pastor,
                        Recurso, Tarea, Usuario)

app = create_app()

# Contraseñas iniciales de los tres accesos de arranque.
# Se pueden cambiar con variables de entorno, por ejemplo:
#     CLAVE_ADMIN="MiClaveSegura2026" python semilla.py
# CÁMBIALAS SIEMPRE desde el panel después del primer ingreso.
CLAVE_ADMIN = os.environ.get("CLAVE_ADMIN", "CambiarEstaClave1")
CLAVE_PASTOR = os.environ.get("CLAVE_PASTOR", "CambiarEstaClave2")
CLAVE_ALUMNO = os.environ.get("CLAVE_ALUMNO", "CambiarEstaClave3")


def proximo_dia(dia_semana, hora, minuto=0, semanas=0):
    """Devuelve la próxima fecha que caiga en ese día de la semana (0=lunes)."""
    hoy = datetime.now().replace(hour=hora, minute=minuto, second=0, microsecond=0)
    faltan = (dia_semana - hoy.weekday()) % 7
    return hoy + timedelta(days=faltan + semanas * 7)


with app.app_context():
    if "--reiniciar" in sys.argv:
        db.drop_all()
        print("· Tablas borradas")

    db.create_all()

    # -----------------------------------------------------------------------
    # USUARIOS
    # -----------------------------------------------------------------------
    if not Usuario.query.first():
        admin = Usuario(usuario="isai", nombre="Isaí Sánchez", rol="admin",
                        nivel="Docente", correo="isai@comunidadjuan316.org")
        admin.poner_contrasena(CLAVE_ADMIN)

        admin2 = Usuario(usuario="omar", nombre="Omar", rol="admin",
                         nivel="Pastor", correo="omar@comunidadjuan316.org")
        admin2.poner_contrasena(CLAVE_PASTOR)

        alumno = Usuario(usuario="estudiante", nombre="Estudiante de prueba",
                         rol="estudiante", nivel="Nivel 1")
        alumno.poner_contrasena(CLAVE_ALUMNO)

        db.session.add_all([admin, admin2, alumno])
        print("· Usuarios creados")

    # -----------------------------------------------------------------------
    # PASTORES
    # -----------------------------------------------------------------------
    if not Pastor.query.first():
        db.session.add_all([
            Pastor(
                nombre="Pastor Omar",
                cargo="Pastor principal",
                anios_servicio=25, desde=2001,
                enfasis="Predicación expositiva · Acompañamiento pastoral · Familia",
                resena=("Acompaña a la congregación desde sus inicios. Dedica buena parte "
                        "de su semana a la visita pastoral, la consejería a las familias y "
                        "la preparación de la enseñanza dominical. Su trabajo se ha centrado "
                        "en formar una congregación que conozca las Escrituras y se sostenga "
                        "en comunidad."),
                foto="pastor-omar.jpg", orden=1,
            ),
            Pastor(
                nombre="Isaí Sánchez",
                cargo="Pastor · Director del estudio bíblico",
                anios_servicio=12, desde=2014,
                enfasis="Enseñanza bíblica · Discipulado · Formación de nuevos creyentes",
                resena=("Dirige el programa de estudio bíblico y el discipulado de la "
                        "iglesia. Su trabajo consiste en acompañar, semana a semana, a "
                        "quienes quieren entender las Escrituras con orden y profundidad, "
                        "desde los fundamentos hasta la preparación para servir."),
                foto="pastor-isai.jpg", orden=2,
            ),
        ])
        print("· Pastores creados")

    # -----------------------------------------------------------------------
    # HORARIOS DE CULTO
    # -----------------------------------------------------------------------
    if not Culto.query.first():
        db.session.add_all([
            Culto(nombre="Culto general", dia="Domingo", hora="9:00 a. m.",
                  descripcion="Servicio principal con predicación, alabanza y santa cena el primer domingo del mes.",
                  dirigido_a="Toda la congregación", orden=1),
            Culto(nombre="Escuela dominical", dia="Domingo", hora="11:00 a. m.",
                  descripcion="Enseñanza por edades para niños, jóvenes y adultos.",
                  dirigido_a="Por edades", orden=2),
            Culto(nombre="Culto de oración", dia="Miércoles", hora="7:00 p. m.",
                  descripcion="Tiempo de intercesión por la iglesia, las familias y la ciudad.",
                  dirigido_a="Toda la congregación", orden=3),
            Culto(nombre="Estudio bíblico", dia="Viernes", hora="7:00 p. m.",
                  descripcion="Clase del programa de formación dirigida por el pastor Isaí Sánchez.",
                  dirigido_a="Estudiantes inscritos", orden=4),
            Culto(nombre="Reunión de jóvenes", dia="Sábado", hora="4:00 p. m.",
                  descripcion="Encuentro de jóvenes y adolescentes.",
                  dirigido_a="12 a 28 años", orden=5),
        ])
        print("· Horarios creados")

    # -----------------------------------------------------------------------
    # MINISTERIOS
    # -----------------------------------------------------------------------
    if not Ministerio.query.first():
        db.session.add_all([
            Ministerio(nombre="Niños", icono="✦", responsable="Equipo de escuela dominical",
                       descripcion="Enseñanza bíblica adaptada por edades, con acompañamiento durante el culto general.", orden=1),
            Ministerio(nombre="Jóvenes", icono="✧", responsable="Liderazgo juvenil",
                       descripcion="Espacio de formación, servicio y compañerismo para adolescentes y jóvenes adultos.", orden=2),
            Ministerio(nombre="Matrimonios y familia", icono="◈", responsable="Pastor Omar",
                       descripcion="Encuentros y consejería para parejas y padres de familia.", orden=3),
            Ministerio(nombre="Alabanza", icono="♪", responsable="Equipo de música",
                       descripcion="Servicio musical de los cultos y formación de nuevos músicos.", orden=4),
            Ministerio(nombre="Oración e intercesión", icono="◇", responsable="Grupo de intercesión",
                       descripcion="Cadena de oración permanente por los motivos de la congregación.", orden=5),
            Ministerio(nombre="Acción social", icono="◎", responsable="Diaconía",
                       descripcion="Apoyo con alimentos y acompañamiento a familias de la comunidad.", orden=6),
        ])
        print("· Ministerios creados")

    # -----------------------------------------------------------------------
    # EVENTOS
    # -----------------------------------------------------------------------
    if not Evento.query.first():
        db.session.add_all([
            Evento(titulo="Vigilia de oración", categoria="Oración", destacado=True,
                   fecha=proximo_dia(4, 20, semanas=1),
                   lugar="Templo principal",
                   descripcion="Noche de oración e intercesión por las familias de la congregación y por la ciudad."),
            Evento(titulo="Encuentro de matrimonios", categoria="Familia",
                   fecha=proximo_dia(5, 15, semanas=2),
                   lugar="Salón comunal",
                   descripcion="Jornada de enseñanza y diálogo para parejas. Incluye refrigerio; se requiere inscripción previa."),
            Evento(titulo="Bautismos", categoria="Congregación", destacado=True,
                   fecha=proximo_dia(6, 9, semanas=4),
                   lugar="Templo principal",
                   descripcion="Ceremonia de bautismo para quienes terminaron el curso de fundamentos."),
            Evento(titulo="Jornada de acción social", categoria="Servicio",
                   fecha=proximo_dia(5, 8, semanas=5),
                   lugar="Barrio Ejemplo",
                   descripcion="Entrega de mercados y visita a familias del sector."),
        ])
        print("· Eventos creados")

    # -----------------------------------------------------------------------
    # CLASES DEL ESTUDIO + TAREAS
    # -----------------------------------------------------------------------
    if not Clase.query.first():
        c1 = Clase(
            titulo="La autoridad de las Escrituras",
            tema="Fundamentos · Bibliología",
            nivel="Nivel 1",
            fecha=proximo_dia(4, 19),
            modalidad="Presencial", lugar="Salón de estudio, segundo piso",
            descripcion=("Cómo se formó el canon bíblico, en qué sentido decimos que la Biblia "
                         "es palabra de Dios y qué implica eso para la manera en que la leemos."),
        )
        c1.tareas = [
            Tarea(titulo="Lectura previa", cita_biblica="2 Timoteo 3:14-17",
                  descripcion="Leer el pasaje tres veces y anotar qué dice el texto sobre el propósito de las Escrituras.",
                  fecha_entrega=(proximo_dia(4, 19) - timedelta(days=1)).date()),
            Tarea(titulo="Cuadro de resumen",
                  descripcion="Escribir en media página la diferencia entre Antiguo y Nuevo Testamento, con dos ejemplos de cada uno."),
        ]

        c2 = Clase(
            titulo="Cómo estudiar un pasaje bíblico",
            tema="Fundamentos · Método de estudio",
            nivel="Nivel 1",
            fecha=proximo_dia(4, 19, semanas=1),
            modalidad="Mixta", lugar="Salón de estudio y transmisión en vivo",
            enlace="",
            descripcion=("Observación, interpretación y aplicación: los tres pasos para acercarse "
                         "a un texto sin sacarlo de contexto."),
        )
        c2.tareas = [
            Tarea(titulo="Ejercicio de observación", cita_biblica="Filipenses 2:1-11",
                  descripcion="Aplicar los tres pasos vistos en clase sobre el pasaje asignado y traerlo por escrito.",
                  fecha_entrega=(proximo_dia(4, 19, semanas=1)).date()),
        ]

        c3 = Clase(
            titulo="La persona de Jesús en los Evangelios",
            tema="Fundamentos · Cristología",
            nivel="Nivel 1",
            fecha=proximo_dia(4, 19, semanas=2),
            modalidad="Presencial", lugar="Salón de estudio, segundo piso",
            descripcion="Quién es Jesús según el testimonio de Mateo, Marcos, Lucas y Juan.",
        )
        c3.tareas = [
            Tarea(titulo="Lectura del Evangelio de Marcos", cita_biblica="Marcos 1-4",
                  descripcion="Leer los primeros cuatro capítulos y anotar tres preguntas para la clase."),
        ]

        c4 = Clase(
            titulo="Arrepentimiento, fe y bautismo",
            tema="Fundamentos · Vida cristiana",
            nivel="Nivel 1",
            fecha=proximo_dia(4, 19, semanas=3),
            modalidad="Presencial", lugar="Salón de estudio, segundo piso",
            descripcion="Qué enseña el Nuevo Testamento sobre la conversión y el bautismo.",
        )

        db.session.add_all([c1, c2, c3, c4])
        print("· Clases y tareas creadas")

    # -----------------------------------------------------------------------
    # AVISOS Y MATERIAL DEL AULA
    # -----------------------------------------------------------------------
    if not Anuncio.query.first():
        db.session.add_all([
            Anuncio(titulo="Bienvenidos al aula del estudio bíblico", fijado=True,
                    contenido=("Aquí encontrarás el cronograma de clases, las tareas de cada sesión, "
                               "el enlace de las clases virtuales y el material de apoyo. "
                               "Si algo no te carga o pierdes tu contraseña, escribe a la administración.")),
            Anuncio(titulo="Recuerda traer tu Biblia y cuaderno",
                    contenido="Trabajamos directamente sobre el texto bíblico; el material impreso es un apoyo, no un reemplazo."),
        ])
        db.session.add_all([
            Recurso(titulo="Guía de estudio · Nivel 1", tipo="Documento",
                    descripcion="Cuadernillo con los cuatro módulos de fundamentos y los ejercicios de cada sesión."),
            Recurso(titulo="Plan de lectura bíblica anual", tipo="Lectura",
                    descripcion="Distribución de lecturas para recorrer toda la Biblia en un año."),
            Recurso(titulo="Cómo hacer un cuadro de observación", tipo="Video",
                    descripcion="Explicación paso a paso del método que usamos en clase."),
        ])
        print("· Avisos y material creados")

    db.session.commit()

print("""
Base de datos lista.

Accesos creados. CÁMBIALOS desde el panel en cuanto entres:
  Administrador   usuario: isai
  Administrador   usuario: omar
  Estudiante      usuario: estudiante

Las contraseñas son las definidas en CLAVE_ADMIN, CLAVE_PASTOR y CLAVE_ALUMNO
al inicio de este archivo (o en las variables de entorno del mismo nombre).
""")
