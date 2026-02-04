# Copyright 2024 Studio73 - Óscar Seguí <oscar@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sii_send_mode = fields.Selection(related="company_id.sii_send_mode", readonly=False)
    sii_send_time = fields.Float(related="company_id.sii_send_time", readonly=False)
    sii_delay_time = fields.Float(related="company_id.sii_delay_time", readonly=False)
    l10n_es_edi_force_invoice_date = fields.Boolean(
        related="company_id.l10n_es_edi_force_invoice_date",
        readonly=False,
    )
