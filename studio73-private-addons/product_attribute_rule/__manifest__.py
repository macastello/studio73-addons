# Copyright 2020 Studio73 - Pablo Fuentes <pablo@studio73.es>
# Copyright 2023 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Product Attribute Rule",
    "summary": "Reglas restrictivas para combinaciones de atributos",
    "version": "17.0.1.0.1",
    "license": "LGPL-3",
    "category": "Product",
    "sequence": 15,
    "author": "Studio73",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "depends": ["sale", "web_widget_x2many_2d_matrix"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
