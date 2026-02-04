.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=======================================
Stock Quant Package Dimension Extension
=======================================

Modelo de albaranes:

* Modifica el cálculo de volumen de paquetes para que tomen sus dimensiones y, en caso de no
  tenerlas establecidas, las de su tipo de paquete.
* Este módulo implementa el volumen a nivel de albarán como la suma de volúmenes
  de sus paquetes asociados.

Wizard para poner en paquete:

* Se añade en los ajustes de inventario el check `Calcular dimensiones en base a los productos`.

* Añade una opción en los tipos de operaciones para evitar mostrar el wizard de paquetes.

Se añade la posibilidad de generar empaquetados de forma automática siempre y cuando el 
tipo de paquete tenga activo el check de generar automáticamente empaquetados.
Al generar un pedido de compra, se rellena la cantidad con la cantidad del empaquetado por defecto 
para las compras. Esto se configura en ajsutes de compra con el campo `Forzar cantidad según el paquete`
Se añaden restricciones para no tener varios empaquetados por defecto para compras o ventas.

Añade un campo en Ajustes > Inventario > Paquetes > **Tipo de paquete por defecto**
donde se puede seleccionar el tipo de paquete que se asignará por defecto a los nuevos
paquetes.
Añade también un campo a los tipos de paquetes **Secuencia de paquetes** donde se peude
seleccionar una secuencia para los nuevos paquetes que se generen con este tipo.

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

* Ferran Mora <ferran@studio73.es>

Maintainer
----------

.. image:: https://www.studio73.es/logo.png
   :alt: Studio73
   :target: https://www.studio73.es/

This module is maintained by Studio73.
