.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

==================================
Stock Restrict Location By Putaway
==================================

El módulo implementa una restricción a la hora de validar transferencias de acuerdo a las
categorías de almacenamiento de las ubicaciones. De este modo, cuando se está validando
cualquier transferencia, si según las reglas de la categoría de almacenamiento la línea
no debería ir a la ubicación, se muestra un mensaje bloqueante.

El móudlo no tienen en cuenta otras entradas pendientes a la ubicación para restringir
como sí lo haría Odoo para sugerir una ubicación nueva.

Añade un campo a categorías de almacenamiento `Volumen máximo` que, de forma similar
a como funciona el de peso máximo, restringe los movimientos a una ubicación si va a 
superar el volumen máximo de la misma. Si no se rellena el campo, no se tendrá en cuenta.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Studio73/stock-addons/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Contributors
------------

* Ferran Mora <ferran@studio73.es>

Maintainer
----------

.. image:: https://www.studio73.es/logo.png
   :alt: Studio 73
   :target: https://www.studio73.es/

This module is maintained by Studio73.
All Rights Reserved.
