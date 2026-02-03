# Copyright 2022 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    dest_location_update_on_validate = fields.Selection(
        string="Elegir ubicación destino al validar",
        help="Si este campo está marcado se permitirá escoger la ubicación destino"
        " del albarán al validar. Con la opción de elegir una vez solo se elige en la "
        "primera validación y se fuerza para el resto",
        copy=False,
        selection=[
            ("never", "No"),
            ("always", "Elegir siempre"),
            ("first", "Elegir una vez"),
        ],
        default="never",
        required=True,
    )
