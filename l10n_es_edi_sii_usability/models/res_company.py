# Copyright 2024 Studio73 - Óscar Seguí <oscar@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    sii_send_mode = fields.Selection(
        string="Metodo de envio",
        selection=[
            ("auto", "Automatico"),
            ("fix_time", "A una hora fija"),
            ("delayed", "Con retardo"),
        ],
        default="auto",
    )
    sii_send_time = fields.Float(
        string="Hora de envio",
        default=0.0,
    )
    sii_delay_time = fields.Float(
        string="Tiempo de retardo",
        default=0.0,
    )
    l10n_es_edi_force_invoice_date = fields.Boolean(
        string="Enviar fecha factura para fecha de operación",
        help="Si marcamos la casilla, cuando una factura se envíe al SII, como fecha "
        "de operación del SII se enviará la fecha de factura. "
        "Por defecto Odoo manda la fecha de entrega",
    )

    @api.constrains("sii_send_time")
    def _check_sii_send_time(self):
        for record in self:
            if record.sii_send_mode and (
                record.sii_send_time < 0.0 or record.sii_send_time > 24.0
            ):
                raise UserError(_("La hora de envio debe estar entre 0:00 y 23:59"))

    @api.constrains("sii_delay_time")
    def _check_sii_delay_time(self):
        for record in self:
            if record.sii_send_mode == "delayed" and record.sii_delay_time < 0.0:
                raise UserError(
                    _(
                        "El tiempo de retardo debe ser mayor a 0:00 horas, "
                        "en caso de ser 0:00 horas, se recomienda usar el "
                        "envio automatico"
                    )
                )
