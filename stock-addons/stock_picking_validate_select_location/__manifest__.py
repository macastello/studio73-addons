# Copyright 2022 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Validate Select Location",
    "summary": "Escoger ubicación destino al validar",
    "version": "17.0.1.0.0",
    "category": "Stock",
    "author": "Studio73",
    "website": "https://github.com/Studio73/stock-addons",
    "license": "LGPL-3",
    "depends": ["stock_picking_batch"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_type.xml",
        "wizard/stock_picking_select_location.xml",
    ],
    "installable": True,
}
