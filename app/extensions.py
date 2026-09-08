"""
app/extensions.py
-----------------
Aquí se CREAN las extensiones de Flask, pero todavía "vacías" (sin app).
Se conectan a la aplicación más adelante, dentro de create_app().

¿Por qué separado? Para evitar imports circulares:
models.py necesita 'db', y create_app() necesita 'models'. Si 'db' viviera
dentro de create_app, Python entraría en un bucle de importaciones.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()          # ORM: convierte clases de Python en tablas de SQLite
login_manager = LoginManager()   # Maneja sesión, cookies y @login_required

# A dónde se redirige a alguien que entra a una página privada sin sesión
login_manager.login_view = "estudio.login"
login_manager.login_message = "Necesitas iniciar sesión para entrar al aula."
login_manager.login_message_category = "aviso"
