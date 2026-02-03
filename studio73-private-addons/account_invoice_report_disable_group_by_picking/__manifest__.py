# Copyright 2021 Studio73 - Ioan Galan <ioan@studio73.es>
# Copyright 2022 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Account Invoice Report Disable Group By Picking",
    "summary": "Poder deshabilitar la impresión de facturas agrupada por albaranes",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "author": "Studio73",
    "category": "Accounting & Finance",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "depends": ["account_invoice_report_grouped_by_picking"],
    "data": [
        "views/account_move.xml",
        "views/report_invoice.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
}
