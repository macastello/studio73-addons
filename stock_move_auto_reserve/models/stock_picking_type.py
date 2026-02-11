# Copyright 2023 Studio73 - Ferran Mora <ferran@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    allow_reserve_relocating = fields.Boolean(
        string="Permitir reubicar reserva",
        help="Si este campo está marcado, cuando se valide un movimiento de este tipo,"
        " si el stock que se mueve estaba reservado para algún otro movimiento, este"
        " se volverá a reservar a partir del movimiento hecho",
        copy=False,
    )
