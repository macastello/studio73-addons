# Copyright 2024 Studio73 - Raúl Menéndez <raul@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import io

import PyPDF2

from odoo import api, fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    number_of_copies = fields.Integer(string="Number of Copies", default=1)

    @api.model
    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):  # pragma: no cover
        def merge_pdfs(_pdfs):
            mergeFile = PyPDF2.PdfFileMerger()
            for _pdf in _pdfs:
                mergeFile.append(io.BytesIO(_pdf), import_bookmarks=False)
            output = io.BytesIO()
            mergeFile.write(output)
            mergeFile.close()
            output.seek(0)
            return output.getvalue()

        res, _ = super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
        report_id = self._get_report(report_ref)
        if report_id.number_of_copies:
            res = merge_pdfs([res] * report_id.number_of_copies)
        return res, _
