/* =========================================================================
   aula.js — comportamiento del aula del estudio bíblico
   Las tareas marcadas se guardan en el navegador de cada estudiante
   (localStorage). Es una ayuda personal, no un registro para el profesor.
   ========================================================================= */
(function () {
  'use strict';

  var LLAVE = 'juan316:tareas-hechas';

  function leer() {
    try { return JSON.parse(localStorage.getItem(LLAVE)) || {}; }
    catch (e) { return {}; }
  }

  function guardar(datos) {
    try { localStorage.setItem(LLAVE, JSON.stringify(datos)); }
    catch (e) { /* modo privado del navegador: se ignora */ }
  }

  var hechas = leer();

  document.querySelectorAll('.tarea[data-tarea]').forEach(function (tarea) {
    var id = tarea.getAttribute('data-tarea');
    var marca = tarea.querySelector('.tarea__marca');
    if (!marca) return;

    if (hechas[id]) {
      marca.classList.add('hecha');
      tarea.classList.add('completada');
    }

    marca.addEventListener('click', function () {
      var activa = marca.classList.toggle('hecha');
      tarea.classList.toggle('completada', activa);
      if (activa) { hechas[id] = true; } else { delete hechas[id]; }
      guardar(hechas);
    });
  });
})();
