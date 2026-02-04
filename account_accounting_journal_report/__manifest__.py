# Copyright 2018 Studio73 - Abraham Anes <abraham@studio73.es>
# Copyright 2020 Studio73 - Ethan Hildick - <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Account Accounting Journal Report",
    "summary": "Obtener diario de contabilidad en formato CSV",
    "version": "17.0.1.0.0",
    "author": "Studio73",
    "category": "Generic Modules/Accounting",
    "license": "LGPL-3",
    "website": "https://github.com/Studio73/studio73-private-addons",
    "depends": ["account_financial_report"],
    "data": [
        "security/ir.model.access.csv",
        "report/report_account_accounting_journal.xml",
        "report/report.xml",
        "wizard/account_accounting_journal_view.xml",
    ],
    "installable": True,
}
