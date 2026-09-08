"""
arrancar_pruebas.py
-------------------
Arranca el sitio en modo PRUEBA CON PERSONAS.

Diferencias con run.py (que es solo para ti, en tu computador):

  1. debug = False       -> IMPRESCINDIBLE. Con debug activo, cualquiera que
                            provoque un error obtiene una consola de Python en
                            tu computador. Nunca expongas el sitio con debug.
  2. host = 0.0.0.0      -> permite que otros dispositivos se conecten,
                            no solo esta computadora.
  3. Te muestra la       -> la dirección que debes enviarle a las personas.
     dirección a compartir

USO:
    ./venv/bin/python arrancar_pruebas.py

Para detenerlo: Ctrl + C en esta misma terminal.
Mientras esté detenido (o si apagas el computador), nadie puede entrar.
"""
import socket

from app import create_app

PUERTO = 5001


def ip_local():
    """Averigua la IP de esta computadora dentro de la red Wi-Fi."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))   # no envía nada, solo consulta la ruta
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


app = create_app()

if __name__ == "__main__":
    ip = ip_local()

    print("\n" + "=" * 62)
    print("  COMUNIDAD CRISTIANA JUAN 3:16 — modo prueba")
    print("=" * 62)
    print("\n  Para ti, en este computador:")
    print(f"    http://127.0.0.1:{PUERTO}")

    if ip:
        print("\n  Para las personas conectadas al MISMO WIFI:")
        print(f"    http://{ip}:{PUERTO}")
        print("\n  (Si cambias de red, esta dirección cambia. Vuelve a")
        print("   ejecutar este archivo para ver la nueva.)")
    else:
        print("\n  No detecté conexión de red. Solo funcionará en este computador.")

    print("\n  Modo debug: DESACTIVADO (correcto para pruebas con gente)")
    print("  Para detener el servidor: Ctrl + C")
    print("=" * 62 + "\n")

    app.run(host="0.0.0.0", port=PUERTO, debug=False)
