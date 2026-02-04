# Copyright 2024 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# Copyright 2024 Studio73 - Ioan Galan <ioan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "edicom.export.mixin"]

    edicom_partner_id = fields.Many2one(
        "res.partner",
        string="Cliente EDI",
        tracking=True,
        copy=False,
        check_company=True,
        ondelete="restrict",
        help="Si el cliente destino es diferente a la dirección de entrega "
        "de la factura, debes seleccionarlo aquí, de lo contrario, deja el "
        "campo vacío. Esto afectará al campo 'CLIENTE' "
        "del fichero generado, en el cual se exportará el código EDI del "
        "contacto seleccionado",
    )

    def action_export_edicom(self):
        export_config = self.env.ref("connector_edicom.edicom_export_invoice_data")
        self.export_to_edicom(
            self, export_config, export_path=self.partner_id.edicom_export_invoice_path
        )
        return True

    def action_post(self):
        res = super().action_post()
        for move in self:
            partner = move.partner_id
            partner_shipping = move.partner_shipping_id
            if (
                move.move_type == "out_invoice"
                and partner.edicom_ean13
                and partner_shipping.edicom_ean13
            ):
                move.action_export_edicom()
        return res
