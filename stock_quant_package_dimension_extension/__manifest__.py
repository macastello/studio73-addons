# Copyright 2021 Studio73 - Ferran Mora <ferran@studio73.es>
# Copyright 2022 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Quant Package Dimension Extension",
    "summary": "Modifica los cálculos de dimensiones de paquetes",
    "version": "17.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/Studio73/stock-addons",
    "author": "Studio73",
    "license": "LGPL-3",
    "depends": [
        "product_logistics_uom",
        "purchase",
        "stock_delivery",
        "stock_picking_volume",
        "stock_quant_package_dimension",
    ],
    "data": [
        "data/stock_package_type.xml",
        "security/ir.model.access.csv",
        "views/product_packaging_view.xml",
        "views/product_product_view.xml",
        "views/purchase_order_line_view.xml",
        "views/product.xml",
        "views/res_config_settings_view.xml",
        "views/stock_lot_view.xml",
        "views/stock_package_type_views.xml",
        "views/stock_picking_type_view.xml",
        "wizard/assign_packages.xml",
        "wizard/choose_delivery_package.xml",
    ],
    "installable": True,
}
