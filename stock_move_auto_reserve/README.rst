.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=======================
Stock Move Auto Reserve
=======================

- El módulo se encarga de volver a reservar mercancía que estaba reservada para un
  movimiento y que se reubica.
- Para que la reserva se haga de nuevo se tienen que cumplir las siguientes condiciones:

  - El movimiento de reubicación que se valida debe tener marcado en su tipo de operación
    el nuevo campo `Permitir reubicar reserva`.
  - La ubicación a la que se mueve debe ser hija de la ubicación de origen del movimiento
    para el cual estaba reservado.


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
   :alt: Consultoría Informática Studio 73 S.L.
   :target: https://www.studio73.es/

This module is maintained by Studio73.
