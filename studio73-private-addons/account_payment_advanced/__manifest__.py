# Copyright 2018-2019 Studio73 - Abraham Anes <abraham@studio73.es>
# Copyright 2024 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Account Payment Advanced",
    "summary": "Interfaz mejorada para la gestión de pagos",
    "version": "17.0.1.0.3",
    "license": "LGPL-3",
    "author": "Studio73",
    "category": "account",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "depends": ["account_payment_date_maturity", "account_payment_partner"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_rule.xml",
        "data/ir_sequence.xml",
        "views/account_journal_view.xml",
        "views/account_payment_view.xml",
        "views/report.xml",
        "views/account_payment_template.xml",
        "views/account_payment_advanced_report.xml",
    ],
    "installable": True,
}
