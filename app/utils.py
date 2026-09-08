"""
app/utils.py
------------
Utilidades pequeñas: filtros de Jinja para mostrar fechas en español sin
depender de la configuración regional (locale) del servidor, que suele
fallar al cambiar de computador.
"""
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MESES_CORTOS = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]


def filtros_fecha(app):
    @app.template_filter("fecha_larga")
    def fecha_larga(f):
        if not f:
            return ""
        return f"{DIAS[f.weekday()]} {f.day} de {MESES[f.month - 1]}"

    @app.template_filter("fecha_corta")
    def fecha_corta(f):
        if not f:
            return ""
        return f"{f.day} de {MESES[f.month - 1]} de {f.year}"

    @app.template_filter("dia_semana")
    def dia_semana(f):
        return DIAS[f.weekday()].capitalize() if f else ""

    @app.template_filter("mes_corto")
    def mes_corto(f):
        return MESES_CORTOS[f.month - 1] if f else ""

    @app.template_filter("hora12")
    def hora12(f):
        if not f:
            return ""
        h = f.hour % 12 or 12
        sufijo = "a. m." if f.hour < 12 else "p. m."
        return f"{h}:{f.minute:02d} {sufijo}"

    @app.template_filter("input_fecha")
    def input_fecha(f):
        """Formato que entiende <input type='datetime-local'>."""
        return f.strftime("%Y-%m-%dT%H:%M") if f else ""

    @app.template_filter("input_dia")
    def input_dia(f):
        return f.strftime("%Y-%m-%d") if f else ""
