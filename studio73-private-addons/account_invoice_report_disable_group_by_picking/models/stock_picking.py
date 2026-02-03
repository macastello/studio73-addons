# Copyright 2022 Studio73 - Ethan Hildick <ethan@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    hide_picking_in_report = fields.Boolean(
        "No mostrar albarán en la factura", copy=False, tracking=True
    )
