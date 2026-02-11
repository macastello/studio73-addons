.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

================
Connector Edicom
================

Módulo de integración EDI (Electronic Data Interchange) con Edicom que permite la importación y exportación automática de documentos comerciales en formato estándar EDI.

Funcionalidades
===============

Exportación EDI
---------------

**Facturas (INVOIC)**

Exporta facturas de cliente al formato EDI INVOIC compatible con Edicom. La exportación incluye:

* Cabecera de factura con datos del vendedor, comprador y receptor
* Líneas de factura con detalles de productos, cantidades y precios
* Información de impuestos (IVA) y totales
* Números de lote de producción asociados a las líneas de factura
* Datos de dirección y NIF del cliente
* Condiciones de pago y vencimientos

**Albaranes (DESADV)**

Exporta albaranes/transferencias al formato EDI DESADV (Despatch Advice). La exportación incluye:

* Datos de la expedición y entrega
* Información de paquetes y embalajes
* Líneas de movimiento con productos, cantidades y ubicaciones
* Referencias a pedidos originales
* Información de pallets y unidades de carga

Importación EDI
---------------

**Pedidos de Venta**

Importa pedidos desde archivos EDI en formato Edicom. El proceso:

* Lee archivos CABPED (cabecera de pedido), LINPED (líneas) y OBSPED (observaciones)
* Crea presupuestos/pedidos automáticamente con toda la información
* Vincula productos mediante códigos EAN13
* Establece fechas de entrega y referencias de cliente
* Asigna equipos de ventas y empresas

Integración FTP
---------------

El módulo incluye conectividad FTP para automatizar el intercambio de archivos:

* Exportación automática de archivos a servidor FTP de Edicom
* Configuración flexible de rutas de exportación
* Manejo de credenciales mediante parámetros del sistema

Configuración
=============

Parámetros del Sistema
----------------------

Configurar la conexión FTP en **Configuración > Técnico > Parámetros del Sistema**:

* **edicom.ftp.connection**: Cadena de conexión en formato ``host:port:user:password``

  Ejemplo: ``ftp.edicom.com:21:usuario:contraseña``

Configuración de Partners
--------------------------

Para habilitar la integración EDI en un partner, configurar los siguientes campos en **Contactos**:

**Campo EAN13** (``edicom_ean13``)
    Código EAN13 del partner para identificación EDI. Requerido para exportación de facturas y albaranes.

**Código Corto Comprador** (``eci_buyer_code``)
    Código que se concatena con el código del pedido en la importación EDI.

**Ruta Exportación Facturas** (``edicom_export_invoice_path``)
    Ruta en el servidor FTP donde se exportarán las facturas.

    * Valor por defecto: ``./PRODUCCION/SALIDA/``
    * Se puede personalizar por partner

Configuración de Facturas
--------------------------

En las facturas de cliente, existe un campo adicional:

**Cliente EDI** (``edicom_partner_id``)
    Si el cliente destino es diferente a la dirección de entrega de la factura,
    seleccionarlo aquí. Esto afecta al campo 'CLIENTE' del fichero EDI generado.

Uso
===

Exportar Facturas
-----------------

Las facturas se exportan automáticamente al confirmarlas si:

* El partner tiene configurado un código ``edicom_ean13``
* La dirección de envío tiene configurado un código ``edicom_ean13``
* El tipo de factura es ``out_invoice`` (factura de cliente)

Para exportar manualmente:

1. Ir a **Facturación > Clientes > Facturas**
2. Seleccionar una o más facturas
3. Hacer clic en **Acción > Export Invoice to Edicom**

El sistema generará:

* Un archivo EDI con el formato INVOIC
* Adjunto en el chatter de la factura
* Exportación automática al servidor FTP (si está configurado)

Exportar Albaranes
------------------

Para exportar albaranes/transferencias:

1. Ir a **Inventario > Operaciones > Transferencias**
2. Seleccionar uno o más albaranes validados
3. Hacer clic en **Acción > Export Transfer to Edicom**

El sistema generará:

* Un archivo EDI con el formato DESADV
* Adjunto en el chatter del albarán
* Exportación automática al servidor FTP (si está configurado)

Importar Pedidos
----------------

Para importar pedidos desde archivos EDI:

1. Ir a **Ventas > Configuración > Importar Pedidos EDI**
2. Seleccionar la compañía y equipo de ventas
3. Adjuntar uno o más archivos EDI (CABPED, LINPED, OBSPED)
4. Hacer clic en **Importar**

El sistema:

* Procesará los archivos y creará presupuestos automáticamente
* Mostrará los presupuestos creados al finalizar
* Los pedidos estarán en estado borrador para revisión

Configuraciones EDI
===================

El módulo incluye configuraciones predefinidas para mapeo de campos:

**Exportación de Facturas**
    Configuración: ``connector_edicom.edicom_export_invoice_data``

    Archivos generados:

    * CABFAC.TXT - Cabecera y pie de factura
    * LINFAC.TXT - Líneas de factura
    * ADICFAC.TXT - Información adicional

**Exportación de Albaranes**
    Configuración: ``connector_edicom.edicom_export_picking_data``

    Archivos generados:

    * CABDES.TXT - Cabecera del aviso de expedición
    * LINDES.TXT - Líneas de expedición
    * EMBALB.TXT - Información de embalajes

**Importación de Pedidos**
    Configuración: ``connector_edicom.sale_order_import_edicom``

    Archivos procesados:

    * CABPED - Cabecera de pedido
    * LINPED - Líneas de pedido
    * OBSPED - Observaciones (pendiente de implementar)

Estas configuraciones definen el mapeo exacto entre campos de Odoo y posiciones en los archivos EDI.

Modelos Extendidos
==================

El módulo extiende los siguientes modelos de Odoo:

**res.partner**
    Añade campos: ``edicom_ean13``, ``eci_buyer_code``, ``edicom_export_invoice_path``

**account.move**
    Añade campos: ``edicom_partner_id``

    Métodos: ``action_export_edicom()``, exportación automática en ``action_post()``

**account.move.line**
    Añade campo: ``edicom_dept`` (departamento)

**sale.order**
    Añade campos relacionados con EDI: ``edicom_order_id``, ``edicom_node``, ``edicom_dept``,
    ``edicom_function``, ``edicom_special_cond``, ``edicom_emitter_id``, ``edicom_buyer_id``,
    ``edicom_original_order``

**stock.picking**
    Métodos: ``action_export_edicom()``

**stock.quant.package**
    Métodos: ``get_related_picking()`` - Identifica el albarán relacionado con un paquete

Dependencias
============

* ``account`` - Contabilidad
* ``account_invoice_production_lot`` - Lotes en facturas
* ``sale`` - Ventas
* ``stock`` - Inventario
* ``ftplib`` (Python) - Conexión FTP

Notas Técnicas
==============

* Los archivos EDI se generan con codificación Windows-1252
* Los caracteres especiales se normalizan usando unidecode
* El separador de campos es posicional (formato de ancho fijo)
* Los números se formatean con signo y decimales según especificación EDI
* Las fechas siguen el formato YYYYMMDD o YYYYMMDDHHMM

Contributors
------------

* Pablo Cortés <pablo.cortes@studio73.es>
* Ioan Galan <ioan@studio73.es>

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Studio73/studio73-private-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Maintainer
----------

.. image:: https://www.studio73.es/logo.png
    :alt: Consultoría Informática Studio 73 S.L.
    :target: https://www.studio73.es/

This module is maintained by Studio73.