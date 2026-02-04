# Copyright 2018-2019 Studio73 - Abraham Anes <abraham@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    account_payment_advanced_id = fields.Many2one(
        comodel_name="account.payment.advanced",
        string="Pago avanzado",
        ondelete="restrict",
    )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_payment_advanced(self):
        if not self.env.context.get("advanced_remove", False) and any(
            payment.account_payment_advanced_id for payment in self
        ):
            raise UserError(
                _("No puede borrar un pago relacionado con un pago avanzado")
            )

    def _prepare_move_line_default_vals(
        self, write_off_line_vals=None, force_balance=None
    ):
        vals_list = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals, force_balance=force_balance
        )
        if self.payment_mode_id:
            for vals in vals_list:
                vals.update({"payment_mode_id": self.payment_mode_id.id})
        account_payment_advanced_id = self.env.context.get(
            "account_payment_advanced_id", False
        )
        if account_payment_advanced_id and vals_list:
            apa = self.env["account.payment.advanced"].browse(
                account_payment_advanced_id
            )
            if apa.journal_id.is_defaulting_debtor_journal:
                debit = sum(line["debit"] for line in vals_list)
                credit = sum(line["credit"] for line in vals_list)
                debit_vals = vals_list[0].copy()
                debit_vals.update(
                    {
                        "account_id": apa.journal_id.credit_impairment_account_id.id,
                        "debit": debit,
                        "credit": 0,
                    }
                )
                credit_vals = vals_list[0].copy()
                credit_vals.update(
                    {
                        "account_id": apa.journal_id.debt_provision_account_id.id,
                        "debit": 0,
                        "credit": credit,
                    }
                )
                vals_list.append(debit_vals)
                vals_list.append(credit_vals)
        return vals_list
