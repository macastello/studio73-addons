.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

===============================================
Account Move Stock Valuation Layer Draft Button
===============================================

- Permitir pasar a borrador una factura de proveedor aunque ésta tenga valoraciones 
   de stock vinculadas, ya que el módulo `stock_account` en ese caso no muestra 
   directamente el botón `Ver código 
   <https://github.com/odoo/odoo/blob/16.0/addons/stock_account/models/account_move.py#L13>`_.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Studio73/studio73-private-addons/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Known issues / Roadmap
======================

- Por problemas técnicos se ha tenido que mostrar un nuevo botón, con nueva función, 
   ya que heredando de la función original no se mostraba el asistente con el mensaje 
   de confirmación.

Contributors
------------

* Sergi Biosca <sergi.biosca@studio73.es>

Maintainer
----------

.. image:: https://www.studio73.es/logo.png
   :alt: Studio73
   :target: https://www.studio73.es/

This module is maintained by Studio73.
