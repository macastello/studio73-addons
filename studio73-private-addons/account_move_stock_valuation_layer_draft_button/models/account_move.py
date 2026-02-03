# Copyright 2023 Studio73 - Sergi Biosca <sergi.biosca@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    show_stock_valuation_layer_message = fields.Boolean(
        compute="_compute_show_message_draft_button"
    )

    def _compute_show_message_draft_button(self):
        for move in self:
            if move.sudo().line_ids.stock_valuation_layer_ids and move.state != "draft":
                move.show_stock_valuation_layer_message = True
            else:
                move.show_stock_valuation_layer_message = False

    def button_draft_confirm(self):
        if self.show_stock_valuation_layer_message:
            return {
                "type": "ir.actions.act_window.message",
                "title": _("Confirm"),
                "message": _(
                    "Se eliminará la valoración de stock correspondiente a esta factura"
                    ", crea o confírmela de nuevo para crear la valoración correcta"
                ),
                "close_button_title": False,
                "buttons": [
                    {
                        "type": "method",
                        "name": ("Aceptar"),
                        "model": "account.move",
                        "method": "button_draft",
                        "args": [self.ids],
                        "kwargs": {},
                        "classes": "btn-primary",
                    },
                    {
                        "type": "method",
                        "name": ("Cancelar"),
                        "model": "account.move",
                        "method": "cancel_button_draft",
                        "args": [self.ids],
                        "kwargs": {},
                        "classes": "btn-secondary",
                    },
                ],
            }

    def cancel_button_draft(self):
        return {"type": "ir.actions.act_window_close"}

    def button_draft(self):
        self.sudo().line_ids.stock_valuation_layer_ids.unlink()
        return super().button_draft()
