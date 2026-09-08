/* =========================================================================
   principal.js — comportamiento del sitio público
   Todo va dentro de un IIFE para no ensuciar el ámbito global.
   ========================================================================= */
(function () {
  'use strict';

  /* ---------- 1. Menú móvil ---------------------------------------------- */
  var hamburguesa = document.getElementById('hamburguesa');
  var menu = document.getElementById('menu');

  if (hamburguesa && menu) {
    hamburguesa.addEventListener('click', function () {
      var abierto = menu.classList.toggle('abierto');
      hamburguesa.classList.toggle('abierta', abierto);
      hamburguesa.setAttribute('aria-expanded', abierto ? 'true' : 'false');
    });

    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        menu.classList.remove('abierto');
        hamburguesa.classList.remove('abierta');
        hamburguesa.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- 2. Sombra de la cabecera al bajar --------------------------- */
  var cabecera = document.getElementById('cabecera');
  if (cabecera) {
    var alDesplazar = function () {
      cabecera.classList.toggle('desplazada', window.scrollY > 10);
    };
    alDesplazar();
    window.addEventListener('scroll', alDesplazar, { passive: true });
  }

  /* ---------- 3. Aparición suave de las secciones ------------------------- */
  var elementos = document.querySelectorAll('.revelar');
  if ('IntersectionObserver' in window && elementos.length) {
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          observador.unobserve(e.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    elementos.forEach(function (el) { observador.observe(el); });
  } else {
    elementos.forEach(function (el) { el.classList.add('visible'); });
  }

  /* ---------- 4. Enlace activo del menú según la sección visible ---------- */
  var secciones = document.querySelectorAll('main section[id]');
  var enlacesMenu = menu ? menu.querySelectorAll('a[href*="#"]') : [];
  if ('IntersectionObserver' in window && secciones.length && enlacesMenu.length) {
    var observadorMenu = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (!e.isIntersecting) return;
        enlacesMenu.forEach(function (a) {
          a.classList.toggle('activo', a.getAttribute('href').endsWith('#' + e.target.id));
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    secciones.forEach(function (s) { observadorMenu.observe(s); });
  }

  /* ---------- 5. Avisos flash: cerrar y auto-ocultar ---------------------- */
  var avisos = document.getElementById('avisos');
  if (avisos) {
    avisos.addEventListener('click', function (e) {
      var boton = e.target.closest('.aviso__cerrar');
      if (boton) boton.parentElement.remove();
    });
    setTimeout(function () {
      avisos.querySelectorAll('.aviso').forEach(function (a) {
        a.style.transition = 'opacity .4s ease, transform .4s ease';
        a.style.opacity = '0';
        a.style.transform = 'translateX(16px)';
        setTimeout(function () { a.remove(); }, 420);
      });
    }, 6000);
  }

  /* ---------- 6. Copiar al portapapeles ---------------------------------- */
  document.addEventListener('click', function (e) {
    var boton = e.target.closest('[data-copiar]');
    if (!boton) return;

    var texto = boton.getAttribute('data-copiar');
    var original = boton.innerHTML;

    var confirmar = function () {
      boton.textContent = 'Copiado';
      setTimeout(function () { boton.innerHTML = original; }, 1800);
    };

    if (navigator.clipboard) {
      navigator.clipboard.writeText(texto).then(confirmar);
    } else {
      var campo = document.createElement('textarea');
      campo.value = texto;
      document.body.appendChild(campo);
      campo.select();
      try { document.execCommand('copy'); confirmar(); } catch (err) { /* nada */ }
      document.body.removeChild(campo);
    }
  });

  /* ---------- 7. Calendario público -------------------------------------- */
  var contenedorCal = document.getElementById('calendario-publico');
  var datosCrudos = document.getElementById('datos-calendario');
  if (!contenedorCal || !datosCrudos) return;

  var datos;
  try { datos = JSON.parse(datosCrudos.textContent); }
  catch (err) { return; }

  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS_SEMANA = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

  var hoy = new Date();
  var verAnio = hoy.getFullYear();
  var verMes = hoy.getMonth();       // 0-11

  var elMes = document.getElementById('cal-mes');
  var elCuerpo = document.getElementById('cal-cuerpo');
  var elDetalle = document.getElementById('cal-detalle');

  // Reuniones habituales indexadas por número de día de la semana (0 = domingo)
  var cultosPorDia = {};
  datos.cultos.forEach(function (c) {
    var indice = DIAS_SEMANA.indexOf(c.dia);
    if (indice === -1) return;
    if (!cultosPorDia[indice]) cultosPorDia[indice] = [];
    cultosPorDia[indice].push(c);
  });

  // Eventos especiales indexados por 'AAAA-MM-DD'
  var eventosPorFecha = {};
  datos.eventos.forEach(function (e) {
    if (!eventosPorFecha[e.fecha]) eventosPorFecha[e.fecha] = [];
    eventosPorFecha[e.fecha].push(e);
  });

  function claveFecha(anio, mes, dia) {
    return anio + '-' + String(mes + 1).padStart(2, '0') + '-' + String(dia).padStart(2, '0');
  }

  function dibujar() {
    elMes.textContent = MESES[verMes] + ' ' + verAnio;
    elCuerpo.innerHTML = '';

    var primero = new Date(verAnio, verMes, 1);
    var diasEnMes = new Date(verAnio, verMes + 1, 0).getDate();
    var diasMesAnterior = new Date(verAnio, verMes, 0).getDate();
    // getDay(): 0=domingo. Queremos que la semana empiece en lunes.
    var desplazamiento = (primero.getDay() + 6) % 7;

    var celdas = [];

    for (var i = desplazamiento; i > 0; i--) {
      celdas.push({ dia: diasMesAnterior - i + 1, fuera: true });
    }
    for (var d = 1; d <= diasEnMes; d++) {
      celdas.push({ dia: d, fuera: false });
    }
    while (celdas.length % 7 !== 0) {
      celdas.push({ dia: celdas.length - desplazamiento - diasEnMes + 1, fuera: true });
    }

    celdas.forEach(function (celda) {
      var div = document.createElement('div');
      div.className = 'dia';

      if (celda.fuera) {
        div.classList.add('dia--fuera');
        div.textContent = celda.dia;
        elCuerpo.appendChild(div);
        return;
      }

      var fecha = new Date(verAnio, verMes, celda.dia);
      var clave = claveFecha(verAnio, verMes, celda.dia);
      var eventosDelDia = eventosPorFecha[clave] || [];
      var cultosDelDia = cultosPorDia[fecha.getDay()] || [];

      div.textContent = celda.dia;

      if (fecha.toDateString() === hoy.toDateString()) div.classList.add('dia--hoy');

      if (eventosDelDia.length || cultosDelDia.length) {
        div.classList.add('dia--evento');

        var puntos = document.createElement('div');
        puntos.className = 'dia__puntos';
        cultosDelDia.forEach(function () {
          var p = document.createElement('i');
          p.className = 'punto punto--culto';
          puntos.appendChild(p);
        });
        eventosDelDia.forEach(function () {
          var p = document.createElement('i');
          p.className = 'punto';
          puntos.appendChild(p);
        });
        div.appendChild(puntos);

        var resumen = [];
        cultosDelDia.forEach(function (c) { resumen.push(c.nombre + ' · ' + c.hora); });
        eventosDelDia.forEach(function (e) { resumen.push(e.titulo + ' · ' + e.hora); });
        div.title = resumen.join('\n');

        div.addEventListener('click', function () {
          elDetalle.textContent = celda.dia + ' de ' + MESES[verMes] + ': ' + resumen.join('  /  ');
        });
      }

      elCuerpo.appendChild(div);
    });
  }

  document.getElementById('cal-anterior').addEventListener('click', function () {
    verMes--; if (verMes < 0) { verMes = 11; verAnio--; }
    elDetalle.textContent = '';
    dibujar();
  });

  document.getElementById('cal-siguiente').addEventListener('click', function () {
    verMes++; if (verMes > 11) { verMes = 0; verAnio++; }
    elDetalle.textContent = '';
    dibujar();
  });

  dibujar();
})();
