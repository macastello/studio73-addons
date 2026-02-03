# Copyright 2024 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    restrict_location_by_putaway = fields.Boolean(
        string="Restringir movimientos según categoría de ubicación",
        help="Si está marcado, se restringirán el validado de movimientos a una "
        "ubicación si estos no cumplen las restricciones de la categoría de la misma",
        default=True,
    )
