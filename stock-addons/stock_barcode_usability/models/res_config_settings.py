# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_barcode_force_increment = fields.Boolean(
        string="Forzar sumar cantidad al escanear producto",
        help="Si se marca la casilla, en la interfaz de código de barras se "
        "sumará cantidad a la línea al escanear producto incluso si el producto de "
        "esta tiene seguimiento por lotes",
        related="company_id.stock_barcode_force_increment",
        readonly=False,
    )
