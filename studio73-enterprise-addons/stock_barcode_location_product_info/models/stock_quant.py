# Copyright 2024 Studio73 - Sergi Biosca <sergi.biosca@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    location_name_id = fields.Char(string="Ubicación", related="location_id.name")
