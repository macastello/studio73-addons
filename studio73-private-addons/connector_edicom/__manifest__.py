# Copyright 2024 Studio73 - Pablo Cortés <david.lopez@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Connector EDI",
    "summary": "Importar/Exportar datos EDI",
    "author": "Studio73",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "category": "connector",
    "version": "17.0.3.0.2",
    "license": "LGPL-3",
    "depends": ["sale", "account", "account_invoice_production_lot"],
    "data": [
        "data/edicom_import_sale_order_data.xml",
        "data/edicom_export_invoice_data.xml",
        "security/ir.model.access.csv",
        "wizard/sale_order_import_edicom.xml",
        "views/account_move.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
        "views/edicom_import_configuration_line.xml",
        "views/edicom_export_configuration_line.xml",
    ],
    "external_dependencies": {"python": ["ftplib"]},
    "installable": True,
}
