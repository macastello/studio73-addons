# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Barcode GS1",
    "summary": "Integrar nomenclatura GS1 en la PDA",
    "version": "17.0.1.0.1",
    "license": "LGPL-3",
    "category": "Barcodes",
    "sequence": 14,
    "author": "Studio73",
    "website": "https://github.com/Studio73/stock-addons",
    "depends": ["stock_barcode_product_expiry"],
    "assets": {
        "web.assets_backend": [
            "stock_barcode_gs1/static/src/**/*",
        ],
    },
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "external_dependencies": {"python": ["openupgradelib"]},
}
