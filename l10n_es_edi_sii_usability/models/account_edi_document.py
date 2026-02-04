# Copyright 2024 Studio73 - Óscar Seguí <oscar@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models

DEFAULT_BLOCKING_LEVEL = "error"


class AccountEdiDocument(models.Model):
    _inherit = "account.edi.document"

    @api.model
    def _process_job(self, job):
        res = super()._process_job(job)
        documents = job["documents"]
        for document in documents:
            if document.edi_format_id.code == "es_sii":
                move = document.move_id
                if document.error:
                    move.write({"sii_state": "error", "sii_error": document.error})
                else:
                    move.write({"sii_state": "sent", "sii_error": False})
        return res
