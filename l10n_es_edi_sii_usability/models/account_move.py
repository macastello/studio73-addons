# Copyright 2024 Studio73 - Óscar Seguí <oscar@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


import threading

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sii_cron_trigger_ids = fields.Many2many(
        "ir.cron.trigger",
        "account_move_ir_cron_trigger_rel",
        "account_move_id",
        "ir_cron_trigger_id",
        string="SII Cron Triggers ",
        help="Triggers para los envios al SII",
        copy=False,
    )
    sii_send_date = fields.Datetime(
        string="Fecha de envio al SII",
        copy=False,
    )
    sii_state = fields.Selection(
        string="Estado de envio SII",
        selection=[
            ("not_sent", "No registrada"),
            ("sent", "Enviada"),
            ("error", "Error de envio"),
            ("processing", "Procesando"),
            ("modified", "Modificado pendiente de enviar al SII"),
            ("cancel", "Cancelado en el SII"),
        ],
        default="not_sent",
        readonly=True,
        copy=False,
    )
    sii_error = fields.Html(
        string="Error de envio SII",
        readonly=True,
        copy=False,
    )
    sii_csv = fields.Html(
        string="SII CSV",
        readonly=True,
        copy=False,
    )
    sii_sent_header = fields.Text(string="Last header sent SII")
    sii_sent_response = fields.Text(string="Last response sent SII")
    sii_dua_invoice = fields.Boolean("SII DUA Invoice", compute="_compute_dua_invoice")

    @api.depends("company_id", "fiscal_position_id", "invoice_line_ids.tax_ids")
    def _compute_dua_invoice(self):
        tax_dua = self.env.ref(
            f"account.{self.env.company.id}_account_tax_template_p_dua0",
            raise_if_not_found=False,
        )
        if not tax_dua:
            tax_dua = self.env.ref(
                f"account.{self.env.company.id}_account_tax_template_p_dua_exempt",
                raise_if_not_found=False,
            )

        for invoice in self:
            invoice.sii_dua_invoice = invoice.invoice_line_ids.filtered(
                lambda x: any([tax == tax_dua for tax in x.tax_ids])
            )

    @api.model
    def process_sii_cron_triggers(self):
        invoice_ids = self.env["account.move"].search(
            [
                ("sii_send_date", "<=", fields.Datetime.now()),
                ("sii_send_date", "!=", False),
                ("sii_state", "!=", "sent"),
            ]
        )
        invoice_ids._post_invoice_to_sii()
        return True

    def _post(self, soft=True):
        return super(
            AccountMove, self.with_context(skip_account_edi_cron_trigger=True)
        )._post(soft=soft)

    def _post_invoice_to_sii(self):
        for move in self:
            try:
                edi_document_vals_list = []
                for edi_format in move.journal_id.edi_format_ids:
                    move_applicability = edi_format._get_move_applicability(move)
                    if move_applicability:
                        errors = edi_format._check_move_configuration(move)
                        if errors:
                            move.write({"sii_state": "error"})
                            break
                        existing_edi_document = move.edi_document_ids.filtered(
                            lambda x: x.edi_format_id == edi_format  # noqa: B023
                        )
                        if existing_edi_document:
                            existing_edi_document.sudo().write(
                                {
                                    "state": "to_send",
                                    "attachment_id": False,
                                }
                            )
                        else:
                            edi_document_vals_list.append(
                                {
                                    "edi_format_id": edi_format.id,
                                    "move_id": move.id,
                                    "state": "to_send",
                                }
                            )
                self.env["account.edi.document"].create(edi_document_vals_list)
                move.edi_document_ids._process_documents_no_web_services()
                move.write({"sii_state": "processing"})
                self.env.ref("account_edi.ir_cron_edi_network")._trigger()
                if move.state == "cancel":
                    move.write({"sii_state": "cancel"})

                if not getattr(threading.current_thread(), "testing", False):
                    self.env.cr.commit()
            except Exception as e:
                self.env.cr.rollback()
                move.write(
                    {
                        "sii_state": "error",
                        "sii_error": f"Error al enviar al SII: {e}",
                    }
                )
                continue
        return True

    def _compute_l10n_es_is_simplified(self):
        super()._compute_l10n_es_is_simplified()
        for move in self:
            if move.partner_id.l10n_es_is_simplified:
                move.l10n_es_is_simplified = True

    def button_draft(self):
        super().button_draft()
        self.sii_state = "modified"

    def action_process_edi_web_services(self, with_commit=False):
        super().action_process_edi_web_services(with_commit)
        if self.state == "cancel":
            self.sii_state = "cancel"

    @api.depends("move_type", "company_id", "invoice_line_ids.tax_ids")
    def _compute_l10n_es_edi_is_required(self):
        super()._compute_l10n_es_edi_is_required()
        for move in self:
            taxes = move.invoice_line_ids.tax_ids
            has_tax = any(t.l10n_es_type and t.l10n_es_type != "ignore" for t in taxes)
            if not has_tax:
                move.l10n_es_edi_is_required = False
