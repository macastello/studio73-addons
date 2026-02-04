
.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :alt: License: LGPL-3

=======================
Stock Barcode Usability
=======================

- Mejoras de usabilidad en la interfaz de código de barras:

    - Añade la posibilidad de ocultar el botón de añadir producto en PDA [1]
    - Añade un campo a tipos de operaciones para permitir introducir más cantidad de la 
      reservada.
    - Modifica el proceso de escaneo de paquete en albaranes de modo que lo asigne como
      destino si está totalmente contenido en el albarán incluso si la línea venía
      prereservada.
    - Añade la posibilidad de forzar sumar unidad al escanear un producto en PDA en 
      albaranes y ajsutes de inventario incluso si este tiene seguimiento por lotes. [3]
    - Se añade la posibilidad de cerrar una agrupación siempre que se pulse validar,
      incluso si no se ha validado por completo [4]. Útil para los que usan el módulo
      stock_picking_batch_propagate.
    - Añade un contador de líneas en la cabecera de la PDA. [5]
    - Posibilidad de no agrupar líneas en la vista de PDA. [6]
    - Añade una opción para restringir el escaneo de productos, lotes y paquetes a 
      aquellos que están préviamente reservados para el albarán / agrupación actual. [7]
    - Añade una opción para aplicar ubicación destino desde la PDA a todas las líneas
      picadas. [8] Además, si se acaba de leer un paquete y luego se lee destino, se
      fuerza que se aplique su ubicación a todas las líneas del mismo.
    - Añade un campo `Agrupar líneas por ubicación y producto` en tipos de operaciones
      que agrupa las líneas en la PDA por ubicación y producto, de modo que si hay
      varias ubicaciones con el mismo producto se muestran como líneas separadas.
      Útil para evitar errores al picar en ubicaciones con stock mixto.


Configuration
=============

- [1] Para ocultar el botón de añadir producto en PDA se debe desmarcar el campo
  `¿Permitir añadir producto PDA?` en el tipo de operación deseado
- [2] `¿Permitir más cantidad de la reservada en PDA?`
- [3] En tipos de operaciones se configura con el campo `Forzar sumar cantidad al escanear producto`
  y para ajsutes de inventario se debe configurar en Ajustes > Inventario > Código de barras
  > `Forzar sumar cantidad al escanear producto`
- [4] Se debe marcar el campo en tipos de operaciones `PDA Agrupaciones: Cerrar agrupación parcial`
- [5] Se debe marcar el campo en tipos de operaciones `Mostrar contador de líneas`
- [6] En tipos de operaciones marcar el campo `PDA: Evitar agrupar líneas`
- [7] En tipos de operaciones marcar el campo `Restringir escaneo a productos del albarán`
- [8] En tipos de operaciones marcar el campo `PDA: Aplicar ubicación destino a todas las líneas`
- [9] En tipos de operaciones marcar el campo `Agrupar líneas por ubicación y producto` para activar
  la agrupación de líneas por ubicación y producto en la PDA.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Studio73/stock-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Ioan Galan <ioan@studio73.es>
* Ferran Mora <ferran@studio73.es>

Maintainer
----------

.. image:: https://www.studio73.es/logo.png
   :alt: Consultoría Informática Studio 73 S.L.
   :target: https://www.studio73.es/

This module is maintained by Studio73.