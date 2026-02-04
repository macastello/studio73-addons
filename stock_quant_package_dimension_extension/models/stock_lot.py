# Copyright 2021 Studio73 - Carlos Reyes <carlos@studio73.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    packaging_ids = fields.One2many(
        comodel_name="product.packaging",
        inverse_name="lot_id",
        string="Packagings",
    )
