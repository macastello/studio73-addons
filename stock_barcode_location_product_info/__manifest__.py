# Copyright 2023 Studio73 - Carlos Reyes <carlos@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Barcode Location Product Info",
    "summary": "Información de producto y ubicación con código de barras",
    "version": "17.0.1.2.0",
    "category": "Manufacturing",
    "license": "LGPL-3",
    "sequence": 14,
    "author": "Studio73",
    "website": "https://github.com/Studio73/studio73-enterprise-addons",
    "depends": ["stock_barcode", "product_expiry"],
    "data": ["views/stock_quant_views.xml"],
    "assets": {
        "web.assets_backend": [
            "stock_barcode_location_product_info/static/src/js/stock_barcode_location_product.esm.js",
            "stock_barcode_location_product_info/static/src/xml/stock_barcode_location_product.xml",
        ],
    },
    "installable": True,
}
