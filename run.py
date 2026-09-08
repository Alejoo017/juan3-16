"""
run.py
------
Punto de entrada. Se ejecuta con:   python run.py
Luego se abre en el navegador la dirección que aparece en la terminal.

Nota: en macOS el puerto 5000 lo ocupa AirPlay, por eso usamos el 5001.
Se puede cambiar con la variable de entorno PORT.
"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5001))
    # debug=True recarga el servidor al guardar un archivo y muestra los
    # errores en el navegador. En producción SIEMPRE debe ir en False.
    app.run(debug=True, port=puerto)
