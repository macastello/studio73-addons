# Copyright 2020 Studio73 - Ethan Hildick - <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ReportAccountAccountingJournal(models.AbstractModel):
    _name = "report.account_accounting_journal_report.acc_accounting_journal"
    _description = "Informe de diario de contabilidad"

    def _get_report_values(self, docids, data=None):
        if data is None:
            data = {"data": []}
        return {
            "doc_ids": docids,
            "doc_model": "account.accounting_journal",
            "docs": data["data"],
            "company": self.env.company,
            "date_from": data["date_from"],
            "date_to": data["date_to"],
            "level": data["level"],
            "include_analytic_account": data["include_analytic_account"],
        }
