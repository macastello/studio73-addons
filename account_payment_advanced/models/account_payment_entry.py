# Copyright 2018-2019 Studio73 - Abraham Anes <abraham@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentEntry(models.Model):
    _name = "account.payment.entry"
    _description = "Account Payment Entry"
    _order = "date_original ASC, invoice_id DESC"

    @api.depends("invoice_id", "move_line_id")
    def _compute_name(self):
        for entry in self:
            if entry.move_line_id and not entry.invoice_id:
                name = entry.move_line_id.display_name
            else:
                name = entry.invoice_id.display_name
            entry.name = name

    payment_id = fields.Many2one(comodel_name="account.payment.advanced", string="Pago")
    name = fields.Char(string="Referencia", compute="_compute_name", store=True)
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Factura",
        domain="[('state', '=', 'posted'), ('payment_state', '!=', 'paid')]",
    )
    move_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Apunte",
        domain="[('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False)]",
    )
    description = fields.Char(string="-")
    date_original = fields.Date(
        string="Fecha", store=True, related="invoice_id.invoice_date"
    )
    date_due = fields.Date(
        string="Fecha vencimiento", related="invoice_id.invoice_date_due"
    )
    amount_original = fields.Monetary(string="Importe original")
    amount_unreconciled = fields.Monetary(string="Saldo inicial")
    reconcile = fields.Boolean(string="Conciliación completa")
    currency_id = fields.Many2one(
        comodel_name="res.currency", related="payment_id.currency_id"
    )
    amount = fields.Monetary(string="Asignación")
    entry_type = fields.Selection(
        selection=[("cr", "Crédito"), ("dr", "Débito")], string="Tipo"
    )
    state = fields.Selection(related="payment_id.state", store=True)
    unpaid_expense = fields.Boolean(string="Gastos devolución")
    payment_date = fields.Date(related="payment_id.date", store=True)

    @api.onchange("reconcile")
    def _onchange_reconcile(self):
        if self.reconcile:
            self.amount = self.amount_unreconciled
        else:
            self.amount = 0

    def _get_filtered_move_line(self):
        available_lines = self.env["account.move.line"]
        for entry in self:
            if entry.amount and entry.invoice_id:
                for line in entry.invoice_id.line_ids:
                    if line.move_id.state != "posted":
                        raise UserError(
                            _("Solo puede registrar pagos de facturas publicadas.")
                        )
                    if (
                        line.account_type
                        not in (
                            "asset_receivable",
                            "liability_payable",
                        )
                        or (
                            line.currency_id
                            and line.currency_id.is_zero(line.amount_residual_currency)
                        )
                        or line.company_currency_id.is_zero(line.amount_residual)
                    ):
                        continue
                    available_lines |= line
                    entry.write({"move_line_id": line.id})
            elif entry.amount and entry.move_line_id:
                available_lines |= entry.move_line_id
        return available_lines
