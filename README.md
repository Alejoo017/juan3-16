# Comunidad Cristiana Juan 3:16 — sitio web

Sitio web para una iglesia local, construido con **Flask, SQLite y HTML/CSS/JS**
sin frameworks de frontend.

El proyecto resuelve dos necesidades distintas en una sola aplicación:

1. **Un sitio público** donde cualquier persona —incluida la que nunca ha
   asistido— puede conocer la iglesia: quiénes son los pastores, los horarios de
   las reuniones, los ministerios, los eventos próximos y cómo contactarla.
2. **Un aula privada** para el programa de estudio bíblico, con acceso mediante
   usuario y contraseña, donde los estudiantes inscritos ven su cronograma, las
   tareas de cada clase y el enlace de las sesiones virtuales.

> *«Porque de tal manera amó Dios al mundo, que ha dado a su Hijo unigénito, para
> que todo aquel que en él cree, no se pierda, mas tenga vida eterna.»*
> — Juan 3:16

---

## Funcionalidades

### Sitio público

- Página única con navegación por secciones
- Presentación de los pastores con años de ministerio y área de enfoque
- Horarios de reuniones semanales
- Calendario mensual interactivo que combina las reuniones habituales con los
  eventos especiales
- Listado de ministerios
- Eventos próximos con fecha, lugar y descripción
- Sección de ofrendas con los medios de donación
- Formulario de contacto que guarda los mensajes en la base de datos
- Enlaces directos a WhatsApp con mensaje pre-escrito
- Diseño responsive

### Aula del estudio bíblico

- Autenticación con contraseñas cifradas (`pbkdf2:sha256`)
- Panel del estudiante con las dos próximas clases y sus tareas
- Calendario mensual navegable que marca los días de clase
- Botón de acceso al enlace de la clase virtual
- Cronograma completo, material de apoyo y avisos
- Cambio de contraseña desde el perfil

### Panel de administración

- Crear y editar clases, con su enlace y sus tareas
- Publicar avisos y material de apoyo
- Gestionar los accesos de los estudiantes (crear, editar, restablecer
  contraseña, desactivar, eliminar)
- Publicar eventos del sitio público
- Bandeja de los mensajes del formulario de contacto

---

## Tecnologías

| Capa | Herramienta |
|---|---|
| Servidor | Flask 3.1 |
| Base de datos | SQLite con SQLAlchemy (ORM) |
| Sesiones | Flask-Login |
| Plantillas | Jinja2 |
| Frontend | HTML, CSS y JavaScript sin dependencias |
| Tipografías | Fraunces e Inter |

No usa React, Vue, Bootstrap ni Tailwind. El CSS está escrito a mano sobre
variables, y el JavaScript es JS estándar sin librerías.

---

## Instalación

Requiere Python 3.9 o superior.

```bash
# 1. Clonar el repositorio
git clone https://github.com/USUARIO/REPOSITORIO.git
cd REPOSITORIO

# 2. Crear el entorno virtual
python3 -m venv venv

# 3. Instalar las dependencias
./venv/bin/pip install -r requirements.txt

# 4. Crear tu configuración a partir de la plantilla
cp config.example.py config.py
#    Edita config.py con los datos de tu iglesia

# 5. Llenar la base de datos con el contenido inicial
./venv/bin/python semilla.py

# 6. Arrancar el servidor
./venv/bin/python run.py
```

Abre **http://127.0.0.1:5001** en el navegador.

> En macOS el puerto 5000 lo ocupa AirPlay; por eso el proyecto usa el 5001.
> Se puede cambiar con `PORT=8000 ./venv/bin/python run.py`.

### Primeros pasos

`semilla.py` crea tres accesos (`isai`, `omar` y `estudiante`) con las
contraseñas definidas al inicio de ese archivo. **Cámbialas desde el panel de
administración en cuanto ingreses por primera vez.**

También puedes definirlas al momento de crear la base de datos:

```bash
CLAVE_ADMIN="tu-clave" CLAVE_PASTOR="otra-clave" CLAVE_ALUMNO="otra-mas" \
  ./venv/bin/python semilla.py
```

---

## Estructura del proyecto

```
.
├── run.py                  Arranca el servidor de desarrollo
├── arrancar_pruebas.py     Arranca el servidor accesible en la red local
├── config.example.py       Plantilla de configuración
├── semilla.py              Contenido inicial de la base de datos
├── gestionar.py            Administración de usuarios desde la terminal
├── requirements.txt
└── app/
    ├── __init__.py         Application factory
    ├── extensions.py       Instancias de SQLAlchemy y Flask-Login
    ├── models.py           Modelos: 10 tablas
    ├── utils.py            Filtros de fecha en español
    ├── routes/
    │   ├── publico.py      Sitio público
    │   ├── estudio.py      Presentación, login y aula
    │   └── admin.py        Panel de administración
    ├── templates/          Plantillas Jinja2
    └── static/             CSS, JavaScript e imágenes
```

### Arquitectura

El proyecto usa el patrón **application factory**: la aplicación se construye
dentro de `create_app()` en vez de vivir en una variable global. Eso permite
crear instancias con configuraciones distintas (por ejemplo, para pruebas) y
evita imports circulares.

Las rutas están agrupadas en tres **blueprints**:

| Blueprint | Prefijo | Responsabilidad |
|---|---|---|
| `publico` | `/` | Sitio institucional |
| `estudio` | `/estudio` | Presentación del programa, login y aula |
| `admin` | `/estudio/admin` | Administración, protegida por rol |

El acceso se controla con `@login_required` para el aula y con un decorador
propio, `@solo_admin`, para el panel de administración.

---

## Administración desde la terminal

`gestionar.py` permite administrar los accesos sin abrir el sitio. Es útil si se
pierde la contraseña de administrador.

```bash
./venv/bin/python gestionar.py listar        # ver todas las personas
./venv/bin/python gestionar.py crear         # crear un acceso
./venv/bin/python gestionar.py clave USUARIO # cambiar una contraseña
./venv/bin/python gestionar.py borrar USUARIO
./venv/bin/python gestionar.py resumen       # estado de la base de datos
./venv/bin/python gestionar.py respaldo      # copia de seguridad
```

---

## Estado del proyecto

En desarrollo. El sitio es funcional y está en fase de pruebas.

**Antes de desplegarlo en un servidor público** hacen falta cuatro cosas que
todavía no están implementadas:

- Protección CSRF en los formularios (Flask-WTF)
- `SECRET_KEY` provista por variable de entorno, sin valor por defecto
- Límite de intentos en el formulario de login
- Banderas `Secure`, `HttpOnly` y `SameSite` en las cookies de sesión

Además, en producción debe usarse un servidor WSGI como Gunicorn o Waitress con
`debug=False`, y servirse siempre sobre HTTPS.

Lo que sí está resuelto: contraseñas cifradas con `pbkdf2:sha256` (600.000
iteraciones), consultas a través del ORM (sin construcción manual de SQL),
autoescapado de plantillas y control de acceso por rol.

---

## Configuración

`config.py` no se versiona: contiene datos de contacto, cuentas de donación y la
clave de sesión. Para crear el tuyo, copia la plantilla:

```bash
cp config.example.py config.py
```

Ahí se definen el nombre de la iglesia, la dirección, los números de WhatsApp,
las redes sociales, los medios de donación y el mapa.

Las imágenes van en:

- `app/static/img/logo/logo.png`
- `app/static/img/pastores/`

Si falta alguna, el sitio muestra un reemplazo generado y no se rompe.

---

## Licencia

Sin licencia definida por ahora. Si quieres reutilizar el código, escribe al
autor del repositorio.
