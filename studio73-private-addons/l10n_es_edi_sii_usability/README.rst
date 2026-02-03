.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

==========================
España - SII EDI Usability
==========================

- Mejorar el módulo del SII de Odoo para tener diferentes modos de envío, ya que por defecto las facturas se envían al confirmar:
    - `Automático`: Se envía en el momento de validar la factura
    - `A una hora fija`: Se envía a una hora fija
    - `Con retardo`: Se envía con un retardo de X horas

El funcionamiento esta planteado para que cuando este instalado en vez de generar el fichero EDI, se genere un trigger y se 
añada a la factura la fecha de envió, ambos tendrán la misma fecha y hora, cuando se ejecute el cron mediante el trigger se 
creara el fichero y se enviara, de todas las facturas que tengan la fecha de envió igual o anterior a la fecha actual. 

- Añadimos el campo `SII DUA Invoice` para diferenciarlas a la hora del envio al SII
para que la razon social de la contraprte sea la empresa que lo envia al SII.

- A la hora del envio se tiene encuenta tanto el pais como la provincia del cliente
de la factura para tener en cuasnta el campomotivo de exención que hay en el
impuesto

Configuration
=============

- Ir a Contablidad - Configuración - Ajustes - Spain Localization
    - Seleccionar uno de los metodos de envio y seleccionar la hora en caso de ser necesario

.. image:: /l10n_es_edi_sii_usability/static/description/configuracion_metodo_envio_sii.png
   :alt: Configuracion metodo de envio SII
   :align: center


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Studio73/studio73-private-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Authors
~~~~~~~

* Studio73

Contributors
~~~~~~~~~~~~

* Óscar Seguí <oscar@studio73.es>
* Arantxa Gandia <arantxa@studio73.es>

Maintainer
~~~~~~~~~~

.. image:: https://www.studio73.es/logo.png
   :alt: Consultoría Informática Studio 73 S.L.
   :target: https://www.studio73.es/

This module is maintained by Studio73.
