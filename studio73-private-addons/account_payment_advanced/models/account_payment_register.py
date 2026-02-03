# Copyright 2021 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    advanced_payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode", string="Modo de pago", check_company=True
    )

    def _create_payment_vals_from_wizard(self, batch_result):
        vals = super()._create_payment_vals_from_wizard(batch_result)
        if self.advanced_payment_mode_id:
            vals.update({"payment_mode_id": self.advanced_payment_mode_id.id})
        return vals

    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
        key_values = batch_result["payment_values"]
        lines = batch_result["lines"]
        payment_entries = self.env["account.payment.entry"].search(
            [("move_line_id", "in", lines.ids)]
        )
        res = super()._get_wizard_values_from_batch(batch_result)
        if payment_entries:
            company = lines[0].company_id._accessible_branches()[:1]
            source_amount = abs(sum([p.amount for p in payment_entries]))
            vals = {"source_amount": source_amount}
            if key_values["currency_id"] == company.currency_id.id:
                vals.update({"source_amount_currency": source_amount})
            res.update(vals)
        return res
