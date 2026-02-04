# Copyright 2021 Abraham Anes <abraham@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    date_maturity = fields.Date(string="Fecha vencimiento")

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        if self.date_maturity:
            res.update({"date_maturity": self.date_maturity})
        return res
