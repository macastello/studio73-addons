# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Stock Barcode Usability",
    "summary": "Mejoras sobre interfaz código barras",
    "sequence": 14,
    "license": "LGPL-3",
    "author": "Studio73",
    "website": "https://github.com/Studio73/stock-addons",
    "category": "Barcode",
    "version": "17.0.1.8.1",
    "depends": ["stock_barcode_picking_batch"],
    "data": [
        "views/res_config_settings.xml",
        "views/stock_picking_type.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/stock_barcode_usability/static/src/**/*",
        ],
        "web.qunit_suite_tests": [
            "/stock_barcode_usability/static/tests/units/**/*",
        ],
    },
    "installable": True,
}
