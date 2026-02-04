
.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :alt: License: LGPL-3

=================
Stock Barcode GS1
=================

- Integrar el funcionamiento de los códigos de barras GS1 con los inventarios y transferencias realizadas 
  desde la interfaz de código de barras
   
   - Que el sistema reconozca desde la primera lectura un código de este tipo, dado que 
     actualmente solo lo hace a partir de la segunda lectura, si previamente se ha 
     escaneado el código de barras del producto o del empaquetado

   - Al leer un código GS1, que automáticamente se asigne en el lote que crea Odoo, la fecha de consumo preferente 
     o la fecha de caducidad del lote, según la información que contenga el código GS1


Configuration
=============

- Es necesario que en Inventario - Configuración - Ajustes - Lectura de códigos de barra - 
  Nomenclatura de código de barras se seleccione `Default GS1 Nomenclature`


Usage
=====

- Ir a la interfaz de código de barras (ajuste inventario o transferencia interna), escanear una ubicación origen y a continuación escanear un código GS1
  tipo `(01)18480000135480(15)240715(10)240515` (es importante que el código de barras del empaquetado contenga el dígito de control)

  - (01)18480000135480: corresponde al código de barras del empaquetado del producto
  - (15)240715: corresponde a la fecha de consumo preferente del lote
  - (10)240515: corresponde a la referencia del lote

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Studio73/stock-addons/issues>`_. In case of trouble,
please check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Ioan Galan <ioan@studio73.es>

Maintainer
----------

.. image:: https://www.studio73.es/logo.png
   :alt: Studio73
   :target: https://www.studio73.es/

This module is maintained by Studio73.
