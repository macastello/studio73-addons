# Copyright 2018-2019 Studio73 - Abraham Anes <abraham@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    date_maturity = fields.Date(string="Fecha vencimiento")

    def _prepare_move_line_default_vals(
        self, write_off_line_vals=None, force_balance=None
    ):
        res = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals, force_balance=force_balance
        )
        for payment in res:
            payment.update({"date_maturity": self.date_maturity})
        return res
