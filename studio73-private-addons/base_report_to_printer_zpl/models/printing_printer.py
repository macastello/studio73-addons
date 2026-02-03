# Copyright 2023 Studio73 - Guillermo Llinares - <guillermo@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class PrintingPrinter(models.Model):
    _inherit = "printing.printer"

    @staticmethod
    def _set_option_doc_format(report, value):
        if value == "qweb-text" and report.print_as_zpl or value == "raw":
            return {"raw": "True"}
        return {}
