# Copyright 2018-2019 Studio73 - Abraham Anes <abraham@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from itertools import combinations

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class AccountPaymentAdvanced(models.Model):
    _name = "account.payment.advanced"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Pagos de clientes"
    _order = "state ASC, date DESC"

    def _get_default_writeoff_account(self):
        company = self.env.company
        template_code = self.env["account.chart.template"]._guess_chart_template(
            company.country_id
        )
        data = self.env["account.chart.template"]._get_chart_template_data(
            template_code
        )
        code_digits = int(data.pop("template_data").get("code_digits", "0"))
        acc_code = "659".ljust(code_digits, "0")
        account = self.env["account.account"].search([("code", "=", acc_code)], limit=1)
        return account.id if account else False

    def _compute_invoices_count(self):
        for payment in self:
            payment.invoices_count = len(payment.invoice_ids)

    name = fields.Char(
        string="Name", tracking=True, required=True, default="/", copy=False
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        required=True,
        tracking=True,
        check_company=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id,
    )
    date = fields.Date(
        string="Fecha", required=True, tracking=True, default=fields.Date.context_today
    )
    date_maturity = fields.Date(string="Fecha de vencimiento", tracking=True)
    communication = fields.Char(string="Ref. pago", tracking=True)
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Diario",
        required=True,
        tracking=True,
        check_company=True,
    )
    state = fields.Selection(
        string="Estado",
        selection=[
            ("draft", "Borrador"),
            ("posted", "Publicado"),
            ("cancel", "Cancelado"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        string="Asiento contable",
        readonly=True,
        ondelete="cascade",
        check_company=True,
    )
    account_payment_ids = fields.One2many(
        comodel_name="account.payment",
        inverse_name="account_payment_advanced_id",
        string="Pagos",
        check_company=True,
    )
    writeoff_amount = fields.Float(string="Importe de la diferencia")
    writeoff_comment = fields.Char(
        string="Comentario de la contrapartida", default="Contrapartida"
    )
    writeoff_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Cuenta de la diferencia",
        domain=[("deprecated", "=", False)],
        copy=False,
        default=_get_default_writeoff_account,
        check_company=True,
    )
    entry_invoice_ids = fields.One2many(
        comodel_name="account.payment.entry",
        inverse_name="payment_id",
        domain=[("entry_type", "=", "cr")],
        string="Facturas",
    )
    entry_refund_ids = fields.One2many(
        comodel_name="account.payment.entry",
        inverse_name="payment_id",
        domain=[("entry_type", "=", "dr")],
        string="Facturas rectificativas",
    )
    journal_id_type = fields.Selection(related="journal_id.type")
    payment_difference_handling = fields.Selection(
        [
            ("open", "Mantener abierto"),
            ("reconcile", "Marcar factura como totalmente pagada"),
        ],
        default="open",
        string="Diferencia en pago",
        copy=False,
    )
    amount = fields.Float(string="Importe", required=True, tracking=True, copy=False)
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode", string="Modo de pago", check_company=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Empresa",
        default=lambda self: self.env.company,
    )
    is_move_sent = fields.Boolean(
        readonly=True,
        copy=False,
        tracking=True,
        help="It indicates that the invoice/payment has been sent.",
    )
    partner_type = fields.Selection(
        [("customer", "Cliente"), ("supplier", "Proveedor")],
        default="customer",
        tracking=True,
        required=True,
    )
    payment_type = fields.Selection(
        [("outbound", "Enviar dinero"), ("inbound", "Recibir dinero")],
        string="Tipo de pago",
        default="inbound",
        required=True,
    )
    partner_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Banco",
        domain="[('partner_id', '=', partner_id)]",
        check_company=True,
    )
    invoice_ids = fields.Many2many(
        "account.move", string="Facturas", check_company=True
    )
    invoices_count = fields.Integer(
        string="Facturas", compute="_compute_invoices_count"
    )
    no_compute = fields.Boolean(string="No calcular facturas", default=False)
    group_payment = fields.Boolean(string="Agrupar pagos", default=True)
    concile_move_line = fields.Boolean(
        string="Permitir conciliar apuntes",
        help="Si esta opción está marcada se cargarán también apuntes que pertenezcan "
        "al cliente, que la cuenta sea la misma que la cuenta a cobrar del cliente y "
        "que no estén conciliados. Las facturas que ya se muestran seguirán "
        "mostrándose con normalidad.",
    )

    @api.onchange("entry_invoice_ids", "entry_refund_ids", "amount")
    def _onchange_entry_ids(self):
        total = self.amount
        for entry in self.entry_invoice_ids:
            total -= entry.amount
        for entry in self.entry_refund_ids:
            total += entry.amount
        self.writeoff_amount = round(total, 2)

    @api.onchange("partner_id", "concile_move_line")
    def _onchange_partner_id(self):
        self.amount = 0.00
        if self.payment_type == "inbound":
            self.entry_invoice_ids = self._get_entry_vals("out_invoice", "cr")
            self.entry_refund_ids = self._get_entry_vals("out_refund", "dr")

    def _get_invoices(self, inv_type, typee):
        domain = [
            ("commercial_partner_id", "=", self.partner_id.id),
            ("state", "=", "posted"),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("move_type", "=", inv_type),
        ]
        invoices = self.env["account.move"].search(domain, order="date ASC")
        entrys = self.env["account.payment.entry"]
        for invoice in invoices:
            entrys |= self.env["account.payment.entry"].new(
                {
                    "invoice_id": invoice,
                    "reconcile": False,
                    "amount": 0.0,
                    "amount_unreconciled": invoice.amount_residual,
                    "entry_type": typee,
                    "date_original": invoice.date,
                    "amount_original": invoice.amount_total,
                }
            )
        return entrys

    def _get_move_lines(self, typee):
        domain = [
            ("partner_id", "=", self.partner_id.id),
            ("account_id", "=", self.partner_id.property_account_receivable_id.id),
            ("move_id.move_type", "=", "entry"),
            ("reconciled", "=", False),
        ]
        if typee == "cr":
            domain += [("debit", ">", 0)]
        elif typee == "dr":
            domain += [("credit", ">", 0)]
        else:
            raise UserError(_("Error: Tipo {} no contemplado"))
        move_lines = self.env["account.move.line"].search(domain, order="date ASC")
        entrys = self.env["account.payment.entry"]
        for line in move_lines:
            entrys |= self.env["account.payment.entry"].new(
                {
                    "move_line_id": line.id,
                    "reconcile": False,
                    "amount": 0.0,
                    "amount_unreconciled": abs(line.amount_residual),
                    "entry_type": typee,
                    "date_original": line.date,
                    "amount_original": abs(line.balance),
                }
            )
        return entrys

    def _get_entry_vals(self, inv_type, typee):
        self.ensure_one()
        entrys = self._get_invoices(inv_type, typee)
        if self.concile_move_line:
            entrys |= self._get_move_lines(typee)
        return entrys

    @api.onchange("amount")
    def _onchange_amount(self):
        if self.no_compute:
            return {}
        remaining_amount = self.amount
        res_ids = []
        amounts_dict = {}
        entry_lines = self.entry_invoice_ids
        entry_lines += self.entry_refund_ids
        for line in self.entry_invoice_ids:
            amounts_dict[line.id] = 1 * line.amount_unreconciled
        for line in self.entry_refund_ids:
            amounts_dict[line.id] = -1 * line.amount_unreconciled
        for i, vals in amounts_dict.items():
            if vals == remaining_amount:
                res_ids.append(i)
        # Para conciliar lineas de pago completas
        # probamos las suma de hasta
        # 30 lineas de pago juntas
        for comb in range(1, 11):
            # De esta forma mantenemos el orden, si utilizamos
            # amounts_dict.keys() el orden por fecha se pierde.
            ids = [line.id for line in entry_lines]
            for cmb in combinations(ids, comb):
                if round(sum(amounts_dict[i] for i in cmb), 2) == round(
                    remaining_amount, 2
                ):
                    res_ids = list(cmb)
                    break
            if res_ids:
                break
        for entry in self.entry_invoice_ids:
            if entry.id in res_ids:
                entry.reconcile = True
                entry.amount = entry.amount_unreconciled
            else:
                entry.reconcile = False
                entry.amount = 0
        for entry in self.entry_refund_ids:
            if entry.id in res_ids:
                entry.reconcile = True
                entry.amount = entry.amount_unreconciled
            else:
                entry.reconcile = False
                entry.amount = 0

    @api.onchange("journal_id")
    def _onchange_journal(self):
        if self.journal_id.payment_mode_id:
            self.payment_mode_id = self.journal_id.payment_mode_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals.update(
                    {"name": self.env["ir.sequence"].next_by_code("payment_adv")}
                )
        return super().create(vals_list)

    def action_post(self):
        self.ensure_one()
        move_lines_to_pay = self.entry_invoice_ids._get_filtered_move_line()
        move_lines_to_reconcile = self.entry_refund_ids._get_filtered_move_line()
        if sum(mp.amount_residual for mp in move_lines_to_pay) < sum(
            mr.amount_residual for mr in move_lines_to_reconcile
        ):
            temp_invoices = move_lines_to_pay
            move_lines_to_pay = move_lines_to_reconcile
            move_lines_to_reconcile = temp_invoices
        for pay_line in move_lines_to_pay.sorted(
            lambda i: i.amount_residual, reverse=True
        ):
            for rec_line in move_lines_to_reconcile:
                if not pay_line.amount_residual:
                    break
                if rec_line.account_id != pay_line.account_id or rec_line.reconciled:
                    continue
                (rec_line + pay_line).reconcile()
        data = {
            "payment_date": self.date,
            "date_maturity": self.date_maturity,
            "journal_id": self.journal_id.id,
            "group_payment": self.group_payment,
            "company_id": self.company_id.id,
            "source_currency_id": self.currency_id.id,
            "amount": self.amount,
            "payment_difference": -self.writeoff_amount,
            "advanced_payment_mode_id": self.payment_mode_id.id,
            "line_ids": [Command.set(move_lines_to_pay.ids)],
        }
        if (
            self.writeoff_amount != 0
            and self.payment_difference_handling == "reconcile"
        ):
            data.update(
                {
                    "payment_difference_handling": self.payment_difference_handling,
                    "writeoff_account_id": self.writeoff_account_id.id,
                    "writeoff_label": self.writeoff_comment,
                }
            )
        register_payments = self.env["account.payment.register"].new(data)
        payments = register_payments.with_context(
            account_payment_advanced_id=self.id
        )._create_payments()
        move_ids = (move_lines_to_pay + move_lines_to_reconcile).move_id.ids
        lines_with_pay = payments.mapped("move_id.line_ids")
        if hasattr(self.env["account.move.line"], "origin_date_maturity"):
            date_due_list = []
            for line in self.entry_invoice_ids:
                if line.reconcile:
                    date_due_list.append(line.date_due)
            min_date = min(date_due_list) if date_due_list else None
            if min_date:
                lines_with_pay.write({"origin_date_maturity": min_date})
        lines_with_pay.write(
            {
                "date_maturity": self.date_maturity,
            }
        )
        self.write(
            {
                "state": "posted",
                "account_payment_ids": [Command.set(payments.ids)],
                "invoice_ids": [Command.set(move_ids)],
            }
        )
        return True

    def action_post_and_new(self):
        self.action_post()
        res = self.env["ir.actions.actions"]._for_xml_id(
            "account_payment_advanced.action_account_payments"
        )
        context = safe_eval(res["context"])
        context.update({"default_journal_id": self.journal_id.id})
        view = self.env.ref(
            "account_payment_advanced.customer_account_payment_advanced_form"
        )
        res.update({"context": context, "views": [(view.id, "form")]})
        return res

    def action_draft(self):
        if any(p.state != "cancel" for p in self):
            raise UserError(
                _("No puede pasar el pago a 'Borrador' si este no está 'Cancelado'")
            )
        self.write({"state": "draft"})

    def action_cancel(self):
        for payment in self.account_payment_ids:
            payment.action_draft()
            payment.action_cancel()
            payment.with_context(advanced_remove=True).unlink()
        self.write({"state": "cancel", "invoice_ids": [Command.clear()]})

    def button_open_invoices(self):
        self.ensure_one()
        action = {
            "name": _("Facturas pagadas"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "context": {"create": False},
        }
        if len(self.invoice_ids) == 1:
            action.update({"view_mode": "form", "res_id": self.invoice_ids.id})
        else:
            action.update(
                {
                    "view_mode": "list,form",
                    "domain": [("id", "in", self.invoice_ids.ids)],
                }
            )
        return action

    @api.ondelete(at_uninstall=False)
    def _unlink_except_posted_payment_advanced(self):
        if any(payment_advanced.state == "posted" for payment_advanced in self):
            raise UserError(_("No puede borrar un pago publicado"))
