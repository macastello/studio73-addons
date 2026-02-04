# Copyright 2023 Studio73 - Sergi Biosca <sergi.biosca@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Move Stock Valuation Layer Draft Button",
    "summary": "Permitir pasar a borrador facturas con valoraciones de stock",
    "version": "17.0.0.0.0",
    "author": "Studio73",
    "category": "Account",
    "license": "LGPL-3",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "depends": [
        "stock_account",
        "web_ir_actions_act_window_message",
    ],
    "data": ["views/account_move.xml"],
    "installable": True,
}
